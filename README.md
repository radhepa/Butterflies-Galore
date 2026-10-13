# Butterflies Galore

A Minecraft Bedrock Edition add-on that fills the world with **100 unique butterflies**, each with its own hand-designed wing pattern, size, flight rhythm and home biome. It's built in a vanilla style: pixel-art textures, simple models and survival-friendly mechanics.

![All 100 butterflies](docs/preview.png)

## Features

- **100 butterfly species.** Real-world favorites like the Monarch, Blue Morpho, Peacock, Zebra Longwing and Queen Alexandra's Birdwing, plus a handful of Minecraft-native species: the Cherry Blossom Wing, Sculk Wisp, Crimson Ember, Warped Wanderer, Ender Wing and more.
- **Natural spawning by biome.** Meadows, forests, jungles, deserts, badlands, swamps, beaches, snowy biomes, lush caves, the deep dark, the Nether and the End all have their own species. Rarity ranges from common to legendary.
- **Lifelike flight.** Butterflies flutter, glide and bob through the air. They visit flowers, flee when hurt and never take fall damage.
- **Catch & collect.** Use a **Butterfly Jar** on a butterfly to catch it. Each species has its own jar item with a matching icon. Use a filled jar on a block to release the butterfly again.
- **Bottle of Nectar.** Butterflies follow you while you hold it, and you can drink it too.
- **New flowers.** Butterfly Bush, Milkweed and Coneflower grow naturally in fitting biomes, attract butterflies and can be crafted into dye.
- **Chrysalis.** A decorative hanging block for your butterfly garden.
- Every butterfly has a spawn egg in the creative inventory.

See the full [Butterfly Field Guide](docs/species.md) for every species, where it lives and how rare it is.

## Recipes

| Item | Ingredients |
|---|---|
| Butterfly Jar ×3 | 5 Glass + 1 Planks (shaped: planks on top, glass cup below) |
| Bottle of Nectar | Glass Bottle + Sugar + Dandelion, Butterfly Bush or Milkweed |
| Butterfly Bush | Oak Sapling + 2 Purple Dye |
| Milkweed | Wheat Seeds + Pink Dye + White Dye |
| Coneflower | Wheat Seeds + Magenta Dye + Brown Dye |
| Chrysalis | String + Green Dye + Gold Nugget |
| Purple / Pink / Magenta Dye ×2 | Butterfly Bush / Milkweed / Coneflower |

## Installation

1. Download `dist/ButterfliesGalore.mcaddon`.
2. Open it. Minecraft imports both the behavior pack and the resource pack.
3. In your world settings, activate **Butterflies Galore Behavior Pack**. The resource pack is added automatically.

Requires Minecraft Bedrock **1.21.40** or newer.

## Project layout

```
ButterfliesGalore_BP/   behavior pack (entities, spawn rules, items, blocks, recipes, world features)
ButterfliesGalore_RP/   resource pack (models, animation, textures, language)
tools/generate.py       builds both packs, the preview sheet and the .mcaddon
docs/                   preview image and field guide
dist/                   ready-to-install .mcaddon
```

All packs, textures and docs are generated from the species table in `tools/generate.py`. To add or change a butterfly, edit its entry and run:

```
pip install pillow
python3 tools/generate.py
```
