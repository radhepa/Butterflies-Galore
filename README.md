# Butterflies Galore

A Minecraft Bedrock Edition add-on that fills the world with **100 unique butterflies**. Each one has its own vibrant, hand-designed wing pattern, wing shape, size, flight rhythm and home biome. Every species also has a complete life cycle, from egg to caterpillar to chrysalis to butterfly, and a **Butterfly Handbook** lets you record them all.

![All 100 butterflies](docs/preview.png)

## Features

- **100 butterfly species.** Real-world favorites like the Monarch, Blue Morpho, Peacock, Zebra Longwing and Queen Alexandra's Birdwing, plus Minecraft-native species: the Cherry Blossom Wing, Sculk Wisp, Crimson Ember, Warped Wanderer, Ender Wing and more.
- **Full life cycle for every species.**
  - **Eggs:** feed a butterfly a Bottle of Nectar and it lays a cluster of eggs on a leaf.
  - **Caterpillars:** they hatch, crawl and munch. Feed them leaves, grass or the new flowers to help them grow. Each species has its own caterpillar: banded Monarchs, green swallowtails with eyespots, spiky brush-foots, fleshy birdwings and more.
  - **Chrysalis:** a fully grown caterpillar hangs up as a chrysalis that sways and twitches before a new butterfly emerges.
  - Wild caterpillars also appear in each species' home biome.
- **Butterfly Handbook.** Every player gets one on first join. Walk up to any egg, caterpillar, chrysalis or butterfly to record it. Browse 8 chapters of entries with habitat, rarity, wingspan, caterpillar food and a fun fact, and complete all four life stages of each species.
- **Natural spawning by biome.** Meadows, forests, jungles, deserts, badlands, swamps, beaches, snowy biomes, lush caves, the deep dark, the Nether and the End all have their own species, from common to legendary.
- **Lifelike flight.** Butterflies flutter, glide and bob through the air. They visit flowers, flee when hurt and never take fall damage.
- **Catch & release.** Use a **Butterfly Jar** on a butterfly to catch it. Every species has its own jar. Use a filled jar on a block to release the butterfly.
- **New flowers.** Butterfly Bush, Milkweed and Coneflower grow naturally, attract butterflies, feed caterpillars and craft into dye.

![The life cycle](docs/lifecycle.png)

See the full [Butterfly Field Guide](docs/species.md) for every species, where it lives and how rare it is.

## Recipes

| Item | Ingredients |
|---|---|
| Butterfly Jar ×3 | 5 Glass + 1 Planks (shaped: planks on top, glass cup below) |
| Butterfly Handbook | Book + Butterfly Jar |
| Bottle of Nectar | Glass Bottle + Sugar + Dandelion, Butterfly Bush or Milkweed |
| Butterfly Bush | Oak Sapling + 2 Purple Dye |
| Milkweed | Wheat Seeds + Pink Dye + White Dye |
| Coneflower | Wheat Seeds + Magenta Dye + Brown Dye |
| Purple / Pink / Magenta Dye ×2 | Butterfly Bush / Milkweed / Coneflower |

## Installation

1. Download `dist/ButterfliesGalore.mcaddon`.
2. Open it. Minecraft imports both the behavior pack and the resource pack.
3. In your world settings, activate **Butterflies Galore Behavior Pack**. The resource pack is added automatically.

Requires Minecraft Bedrock **1.21.90** or newer.

## Project layout

```
ButterfliesGalore_BP/   behavior pack (mobs, spawn rules, items, blocks, recipes, world features, handbook script)
ButterfliesGalore_RP/   resource pack (models, animations, textures, language)
tools/generate.py       builds both packs, the preview images and the .mcaddon
tools/handbook.js       source of the Butterfly Handbook script
docs/                   preview images and field guide
dist/                   ready-to-install .mcaddon
```

All packs, textures and docs are generated from the species table in `tools/generate.py`. To add or change a butterfly, edit its entry and run:

```
pip install pillow
python3 tools/generate.py
```
