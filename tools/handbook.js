// Butterflies Galore gameplay script:
// - the Butterfly Handbook, which records every butterfly, egg, caterpillar and chrysalis a player gets close to
// - shiny butterflies, collection milestones, rank titles and chapter wings
// - wearable wings that glide and flap
// - Display Jars and Terrariums that hold a living butterfly
// - Field Notes, which point the way to undiscovered butterflies
import { world, system, ItemStack } from "@minecraft/server";
import { ActionFormData } from "@minecraft/server-ui";
import { SPECIES, CATEGORIES } from "./species.js";

const NS = "butterflies";
const JOURNAL = "butterflies:journal";
const SHINY_JOURNAL = "butterflies:shiny";
const REWARDS = "butterflies:rewards";
const GIFTED = "butterflies:handbook_given";
const HANDBOOK = "butterflies:handbook";
const JAR = "butterflies:butterfly_jar";
const NECTAR = "butterflies:nectar_bottle";
const FIELD_NOTES = "butterflies:field_notes";
const SHINY_CHARM = "butterflies:shiny_charm";
const DISPLAYED = "butterflies:displayed";
const SHINY_LORE = "§6* Shiny *";
const UNKNOWN_ICON = "textures/ui/butterflies/unknown";
const STAGES = ["Eggs", "Caterpillar", "Chrysalis", "Butterfly"];
const SUFFIXES = [["_egg", 0], ["_caterpillar", 1], ["_chrysalis", 2]];
const ADULT = 3;
const ALL_STAGES = 0b1111;
const SCAN_RADIUS = 6;
const PAGE_SIZE = 24;
const RARITY_COLOR = { Common: "§a", Uncommon: "§b", Rare: "§d", Legendary: "§6" };
const INDEX = new Map(SPECIES.map((s, i) => [s.id, i]));
const REALM_OF_DIMENSION = { "minecraft:overworld": "overworld", "minecraft:nether": "nether", "minecraft:the_end": "end" };

// Shiny odds: 1 in 256 in the wild, 1 in 64 when raised from a chrysalis, three times better with a Shiny Charm.
const SHINY_WILD = 1 / 256;
const SHINY_RAISED = 1 / 64;
const CHARM_BONUS = 3;
const CHARM_RANGE = 48;

const RANKS = [
  [0, "Beginner"], [10, "Butterfly Spotter"], [25, "Nature Explorer"], [50, "Field Naturalist"],
  [100, "Lepidopterist"], [250, "Butterfly Expert"], [500, "Butterfly Scholar"], [750, "Butterfly Legend"],
  [1000, "Butterfly Master"],
];
const MILESTONES = [
  { n: 10, label: "4 Butterfly Jars and 4 Bottles of Nectar", items: [[JAR, 4], [NECTAR, 4]] },
  { n: 25, label: "2 Field Notes and 16 Torchflower Seeds", items: [[FIELD_NOTES, 2], ["minecraft:torchflower_seeds", 16]] },
  { n: 50, label: "2 Display Jars and 2 Field Notes", items: [[`${NS}:display_jar`, 2], [FIELD_NOTES, 2]] },
  { n: 100, label: "2 Terrariums and a Shiny Charm", items: [[`${NS}:terrarium`, 2], [SHINY_CHARM, 1]] },
  { n: 250, label: "4 Terrariums and 8 Field Notes", items: [[`${NS}:terrarium`, 4], [FIELD_NOTES, 8]] },
  { n: 500, label: "Rainbow Wings", items: [[`${NS}:wings_rainbow`, 1]] },
  { n: 750, label: "16 Display Jars and 32 Bottles of Nectar", items: [[`${NS}:display_jar`, 16], [NECTAR, 32]] },
  { n: 1000, label: "Golden Wings", items: [[`${NS}:wings_golden`, 1]] },
];

// ---------------------------------------------------------------------------
// Saved progress
// ---------------------------------------------------------------------------

// The journal is one hex digit per species; each bit is a life stage.
function loadJournal(player) {
  const raw = player.getDynamicProperty(JOURNAL);
  const journal = new Array(SPECIES.length).fill(0);
  if (typeof raw === "string") {
    for (let i = 0; i < Math.min(raw.length, journal.length); i++) journal[i] = parseInt(raw[i], 16) || 0;
  }
  return journal;
}

function saveJournal(player, journal) {
  player.setDynamicProperty(JOURNAL, journal.map((n) => n.toString(16)).join(""));
}

function loadShiny(player) {
  const raw = player.getDynamicProperty(SHINY_JOURNAL);
  const shiny = new Array(SPECIES.length).fill(false);
  if (typeof raw === "string") for (let i = 0; i < Math.min(raw.length, shiny.length); i++) shiny[i] = raw[i] === "1";
  return shiny;
}

function saveShiny(player, shiny) {
  player.setDynamicProperty(SHINY_JOURNAL, shiny.map((b) => (b ? "1" : "0")).join(""));
}

function loadRewards(player) {
  const raw = player.getDynamicProperty(REWARDS);
  return new Set(typeof raw === "string" && raw ? raw.split(",") : []);
}

function saveRewards(player, rewards) {
  player.setDynamicProperty(REWARDS, [...rewards].join(","));
}

const adults = (journal) => journal.filter((n) => n & (1 << ADULT)).length;
const complete = (journal) => journal.filter((n) => (n & ALL_STAGES) === ALL_STAGES).length;
const stageCount = (bits) => [0, 1, 2, 3].filter((s) => bits & (1 << s)).length;
const rankOf = (count) => RANKS.filter(([n]) => count >= n).pop()[1];
const chapterSpecies = (cat) => SPECIES.filter((s) => s.category === cat.name);
const chapterFound = (journal, cat) => chapterSpecies(cat).filter((s) => journal[INDEX.get(s.id)] & (1 << ADULT)).length;
const wingsNeeded = (cat) => Math.ceil(chapterSpecies(cat).length / 2);

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

function isShiny(entity) {
  try {
    return entity.getComponent("minecraft:mark_variant")?.value === 1;
  } catch {
    return false;
  }
}

// ---------------------------------------------------------------------------
// Items
// ---------------------------------------------------------------------------

function giveItem(player, typeId, amount = 1, lore) {
  const stack = new ItemStack(typeId, amount);
  if (lore) stack.setLore(lore);
  const left = player.getComponent("minecraft:inventory")?.container?.addItem(stack);
  if (left) player.dimension.spawnItem(left, player.location);
}

function consumeHeld(player, replacement) {
  const container = player.getComponent("minecraft:inventory")?.container;
  if (!container) return;
  const slot = player.selectedSlotIndex;
  const held = container.getItem(slot);
  if (!held) return;
  if (held.amount > 1) {
    held.amount -= 1;
    container.setItem(slot, held);
    if (replacement) giveItem(player, replacement);
  } else {
    container.setItem(slot, replacement ? new ItemStack(replacement, 1) : undefined);
  }
}

const hasShinyLore = (stack) => !!stack?.getLore().some((l) => l.includes("Shiny"));

function hasItem(player, typeId) {
  const container = player.getComponent("minecraft:inventory")?.container;
  if (!container) return false;
  for (let i = 0; i < container.size; i++) if (container.getItem(i)?.typeId === typeId) return true;
  return false;
}

// ---------------------------------------------------------------------------
// Discoveries, milestones and wings
// ---------------------------------------------------------------------------

function celebrate(player, title, subtitle) {
  player.onScreenDisplay.setTitle(title, { subtitle, fadeInDuration: 10, stayDuration: 60, fadeOutDuration: 20 });
  player.playSound("random.levelup", { volume: 0.7 });
}

function checkRewards(player, journal, index) {
  const rewards = loadRewards(player);
  let changed = false;
  const count = adults(journal);
  for (const m of MILESTONES) {
    const key = `m${m.n}`;
    if (count < m.n || rewards.has(key)) continue;
    rewards.add(key);
    changed = true;
    for (const [id, amount] of m.items) giveItem(player, id, amount);
    celebrate(player, `§6${m.n} Butterflies!`, `§fNew rank: §e${rankOf(count)}`);
    player.sendMessage(`§6Milestone reached: §f${m.n} butterflies discovered! §7Reward: ${m.label}.`);
  }
  const cat = CATEGORIES.find((c) => c.name === SPECIES[index].category);
  const key = cat && `w:${cat.name}`;
  if (cat && !rewards.has(key) && chapterFound(journal, cat) >= wingsNeeded(cat)) {
    rewards.add(key);
    changed = true;
    giveItem(player, cat.wings);
    celebrate(player, "§dWings Unlocked!", `§f${cat.wingsName}`);
    player.sendMessage(
      `§dYou discovered half of ${cat.name} and earned the §f${cat.wingsName}§d! ` +
        "Wear them in your chest slot to glide, and jump in the air to flap."
    );
  }
  if (changed) saveRewards(player, rewards);
}

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
  if (stage === ADULT) checkRewards(player, journal, index);
  return true;
}

function recordShiny(player, index) {
  const shiny = loadShiny(player);
  if (shiny[index]) return;
  shiny[index] = true;
  saveShiny(player, shiny);
  const count = shiny.filter(Boolean).length;
  celebrate(player, "§d* SHINY! *", `§fYou found a shiny ${SPECIES[index].name}!`);
  player.sendMessage(`§dShiny ${SPECIES[index].name} added to your handbook! §7(${count} shiny found)`);
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
      if (!found) continue;
      if (record(player, journal, found.index, found.stage)) changed = true;
      if (found.stage === ADULT && isShiny(entity)) recordShiny(player, found.index);
    }
    if (changed) saveJournal(player, journal);
  }
}, 20);

world.afterEvents.playerSpawn.subscribe(({ player, initialSpawn }) => {
  if (!initialSpawn || player.getDynamicProperty(GIFTED)) return;
  player.setDynamicProperty(GIFTED, true);
  giveItem(player, HANDBOOK);
  player.sendMessage("§aYou received a §fButterfly Handbook§a! Get close to butterflies to record them.");
});

// ---------------------------------------------------------------------------
// Shiny butterflies
// ---------------------------------------------------------------------------

// Butterflies released from jars keep the shininess they were caught with.
const pendingReleases = [];
// Butterflies this script spawns itself, which skip the shiny roll.
const scripted = new Set();

function makeShiny(entity) {
  try {
    entity.triggerEvent(`${NS}:make_shiny`);
  } catch {}
}

world.afterEvents.entitySpawn.subscribe(({ entity, cause }) => {
  if (!entity.isValid || !entity.typeId.startsWith(NS + ":")) return;
  const found = parseType(entity.typeId);
  if (!found || found.stage !== ADULT) return;
  if (scripted.delete(entity.id)) return;
  if (cause === "Loaded") return;
  const now = system.currentTick;
  const loc = entity.location;
  const i = pendingReleases.findIndex(
    (p) => p.typeId === entity.typeId && now - p.tick < 40 &&
      Math.abs(p.loc.x - loc.x) < 4 && Math.abs(p.loc.y - loc.y) < 4 && Math.abs(p.loc.z - loc.z) < 4
  );
  if (i >= 0) {
    if (pendingReleases[i].shiny) makeShiny(entity);
    pendingReleases.splice(i, 1);
    return;
  }
  let chance = cause === "Transformed" ? SHINY_RAISED : SHINY_WILD;
  let players = [];
  try {
    players = entity.dimension.getPlayers({ location: loc, maxDistance: CHARM_RANGE });
  } catch {}
  if (players.some((p) => hasItem(p, SHINY_CHARM))) chance *= CHARM_BONUS;
  if (Math.random() >= chance) return;
  makeShiny(entity);
  for (const p of players) {
    if (Math.hypot(p.location.x - loc.x, p.location.z - loc.z) < 32) {
      p.onScreenDisplay.setActionBar("§dSomething is sparkling nearby...");
    }
  }
});

// Catching a shiny butterfly marks its jar so the shine is kept.
world.beforeEvents.playerInteractWithEntity.subscribe((ev) => {
  const { player, target, itemStack } = ev;
  if (itemStack?.typeId !== JAR || !target.typeId.startsWith(NS + ":")) return;
  const found = parseType(target.typeId);
  if (!found || found.stage !== ADULT || !isShiny(target)) return;
  const jarId = `${NS}:jar_${SPECIES[found.index].id}`;
  system.runTimeout(() => markShinyJar(player, jarId), 2);
});

function markShinyJar(player, jarId) {
  const container = player.getComponent("minecraft:inventory")?.container;
  if (!container) return;
  for (let i = 0; i < container.size; i++) {
    const stack = container.getItem(i);
    if (stack?.typeId !== jarId || hasShinyLore(stack)) continue;
    if (stack.amount > 1) {
      stack.amount -= 1;
      container.setItem(i, stack);
      giveItem(player, jarId, 1, [SHINY_LORE]);
    } else {
      stack.setLore([SHINY_LORE]);
      container.setItem(i, stack);
    }
    return;
  }
}

// ---------------------------------------------------------------------------
// Display Jars and Terrariums
// ---------------------------------------------------------------------------

const DISPLAY_BLOCKS = {
  [`${NS}:display_jar`]: { event: `${NS}:show_in_jar`, y: 0.35 },
  [`${NS}:terrarium`]: { event: `${NS}:show_in_terrarium`, y: 0.45 },
};

function displayCenter(block, y) {
  return { x: block.location.x + 0.5, y: block.location.y + y, z: block.location.z + 0.5 };
}

function occupant(dimension, center) {
  try {
    return dimension.getEntities({ location: center, maxDistance: 0.8, families: ["butterfly"], tags: [DISPLAYED] })[0];
  } catch {
    return undefined;
  }
}

world.beforeEvents.playerInteractWithBlock.subscribe((ev) => {
  if (!ev.isFirstEvent) return;
  const { player, block, itemStack } = ev;
  const display = DISPLAY_BLOCKS[block.typeId];
  const held = itemStack?.typeId ?? "";
  const isFilledJar = held.startsWith(`${NS}:jar_`);
  if (!display) {
    if (isFilledJar) {
      const id = held.slice(`${NS}:jar_`.length);
      pendingReleases.push({ typeId: `${NS}:${id}`, shiny: hasShinyLore(itemStack), loc: block.location, tick: system.currentTick });
      if (pendingReleases.length > 32) pendingReleases.shift();
    }
    return;
  }
  const center = displayCenter(block, display.y);
  const current = occupant(block.dimension, center);
  if (isFilledJar && !current) {
    ev.cancel = true;
    const id = held.slice(`${NS}:jar_`.length);
    const shiny = hasShinyLore(itemStack);
    system.run(() => {
      const bug = block.dimension.spawnEntity(`${NS}:${id}`, center);
      scripted.add(bug.id);
      bug.addTag(DISPLAYED);
      bug.triggerEvent(display.event);
      if (shiny) makeShiny(bug);
      consumeHeld(player, JAR);
      player.playSound("random.pop", { pitch: 1.4 });
    });
  } else if (!itemStack && current) {
    ev.cancel = true;
    system.run(() => {
      const found = parseType(current.typeId);
      if (found) giveItem(player, `${NS}:jar_${SPECIES[found.index].id}`, 1, isShiny(current) ? [SHINY_LORE] : undefined);
      current.remove();
      player.playSound("random.pop", { pitch: 0.9 });
    });
  }
});

// Breaking a jar or terrarium sets its butterfly free.
world.afterEvents.playerBreakBlock.subscribe(({ block, brokenBlockPermutation, dimension }) => {
  const display = DISPLAY_BLOCKS[brokenBlockPermutation.type.id];
  if (!display) return;
  const bug = occupant(dimension, displayCenter(block, display.y));
  if (!bug) return;
  bug.removeTag(DISPLAYED);
  bug.triggerEvent(`${NS}:release`);
});

// ---------------------------------------------------------------------------
// Wearable wings: glide while falling, flap by jumping in mid-air
// ---------------------------------------------------------------------------

const wingState = new Map();

system.runInterval(() => {
  for (const player of world.getAllPlayers()) {
    let chest;
    try {
      chest = player.getComponent("minecraft:equippable")?.getEquipment("Chest");
    } catch {
      continue;
    }
    if (!chest?.typeId.startsWith(`${NS}:wings_`)) {
      wingState.delete(player.id);
      continue;
    }
    const special = chest.typeId.endsWith("_rainbow") || chest.typeId.endsWith("_golden");
    const st = wingState.get(player.id) ?? { flaps: 0, jumping: false };
    const jumping = player.isJumping;
    if (player.isOnGround || player.isInWater || player.isFlying) {
      st.flaps = 0;
    } else {
      if (!player.isSneaking && player.getVelocity().y < -0.12) {
        player.addEffect("slow_falling", 4, { showParticles: false });
      }
      if (jumping && !st.jumping && st.flaps < (special ? 5 : 3)) {
        st.flaps += 1;
        const dir = player.getViewDirection();
        try {
          player.applyKnockback({ x: dir.x * 0.5, z: dir.z * 0.5 }, 0.6);
        } catch {}
        player.playSound("mob.parrot.fly", { pitch: 1.2 });
        if (special) {
          try {
            player.dimension.spawnParticle("minecraft:villager_happy", player.location);
          } catch {}
        }
      }
    }
    st.jumping = jumping;
    wingState.set(player.id, st);
  }
}, 1);

// ---------------------------------------------------------------------------
// Field Notes
// ---------------------------------------------------------------------------

function readFieldNotes(player) {
  const journal = loadJournal(player);
  const realm = REALM_OF_DIMENSION[player.dimension.id] ?? "overworld";
  const missing = SPECIES.filter((s) => !(journal[INDEX.get(s.id)] & (1 << ADULT)));
  if (missing.length === 0) {
    player.sendMessage("§aYou have already discovered every butterfly. There is nothing left to note down!");
    return;
  }
  const here = missing.filter((s) => s.realm === realm);
  const pool = here.length ? here : missing;
  const sp = pool[Math.floor(Math.random() * pool.length)];
  consumeHeld(player);
  player.playSound("item.book.page_turn");
  player.sendMessage(
    `§eField Notes: §fA ${RARITY_COLOR[sp.rarity] ?? ""}${sp.rarity}§f butterfly, the §l${sp.name}§r§f, ` +
      `has been seen in: §a${sp.habitat}§f.`
  );
}

world.afterEvents.itemUse.subscribe(({ source, itemStack }) => {
  if (itemStack?.typeId === HANDBOOK) system.run(() => openHome(source));
  else if (itemStack?.typeId === FIELD_NOTES) system.run(() => readFieldNotes(source));
});

// ---------------------------------------------------------------------------
// Handbook screens
// ---------------------------------------------------------------------------

function openHome(player) {
  const journal = loadJournal(player);
  const shinyCount = loadShiny(player).filter(Boolean).length;
  const count = adults(journal);
  const form = new ActionFormData()
    .title("Butterfly Handbook")
    .body(
      `§7Rank: §e${rankOf(count)}\n` +
        `§7Butterflies discovered: §f${count}/${SPECIES.length}\n` +
        `§7Life cycles completed: §f${complete(journal)}/${SPECIES.length}\n` +
        `§7Shiny butterflies found: §d${shinyCount}\n\n` +
        "§8Get close to butterflies, eggs, caterpillars and chrysalises to record them."
    );
  for (const cat of CATEGORIES) {
    form.button(`${cat.name}\n§8${chapterFound(journal, cat)}/${chapterSpecies(cat).length} discovered`, cat.icon);
  }
  form.button("Rewards & Wings", "textures/items/wings/wings_rainbow");
  form.button("Life Cycle Guide", "textures/items/nectar_bottle");
  form.button("Tips & Secrets", "textures/items/shiny_charm");
  form.show(player).then((res) => {
    if (res.canceled || res.selection === undefined) return;
    const extra = res.selection - CATEGORIES.length;
    if (extra < 0) openCategory(player, CATEGORIES[res.selection], 0);
    else if (extra === 0) openRewards(player);
    else if (extra === 1) openGuide(player);
    else openTips(player);
  });
}

function openCategory(player, cat, page) {
  const journal = loadJournal(player);
  const shiny = loadShiny(player);
  const all = chapterSpecies(cat);
  const pages = Math.max(1, Math.ceil(all.length / PAGE_SIZE));
  const list = all.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);
  const title = pages > 1 ? `${cat.name} (${page + 1}/${pages})` : cat.name;
  const form = new ActionFormData().title(title).body("§7Select an entry to read about it.");
  for (const s of list) {
    const i = INDEX.get(s.id);
    const bits = journal[i];
    if (bits === 0) {
      form.button(`§8???\n§8Not yet discovered`, UNKNOWN_ICON);
    } else {
      const star = shiny[i] ? " §d*" : "";
      const name = bits & (1 << ADULT) ? s.name : `${s.name} §8(young)`;
      form.button(`${name}${star}\n§8${stageCount(bits)}/4 life stages`, bits & (1 << ADULT) ? s.icon : UNKNOWN_ICON);
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
  const i = INDEX.get(s.id);
  const bits = loadJournal(player)[i];
  const shiny = loadShiny(player)[i];
  const rarity = `${RARITY_COLOR[s.rarity] ?? "§f"}${s.rarity}`;
  let body;
  if (bits === 0) {
    body = "§8You have not found this butterfly yet.\n\n" + `§7Hint: look in §f${s.habitat}§7.\n§7Rarity: ${rarity}`;
  } else {
    const stages = STAGES.map((label, n) => (bits & (1 << n) ? `§a[x] ${label}` : `§8[ ] ${label}`)).join("\n");
    body =
      `§l${s.name}§r\n${rarity}§r §7- ${s.category}\n\n` +
      `§7Habitat: §f${s.habitat}\n` +
      `§7Wingspan: §f${s.wingspan}\n` +
      `§7Caterpillars eat: §f${s.food}\n\n` +
      `§f${s.info}\n\n` +
      `§lLife cycle§r\n${stages}\n\n` +
      (shiny ? "§d* Shiny form found! *" : "§8Shiny form: not found yet");
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

function openRewards(player) {
  const journal = loadJournal(player);
  const rewards = loadRewards(player);
  const count = adults(journal);
  const milestones = MILESTONES.map((m) =>
    rewards.has(`m${m.n}`) ? `§a[x] ${m.n}: ${m.label}` : `§7[ ] ${m.n}: ${m.label} §8(${count}/${m.n})`
  ).join("\n");
  const wings = CATEGORIES.map((c) => {
    const found = chapterFound(journal, c);
    const need = wingsNeeded(c);
    return rewards.has(`w:${c.name}`) ? `§a[x] ${c.wingsName}` : `§7[ ] ${c.wingsName} §8- ${c.name} ${found}/${need}`;
  }).join("\n");
  const ranks = RANKS.map(([n, name]) => (count >= n ? `§e${name}` : `§8${name} (${n})`)).join("§7, ");
  new ActionFormData()
    .title("Rewards & Wings")
    .body(
      `§lRank§r\n${ranks}\n\n` +
        `§lMilestones§r\n${milestones}\n\n` +
        "§lChapter Wings§r\n§7Discover half the butterflies in a chapter to earn its wings.\n" +
        `${wings}\n\n` +
        "§7Wings go in your chest slot. Fall to glide, and jump in mid-air to flap " +
        "(3 flaps, or 5 with Rainbow or Golden Wings). Sneak to drop faster."
    )
    .button("< Back")
    .show(player)
    .then((res) => {
      if (!res.canceled) openHome(player);
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
        "§l4. Butterfly§r\n§7A brand new butterfly emerges and flies off to find flowers. " +
        "Butterflies you raise yourself are four times more likely to be §dshiny§7!\n\n" +
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

function openTips(player) {
  new ActionFormData()
    .title("Tips & Secrets")
    .body(
      "§l§dShiny Butterflies§r\n§7About 1 in 256 butterflies is a rare shiny colour form that sparkles. " +
        "Raised butterflies are shiny 1 in 64 times, and carrying a §fShiny Charm§7 triples your luck. " +
        "Shiny butterflies stay shiny when you catch them in a jar.\n" +
        "§8Shiny Charm: 3 Gold Ingots, a Diamond and a Bottle of Nectar.\n\n" +
        "§l§6Display Jars & Terrariums§r\n§7Use a filled Butterfly Jar on a §fDisplay Jar§7 or §fTerrarium§7 to " +
        "show off your butterfly. Use it with an empty hand to take the butterfly back. Display Jars glow like lanterns!\n" +
        "§8Display Jar: Butterfly Jar + Glowstone Dust. Terrarium: glass, Butterfly Bush, moss and planks.\n\n" +
        "§l§eField Notes§r\n§7Read Field Notes to learn where an undiscovered butterfly lives. " +
        "Craft them from paper, an ink sac and a Bottle of Nectar.\n\n" +
        "§l§bWings§r\n§7Earn wings by discovering half of a chapter, and special wings at 500 and 1000 " +
        "discoveries. See Rewards & Wings."
    )
    .button("< Back")
    .show(player)
    .then((res) => {
      if (!res.canceled) openHome(player);
    });
}
