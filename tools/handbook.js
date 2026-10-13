// Butterfly Handbook: records every butterfly, egg, caterpillar and chrysalis a
// player gets close to, and shows the collection in a browsable book.
import { world, system, ItemStack } from "@minecraft/server";
import { ActionFormData } from "@minecraft/server-ui";
import { SPECIES, CATEGORIES } from "./species.js";

const NS = "butterflies";
const JOURNAL = "butterflies:journal";
const GIFTED = "butterflies:handbook_given";
const HANDBOOK = "butterflies:handbook";
const UNKNOWN_ICON = "textures/ui/butterflies/unknown";
const STAGES = ["Eggs", "Caterpillar", "Chrysalis", "Butterfly"];
const SUFFIXES = [["_egg", 0], ["_caterpillar", 1], ["_chrysalis", 2]];
const ADULT = 3;
const ALL_STAGES = 0b1111;
const SCAN_RADIUS = 6;
const PAGE_SIZE = 24;
const RARITY_COLOR = { Common: "§a", Uncommon: "§b", Rare: "§d", Legendary: "§6" };
const INDEX = new Map(SPECIES.map((s, i) => [s.id, i]));

// The journal is one hex digit per species; each bit is a life stage.
function loadJournal(player) {
  const raw = player.getDynamicProperty(JOURNAL);
  const journal = new Array(SPECIES.length).fill(0);
  if (typeof raw === "string") {
    for (let i = 0; i < Math.min(raw.length, journal.length); i++) {
      journal[i] = parseInt(raw[i], 16) || 0;
    }
  }
  return journal;
}

function saveJournal(player, journal) {
  player.setDynamicProperty(JOURNAL, journal.map((n) => n.toString(16)).join(""));
}

function parseType(typeId) {
  if (!typeId.startsWith(NS + ":")) return undefined;
  let id = typeId.slice(NS.length + 1);
  let stage = ADULT;
  for (const [suffix, s] of SUFFIXES) {
    if (id.endsWith(suffix)) {
      id = id.slice(0, -suffix.length);
      stage = s;
      break;
    }
  }
  const index = INDEX.get(id);
  return index === undefined ? undefined : { index, stage };
}

const adults = (journal) => journal.filter((n) => n & (1 << ADULT)).length;
const complete = (journal) => journal.filter((n) => (n & ALL_STAGES) === ALL_STAGES).length;
const stageCount = (bits) => [0, 1, 2, 3].filter((s) => bits & (1 << s)).length;

function record(player, journal, index, stage) {
  const bit = 1 << stage;
  if (journal[index] & bit) return false;
  journal[index] |= bit;
  const sp = SPECIES[index];
  const label = stage === ADULT ? sp.name : `${sp.name} ${STAGES[stage]}`;
  player.onScreenDisplay.setActionBar(
    `§eNew handbook entry: §f${label} §7(${adults(journal)}/${SPECIES.length} butterflies)`
  );
  player.playSound("random.orb", { pitch: 1.3, volume: 0.6 });
  if ((journal[index] & ALL_STAGES) === ALL_STAGES) {
    player.sendMessage(`§6Life cycle complete: §f${sp.name}§6! All four stages are in your handbook.`);
    player.playSound("random.levelup", { volume: 0.5 });
  }
  return true;
}

system.runInterval(() => {
  for (const player of world.getAllPlayers()) {
    let nearby;
    try {
      nearby = player.dimension.getEntities({
        location: player.location,
        maxDistance: SCAN_RADIUS,
        families: ["butterfly_lifecycle"],
      });
    } catch {
      continue;
    }
    if (nearby.length === 0) continue;
    const journal = loadJournal(player);
    let changed = false;
    for (const entity of nearby) {
      const found = parseType(entity.typeId);
      if (found && record(player, journal, found.index, found.stage)) changed = true;
    }
    if (changed) saveJournal(player, journal);
  }
}, 20);

world.afterEvents.playerSpawn.subscribe(({ player, initialSpawn }) => {
  if (!initialSpawn || player.getDynamicProperty(GIFTED)) return;
  player.setDynamicProperty(GIFTED, true);
  player.getComponent("minecraft:inventory")?.container?.addItem(new ItemStack(HANDBOOK, 1));
  player.sendMessage("§aYou received a §fButterfly Handbook§a! Get close to butterflies to record them.");
});

world.afterEvents.itemUse.subscribe(({ source, itemStack }) => {
  if (itemStack?.typeId !== HANDBOOK) return;
  system.run(() => openHome(source));
});

function openHome(player) {
  const journal = loadJournal(player);
  const form = new ActionFormData()
    .title("Butterfly Handbook")
    .body(
      `§7Butterflies discovered: §f${adults(journal)}/${SPECIES.length}\n` +
        `§7Life cycles completed: §f${complete(journal)}/${SPECIES.length}\n\n` +
        "§8Get close to butterflies, eggs, caterpillars and chrysalises to record them."
    );
  for (const cat of CATEGORIES) {
    const list = SPECIES.filter((s) => s.category === cat.name);
    const found = list.filter((s) => journal[INDEX.get(s.id)] & (1 << ADULT)).length;
    form.button(`${cat.name}\n§8${found}/${list.length} discovered`, cat.icon);
  }
  form.button("Life Cycle Guide", "textures/items/nectar_bottle");
  form.show(player).then((res) => {
    if (res.canceled || res.selection === undefined) return;
    if (res.selection < CATEGORIES.length) openCategory(player, CATEGORIES[res.selection], 0);
    else openGuide(player);
  });
}

function openCategory(player, cat, page) {
  const journal = loadJournal(player);
  const all = SPECIES.filter((s) => s.category === cat.name);
  const pages = Math.max(1, Math.ceil(all.length / PAGE_SIZE));
  const list = all.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);
  const title = pages > 1 ? `${cat.name} (${page + 1}/${pages})` : cat.name;
  const form = new ActionFormData().title(title).body("§7Select an entry to read about it.");
  for (const s of list) {
    const bits = journal[INDEX.get(s.id)];
    if (bits === 0) {
      form.button(`§8???\n§8Not yet discovered`, UNKNOWN_ICON);
    } else {
      const name = bits & (1 << ADULT) ? s.name : `${s.name} §8(young)`;
      form.button(`${name}\n§8${stageCount(bits)}/4 life stages`, bits & (1 << ADULT) ? s.icon : UNKNOWN_ICON);
    }
  }
  const nav = [];
  if (page + 1 < pages) {
    form.button("Next page >");
    nav.push(() => openCategory(player, cat, page + 1));
  }
  if (page > 0) {
    form.button("< Previous page");
    nav.push(() => openCategory(player, cat, page - 1));
  }
  form.button("< Back");
  nav.push(() => openHome(player));
  form.show(player).then((res) => {
    if (res.canceled || res.selection === undefined) return;
    if (res.selection < list.length) openEntry(player, cat, page, list[res.selection]);
    else nav[res.selection - list.length]();
  });
}

function openEntry(player, cat, page, s) {
  const bits = loadJournal(player)[INDEX.get(s.id)];
  const rarity = `${RARITY_COLOR[s.rarity] ?? "§f"}${s.rarity}`;
  let body;
  if (bits === 0) {
    body =
      "§8You have not found this butterfly yet.\n\n" +
      `§7Hint: look in §f${s.habitat}§7.\n§7Rarity: ${rarity}`;
  } else {
    const stages = STAGES.map((label, i) => (bits & (1 << i) ? `§a[x] ${label}` : `§8[ ] ${label}`)).join("\n");
    body =
      `§l${s.name}§r\n${rarity}§r §7- ${s.category}\n\n` +
      `§7Habitat: §f${s.habitat}\n` +
      `§7Wingspan: §f${s.wingspan}\n` +
      `§7Caterpillars eat: §f${s.food}\n\n` +
      `§f${s.info}\n\n` +
      `§lLife cycle§r\n${stages}`;
  }
  new ActionFormData()
    .title(bits === 0 ? "???" : s.name)
    .body(body)
    .button("< Back")
    .show(player)
    .then((res) => {
      if (!res.canceled) openCategory(player, cat, page);
    });
}

function openGuide(player) {
  new ActionFormData()
    .title("Life Cycle Guide")
    .body(
      "§l1. Eggs§r\n§7Give a butterfly a §fBottle of Nectar§7 and it will lay a cluster of eggs. " +
        "Eggs hatch after about five minutes.\n\n" +
        "§l2. Caterpillar§r\n§7Caterpillars take a long time to grow up on their own (about 40 minutes). " +
        "Feed them §fseeds§7 to speed things up a lot: wheat, melon, pumpkin, beetroot and torchflower seeds " +
        "and pitcher pods all work. Leaves, grass and flowers help a little too. Nether caterpillars also " +
        "eat fungus and Nether Wart, and End caterpillars eat Chorus Fruit. Wild caterpillars can be found " +
        "in each species' home biome.\n\n" +
        "§l3. Chrysalis§r\n§7A full-grown caterpillar hangs up as a chrysalis. Inside, it changes completely " +
        "over about ten minutes. Keep it safe!\n\n" +
        "§l4. Butterfly§r\n§7A brand new butterfly emerges and flies off to find flowers.\n\n" +
        "§lTips§r\n§7- Hold a Bottle of Nectar to make butterflies follow you.\n" +
        "§7- Use a §fButterfly Jar§7 on a butterfly to catch it, and on a block to release it.\n" +
        "§7- Plant Butterfly Bush, Milkweed and Coneflowers to attract butterflies.\n" +
        "§7- Record all four stages of a species to complete its life cycle."
    )
    .button("< Back")
    .show(player)
    .then((res) => {
      if (!res.canceled) openHome(player);
    });
}
