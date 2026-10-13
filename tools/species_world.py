"""The third wave: 500 more Overworld butterflies (450 real species, 50 inspired by Minecraft).

Same format as species_more.py:  Name | wing shape | habitats | pattern | colours | rarity
"""

TABLE = """
# Meadows & Fields
Australian Painted Lady|classic|plains meadow|edge|E8862A 1E1A16 F4F0EA|c
Kamehameha Lady|classic|flower_forest meadow|band|E8642A 1E1A16 F4F0EA E8642A|r
Indian Red Admiral|classic|mountains meadow|band|1E1A16 0E0A08 E8642A F4F0EA|u
Yellow Admiral|classic|plains meadow|band|1E1A16 0E0A08 F2D84A F4F0EA|u
Indian Tortoiseshell|scalloped|mountains meadow|edge|E8762A 1E1A16 4A7AD8|u
Large Wall Brown|classic|mountains meadow|eyes|C89A5A 6A4A2A 1E1A16 FFFFFF|c
Chestnut Heath|rounded|meadow|ocelli|C87A3A 6A4A2A F2D080 1E1A16|u
Pearly Heath|rounded|meadow forest|ocelli|D8A050 8A6A3A F4F0EA 1E1A16|c
Dusky Meadow Brown|classic|meadow mountains|eyes|7A5A40 4A3A28 E8A04A 1E1A16|c
Oriental Meadow Brown|classic|plains meadow|patch|6A4A30 3A2A1A E8A04A|u
Great Banded Grayling|classic|meadow forest|band|3A2A20 1E1A16 F4F0DA|u
Hermit|classic|desert mesa|ocelli|8A7A6A 4A3A2E F4F0DA 1E1A16|r
Rock Grayling|classic|mountains mesa|eyes|8A7060 4A3A2E E8B070 1E1A16|u
Dryad|classic|meadow forest|ocelli|5A4030 2A1E14 4A6AD8 1E1A16|u
Great Sooty Satyr|classic|mountains meadow|eyes|2A2420 1A1612 4A6AD8 1E1A16|u
Black Satyr|classic|mountains|spotted|2A2420 1A1612 F4F0EA|r
Knapweed Fritillary|rounded|meadow|checker|E88A2A 2A1A0E F2D8A0|u
Spotted Fritillary|rounded|meadow mountains|spotted|E8862A 2A1A0E 1E1A16|u
Weaver's Fritillary|classic|meadow forest|checker|E8902A 3A2210 E8C8D0|u
Niobe Fritillary|classic|meadow mountains|checker|E8962E 2A1A0E F4F0EA|u
Meadow Fritillary|rounded|meadow plains|checker|E8882A 3A2210 E8C090|c
Aphrodite Fritillary|classic|meadow forest|checker|E07A2A 2A1A0E F2E2B8|u
Regal Fritillary|classic|plains meadow|split|E86A2A 1E1A16 F4F0EA|r
Variegated Fritillary|classic|plains meadow|checker|E8A050 6A3A1A F4E0B0|c
Pearl Crescent|rounded|meadow plains|crescent|E8822A 2A1A0E F4F0DA|c
Tawny Crescent|rounded|meadow|stripes|E8862A 2A1A0E F2D8A0|u
Painted Crescent|rounded|plains desert|edge|E8902A 2A1A0E F4F0DA|c
Gorgone Checkerspot|rounded|plains|checker|E8902A 1E1A16 F4F0EA|u
Harris' Checkerspot|rounded|meadow swamp|checker|E87A2A 1E1A16 F4F0DA|u
Edith's Checkerspot|rounded|meadow mountains|checker|2A1A12 E83A2A F4F0DA|u
Tropical Buckeye|rounded|plains savanna|eyes|8A6040 4A3A28 E8862A 1E1A16|c
American Lady|classic|plains meadow|ocelli|E8862A 2A1A0E 4A7AD8 1E1A16|c
Common Brown|classic|plains forest|eyes|C88A4A 6A4A2A 1E1A16 FFFFFF|c
Meadow Argus|rounded|plains meadow|eyes|6A4A30 3A2A1A E8862A 1E1A16|c
Common Evening Brown|leaf|plains forest|dusk|8A6A4A 5A4A30 E8C070 1E1A16|c
Common Bushbrown|rounded|plains forest|ocelli|7A5A40 4A3A28 E8C070 1E1A16|c
Common Four-ring|rounded|plains|ocelli|8A7050 5A4A30 F2D080 1E1A16|c
Common Five-ring|rounded|plains forest|ocelli|9A7A5A 5A4A30 F2D080 1E1A16|c
Danaid Eggfly|classic|plains savanna|tiger|E8862A 1E1A16 F4F0EA|u
Common Leopard|classic|plains meadow|spotted|E8902A 2A1A0E 1E1A16|c
Tawny Coster|longwing|plains savanna|rays|E8862A 1E1A16 F4F0EA|c
Yellow Coster|longwing|plains|rays|E8C84A 1E1A16 F4F0EA|c
Spanish Gatekeeper|classic|mesa meadow|eyes|E8862A 6A4A2A 1E1A16 FFFFFF|u
Southern Gatekeeper|classic|meadow|patch|E8862A 5A3A20 1E1A16|c
Ox-eyed Satyr|classic|meadow plains|eyes|9A7A5A 5A4A30 F2D080 1E1A16|u

# Swallowtails
Mountain Swallowtail|swallowtail|mountains forest|band|1E1A16 0E0A08 F2E080|u
Corsican Swallowtail|swallowtail|mountains meadow|stripes|F2D84A 1E1A16 4A7AD8|r
Southern Swallowtail|swallowtail|meadow mesa|stripes|F4E080 1E1A16 E8642A|u
Iberian Scarce Swallowtail|kite|mesa meadow|stripes|F4F0DA 1E1A16 4A7AD8|u
Victorine Swallowtail|swallowtail|jungle savanna|band|1E1A16 0E0A08 F2D84A E83A3A|u
Polydamas Swallowtail|rounded|jungle savanna|edge|1E1A16 0E0A08 F2D84A|c
Ruby-spotted Cattleheart|rounded|jungle|patch|1E1A16 0E0A08 E83A6A|u
Pink Cattleheart|rounded|jungle|patch|1E1A16 0E0A08 F07AB0 4AD08A|u
Transandean Cattleheart|rounded|jungle|patch|1E1A16 0E0A08 E83A3A F4F0EA|r
Black-and-white Kite|kite|jungle river|zebra|F4F0EA 1E1A16 E83A3A|u
Dark Kite Swallowtail|kite|jungle|stripes|E0E8D0 1E1A16 E83A3A|u
Broad-banded Swallowtail|swallowtail|jungle|band|1E1A16 0E0A08 F2E080|u
Ozark Swallowtail|swallowtail|forest|band|1E1A16 0E0A08 F2D84A 5A7AD0|r
Appalachian Tiger Swallowtail|swallowtail|forest mountains|stripes|F2D04A 1E1A16 E8862A|u
Canadian Tiger Swallowtail|swallowtail|taiga birch|stripes|F2D84A 1E1A16 5A7AD0|c
Noble Swallowtail|swallowtail|savanna forest|split|F2E080 1E1A16 E8642A|r
Christmas Swallowtail|swallowtail|savanna jungle|spotted|1E1A16 0E0A08 F2D84A|u
Emperor Swallowtail|swallowtail|savanna forest|band|1E1A16 0E0A08 F2D84A|r
Green-patch Swallowtail|swallowtail|savanna jungle|patch|1E1A16 0E0A08 4AD08A|u
Constantine's Swallowtail|swallowtail|savanna|band|1E1A16 0E0A08 F2E080|u
Narrow Blue-banded Swallowtail|swallowtail|jungle|band|1E1A16 0E0A08 4AA8E8|u
Giant African Swallowtail|swallowtail|jungle|tiger|E8862A 1E1A16 F2D84A|l
Mountain Green-banded Swallowtail|swallowtail|mountains jungle|band|1E1A16 0E0A08 4AD08A|r
Chinese Windmill|swallowtail|bamboo forest|rays|1E1A16 0E0A08 E86A8A|u
Common Batwing|classic|jungle|rays|1E1A16 0E0A08 E83A3A|u
Great Windmill|swallowtail|jungle mountains|rays|1E1A16 0E0A08 E83A6A|r
Common Windmill|swallowtail|jungle|rays|2A2A20 0E0A08 E86A8A|u
Crimson Rose|swallowtail|jungle savanna|patch|1E1A16 0E0A08 E83A4A F4F0EA|u
Common Clubtail|swallowtail|jungle bamboo|band|1E1A16 0E0A08 F4F0EA E83A4A|r
Yellow-crested Spangle|swallowtail|jungle|band|1E1A16 0E0A08 F2D84A|u
Spangle|swallowtail|jungle mountains|spotted|1E1A16 0E0A08 5A9AE8|u
Banded Swallowtail|swallowtail|jungle|band|1E1A16 0E0A08 F4F0EA|c
Great Blue Mime|classic|jungle|sheen|1A1A30 0E0A08 5A8AF0|r
Common Raven|classic|jungle|stripes|1E1A16 F4F0EA E8642A|u
Green Dragontail|kite|jungle river|glass|D0F0D0 1E1A16 4AD08A|r
Common Jay|kite|jungle|spotted|1E1A16 0E0A08 7AD0F0|c
Blue Triangle|swallowtail|jungle bamboo|band|1E1A16 0E0A08 4AB0F0|c
Green-spotted Triangle|swallowtail|jungle|spotted|1E1A16 0E0A08 7AE0A0|u
Spotted Zebra|kite|jungle|zebra|F4F0EA 1E1A16 4AA8E8|u
Chain Swordtail|kite|jungle|stripes|F4F0DA 2A2A20 E8642A|u
Lesser Zebra|kite|jungle|zebra|F4F0EA 1E1A16 F2D84A|u
Southern Birdwing|birdwing|jungle|split|1E1A16 F2C83A 0E0A08|r
Common Birdwing|birdwing|jungle bamboo|split|1E1A16 F2D84A 0E0A08|r
Goliath Birdwing|birdwing|jungle|split|1E1A16 4AD08A F2C83A|l
Paradise Birdwing|birdwing|jungle|jewel|1E1A16 0E0A08 4AE0A0 F2C83A|l

# Woodland
Asian Comma|scalloped|forest taiga|speckle|D8822A 3A2210 F4E0B0|c
Hoary Comma|scalloped|taiga mountains|speckle|C87A3A 3A2A1A C8C0B0|u
Satyr Comma|scalloped|forest river|speckle|E8902A 3A2A1A F4E0B0|u
False Comma|scalloped|forest|edge|C8803A 2A1A0E F4F0EA|r
Yellow-legged Tortoiseshell|scalloped|forest birch|edge|D8862A 2A1A0E 4A7AD8|r
Short-tailed Admiral|classic|forest mountains|band|3A2A1E 1E1A16 E8862A F4F0EA|u
Weidemeyer's Admiral|classic|mountains forest|band|1E1A16 0E0A08 F4F0EA|u
Lorquin's Admiral|classic|forest river|band|1E1A16 0E0A08 F4F0EA E8862A|u
California Sister|classic|forest|band|1E1A16 0E0A08 F4F0EA E8862A|u
Indian White Admiral|classic|forest mountains|band|1E1A16 0E0A08 F4F0EA|u
Sordid Emperor|classic|forest|gradient|8A5A30 C8803A F4F0EA 2A1A0E|u
Japanese Emperor|classic|forest mountains|sheen|2A2A3A 1E1A16 9A6AF0 F4F0EA|r
White Emperor|classic|forest|tip|F4F0EA 6A6A60 F4F0EA|r
Siberian Purple Emperor|classic|taiga forest|sheen|2A2420 1E1A16 A07AF0|r
Constable|classic|forest roofed|split|1E1A16 F2E080 1E1A16|r
Circe|classic|forest river|band|1E1A16 0E0A08 F4F0EA|u
Creole Pearly-eye|classic|forest|ocelli|9A8A6A 5A4A30 F4E8C0 1E1A16|c
Southern Pearly-eye|classic|forest swamp|ocelli|8A7A5A 5A4A30 F4E8C0 1E1A16|c
Gemmed Satyr|rounded|forest|ocelli|8A7A6A 5A4A40 C8E0D0 1E1A16|u
Carolina Satyr|rounded|forest|eyes|7A6040 4A3A28 E8C070 1E1A16|c
Red Satyr|rounded|forest mesa|patch|6A4A30 3A2A1A E8642A|u
Canyonland Satyr|rounded|mesa forest|eyes|8A7060 5A4A3A E8A060 1E1A16|u
Nabokov's Satyr|rounded|mountains forest|ocelli|7A5A40 4A3A28 E8A060 1E1A16|r
Woodland Skipper|skipper|forest|edge|E8902A 3A2210 F0A040|c
Mead's Wood-Nymph|classic|forest mesa|patch|6A4A30 3A2A1A E8762A|u
Northern Wall Brown|classic|forest|eyes|C88A4A 6A4A2A 1E1A16 FFFFFF|u
Lattice Brown|classic|forest roofed|checker|8A6A4A 4A3A28 E8C070|u
Dull Forester|rounded|forest|ocelli|8A7050 4A3A28 F2D080 1E1A16|c
Tailed Red Forester|classic|forest|dusk|7A5A40 4A3A28 E8C070 1E1A16|u
Common Treebrown|classic|forest roofed|eyes|8A6A4A 4A3A28 E8C070 1E1A16|c
Bamboo Treebrown|classic|bamboo forest|ocelli|9A7A50 5A4A30 F2D080 1E1A16|u
Straight-banded Treebrown|classic|forest|band|7A5A40 4A3A28 F4F0DA|u
Malabar Tree Nymph|longwing|forest|spotted|F4F0EA 1E1A16 1E1A16|u
Staff Sergeant|classic|forest|stripes|1E1A16 F4F0EA F4F0EA|c
Commander|classic|forest|band|8A4A2A 1E1A16 F4F0EA E8642A|u
Common Sergeant|classic|forest|stripes|2A1E14 F4F0EA E8E0C0|c
Hill Hedge Blue|rounded|forest|basal|9AB8F0 3A3A4A F4F0EA|c
Fourspot Sailer|rounded|forest|spotted|2A1E14 0E0A08 F4F0EA|u
Chestnut-streaked Sailer|rounded|forest|stripes|2A1E14 E8902A E8902A|u
Short-banded Sailer|rounded|forest|band|1E1A16 0E0A08 F4F0EA|c
Clouded Mother-of-pearl|classic|forest jungle|sheen|E8E8E0 B8B0A8 E8C8F0|u
Mother-of-pearl|classic|forest jungle|sheen|C8E8D8 8AA090 E0C8F0|u
Forest Queen|classic|forest jungle|gradient|E8862A F0A040 F4F0EA 2A1A0E|r
Forest Mother-of-pearl|classic|forest|eyes|D8E8E0 9AA8A0 E8862A 1E1A16|u
Indian Purple Emperor|classic|forest mountains|sheen|3A2A20 1E1A16 A07AF0|r

# Blues & Coppers
Eros Blue|rounded|mountains meadow|edge|8AB0F0 3A3A4A F4F0EA|u
Escher's Blue|rounded|meadow mountains|edge|7AA0E8 3A3A4A F4F0EA|u
Meleager's Blue|rounded|mesa meadow|edge|9AB8F0 3A3A4A F4F0EA|r
Damon Blue|rounded|mountains|stripes|7A9AE8 2A2A3A F4F0EA|r
Ripart's Anomalous Blue|rounded|mountains mesa|basal|7A5A40 3A2A1A F4F0EA|r
Osiris Blue|rounded|mountains|gradient|6A8AE8 9AB0F0 F4F0EA 2A2A3A|u
Chapman's Blue|rounded|meadow|basal|6A6A70 7A9AE0 F4F2EA|c
Short-tailed Blue|hairstreak|meadow plains|basal|7A8AE8 3A3A4A E8862A|u
Provencal Short-tailed Blue|hairstreak|meadow mesa|basal|8A9AE8 3A3A4A F4F2EA|u
Odd-spot Blue|rounded|forest|basal|9AB8F0 3A3A4A F4F0EA|c
False Baton Blue|rounded|meadow|basal|7A9AE8 4A8A5A F4F2EA|u
Alcon Blue|rounded|meadow swamp|edge|6A8AD8 2A3A5A F4F2EA|u
Scarce Large Blue|rounded|swamp meadow|spotted|6A8AD8 2A3A5A 1E2A4A|r
Dusky Large Blue|rounded|swamp meadow|dusk|4A4A6A 2A2A3A 9AA8E8 1E1A16|r
Reverdin's Blue|rounded|meadow|edge|7A9AE8 2A2A3A E8862A|u
Geranium Argus|rounded|mountains|crescent|6A4A30 F4F0EA E8862A|u
Mountain Argus|rounded|mountains|crescent|5A4030 E8862A F4F0EA|u
Silvery Argus|rounded|mountains meadow|crescent|8A7A6A E8862A F4F0EA|u
Dotted Blue|rounded|mesa desert|spotted|7A9AE8 2A2A3A 1E1A16|u
Square-spotted Blue|rounded|mesa meadow|spotted|8AA0E8 2A2A3A 1E1A16|u
Arrowhead Blue|rounded|mountains meadow|basal|7A9AE8 2A2A3A F4F0EA|u
Acmon Blue|rounded|meadow desert|crescent|8AA0E8 E8862A F4F0EA|c
Lupine Blue|rounded|mountains meadow|crescent|7A9AE8 E8862A 2A2A3A|c
Shasta Blue|rounded|mountains|stripes|8AA0C8 4A5A6A F4F0EA|u
Greenish Blue|rounded|meadow swamp|basal|8AB8C8 4A8A7A F4F0EA|u
Ceraunus Blue|rounded|beach desert|spotted|8AA0E8 3A3A4A 1E1A16|c
Reakirt's Blue|rounded|desert mesa|spotted|8AA0E8 3A3A4A 1E1A16|c
Hawaiian Blue|rounded|flower_forest|sheen|7A9AE8 2A2A3A C8D8FF|r
Common Grass Blue|rounded|plains meadow|basal|8AA0E8 3A3A4A F4F0EA|c
Dark Grass Blue|rounded|plains|gradient|5A6AC8 8A9AE8 F4F0EA 2A2A3A|c
Lesser Grass Blue|rounded|plains|basal|9AB0E8 4A4A5A F4F0EA|c
Pea Blue|hairstreak|plains meadow|stripes|8A7AD0 4A3A6A F4F0EA|c
Zebra Blue|hairstreak|plains savanna|zebra|E8E8F0 6A6A8A F4F0EA|u
Plains Cupid|rounded|plains savanna|spotted|8AA0E8 3A3A4A E8862A|c
Gram Blue|rounded|plains|crescent|9AB0E8 E8862A F4F0EA|c
Lime Blue|rounded|plains savanna|stripes|8AA0C8 4A4A5A F4F0EA|c
Common Cerulean|rounded|plains forest|gradient|5A8AE8 9AB8F0 F4F0EA 2A2A3A|c
Violet Copper|rounded|swamp meadow|sheen|C8803A 3A1E14 9A6AF0|r
Fiery Copper|rounded|meadow mountains|gradient|F07A2A F8B04A F49A4A 3A1A0E|u
Grecian Copper|rounded|mesa mountains|edge|F0702A 3A1A0E F49A4A|u
Balkan Copper|rounded|desert|spotted|F0702A 3A1A0E 2A1A0E|u
Gorgon Copper|rounded|mountains mesa|spotted|C88A3A 3A1E14 2A1A0E|u
Blue Copper|rounded|mountains meadow|sheen|6A9AE8 2A2A3A C8D8FF|u
Edith's Copper|rounded|mountains|crescent|8A6A50 E8862A F4F0EA|u
Hermes Copper|hairstreak|mesa desert|gradient|F2D84A F8E89A F4F0EA 3A2A1A|r

# Whites & Sulphurs
Bath White|classic|plains meadow|marble|F4F2EA 6A8A5A 3A3A3A|u
Eastern Bath White|classic|plains desert|marble|F4F2EA 6A8A5A 3A3A3A|u
Peak White|classic|mountains frozen|marble|F4F2EA 7A9A6A 3A3A3A|r
Mountain Small White|classic|mountains|tip|F4F2EA 6A6A6A F4F2EA|u
Southern White|classic|plains savanna|tip|F4F2EA 4A4A4A F4F2EA|c
Western White|classic|meadow mountains|marble|F4F2EA 6A7A5A 3A3A3A|c
Checkered White|classic|plains desert|checker|F4F2EA 3A3A3A F4F2EA|c
Mustard White|classic|forest taiga|rays|F4F2EA 9AA06A F4F2EA|u
Pine White|classic|taiga mega|rays|F4F2EA 2A2A2A F4F2EA|u
Becker's White|classic|desert mesa|marble|F4F2EA 6A8A5A 3A3A3A|u
Spring White|classic|desert mountains|marble|F4F2EA 7A9A6A 3A3A3A|u
Falcate Orangetip|pointed|forest meadow|tip|F4F2EA E8862A 6A8A5A|u
Gray Marble|classic|mountains desert|marble|E8E8E0 7A7A70 3A3A3A|u
Large Marble|classic|meadow plains|marble|F4F2EA 7A9A6A 3A3A3A|c
Olympia Marble|classic|plains meadow|marble|F4F2EA 8AA07A F0B0C0|u
Greenish Black-tip|classic|desert|tip|F4F2EA 2A2A2A 8AB06A|r
Moroccan Orange Tip|classic|desert mesa|tip|F2E8A0 E8862A F4F0EA|r
Eastern Dappled White|classic|meadow|marble|F4F2EA 6A8A5A 3A3A3A|u
Small Grass Yellow|rounded|plains savanna|tip|F2D84A 2A2418 F8E89A|c
Common Grass Yellow|rounded|plains savanna|edge|F2D84A 2A2418 F8E89A|c
Broad-bordered Grass Yellow|rounded|plains|edge|F2D84A 2A2418 F2D84A|c
Three-spot Grass Yellow|rounded|plains forest|spotted|F2D84A 2A2418 6A5A30|c
Spotless Grass Yellow|rounded|plains|tip|F2D04A 2A2418 F8E89A|c
Lemon Emigrant|classic|plains savanna|gradient|F4F0A0 F2D84A F4F2EA 6A5A30|c
Mottled Emigrant|classic|plains savanna|speckle|F4E8A0 C8A040 F4F2EA|c
Orange Emigrant|classic|plains savanna|gradient|F4E8A0 E8902A F4F2EA 6A4A20|u
Common Emigrant|classic|savanna|tip|F4F0C0 3A3A20 F4F2EA|c
Yellow Orange Tip|classic|savanna plains|tip|F2E080 E8642A 3A2A1A|u
White Orange Tip|classic|savanna desert|tip|F4F2EA E8642A 3A2A1A|u
Great Orange Tip|pointed|savanna jungle|tip|F4F2EA E8762A 3A2A1A|u
Common Gull|classic|plains savanna|edge|F4F2EA 2A2A2A F2E080|c
Psyche|classic|plains forest|tip|F4F2EA 2A2A2A F2E080|c
Pioneer White|classic|savanna desert|spotted|F4F2EA 2A2A2A 1E1A16|c
Painted Jezebel|classic|forest plains|patch|F4F2EA 1E1A16 E83A2A F2D84A|u
Red-base Jezebel|classic|forest|basal|F4F2EA E83A2A 1E1A16|u
Painted Sawtooth|classic|jungle forest|zebra|F2D84A 1E1A16 E83A2A|r
Small Salmon Arab|classic|desert savanna|tip|F4F2EA E8862A 6A4A20|u
Zebra White|classic|jungle|zebra|F4F2EA 1E1A16 F2D84A|u
Lyside Sulphur|classic|desert beach|gradient|F4F0C0 F2E080 F4F2EA 6A5A30|c
Tailed Sulphur|leaf|jungle savanna|edge|F2D84A 3A3A20 F8E89A|u

# Hairstreaks & Metalmarks
Ruddy Hairstreak|hairstreak|forest|gradient|E8762A F0A040 F4F0EA 2A1A0E|u
Sloe Hairstreak|hairstreak|forest meadow|crescent|7A5A40 E8862A F4F0EA|u
Ilex Hairstreak|hairstreak|forest|crescent|6A4A30 E8642A F4F0EA|u
Blue-spot Hairstreak|hairstreak|forest|crescent|6A5A4A 4A7AD8 F4F0EA|u
False Ilex Hairstreak|hairstreak|forest mesa|crescent|7A5A40 E8862A 2A2018|r
Spanish Purple Hairstreak|hairstreak|mesa forest|sheen|5A5A6A 2A2A3A 9AB0F0|r
Hickory Hairstreak|hairstreak|forest|stripes|7A6A5A 2A2018 F4F0EA|u
Oak Hairstreak|hairstreak|forest|stripes|8A7A6A 2A2018 E8862A|u
Gray Hairstreak|hairstreak|plains meadow|crescent|8A8A90 E8642A F4F0EA|c
Red-banded Hairstreak|hairstreak|forest swamp|band|5A5A60 2A2A30 E8642A|c
White M Hairstreak|hairstreak|forest|sheen|3A6AC8 1E1A16 F4F0EA|u
Great Blue Hairstreak|hairstreak|forest|sheen|2A5AC8 1E1A16 7AD0F0|u
Soapberry Hairstreak|hairstreak|desert plains|stripes|8A7A6A 2A2018 F4F0EA|u
Golden Hairstreak|hairstreak|mountains forest|gradient|C8903A F2C860 F4F0EA 3A2A1A|r
Thicket Hairstreak|hairstreak|taiga mountains|band|8A6A50 3A2A1A F4F0EA|u
Bramble Hairstreak|hairstreak|meadow mesa|gradient|6A9A3A 9AC85A F4F0EA 3A2A1A|c
Gold-hunter's Hairstreak|hairstreak|mountains forest|gradient|C8903A E8B860 F4F0EA 3A2A1A|r
Hoary Elfin|hairstreak|taiga mountains|speckle|7A6A60 C8C0B0 3A2A1A|u
Frosted Elfin|hairstreak|meadow forest|speckle|8A6A50 C8C0B0 3A2A1A|r
Brown Elfin|hairstreak|taiga forest|gradient|7A5A40 9A7A5A F4F0EA 3A2A1A|c
Bog Elfin|hairstreak|swamp taiga|stripes|6A5040 2A2018 C8B8A0|r
Western Pine Elfin|hairstreak|taiga|stripes|8A5A3A 3A2A1A E8C080|u
Silver-banded Hairstreak|hairstreak|jungle|band|6A6A70 2A2A30 F4F0EA|u
Fulvous Hairstreak|hairstreak|jungle savanna|crescent|C8803A 3A2A1A F4F0EA|u
Mallow Scrub-Hairstreak|hairstreak|plains desert|crescent|8A8A90 E8642A F4F0EA|c
Dusky-blue Groundstreak|hairstreak|jungle savanna|basal|8A8A90 4A6AD8 F4F0EA|c
Common Tit|hairstreak|jungle|stripes|E8E0D0 6A5A4A E8642A|u
Silverline|hairstreak|jungle forest|stripes|E8902A 6A4A2A C8C0B0|u
Common Silverline|hairstreak|jungle plains|stripes|E89A3A 7A4A2A C8C0B0|c
Yamfly|hairstreak|jungle|gradient|E8862A F0A040 F4F0EA 2A1A0E|u
Common Guava Blue|hairstreak|jungle plains|sheen|6A8AE8 2A2A3A C8D8FF|u
Red Flash|hairstreak|jungle|basal|5A4A40 E83A2A F4F0EA|r
Fluffy Tit|hairstreak|jungle|stripes|F4F0EA 6A5A4A E8862A|u
Purple Sapphire|hairstreak|jungle|sheen|4A3A8A 1E1A2A B07AF0|r
Northern Metalmark|rounded|forest meadow|checker|E8902A 3A2A1A 9AA0A8|u
Little Metalmark|rounded|swamp plains|crescent|E8902A 9AA0A8 3A2A1A|u
Zela Metalmark|rounded|mesa desert|spotted|6A5A4A 2A2018 F4F0EA|u
Red-bordered Metalmark|rounded|desert mesa|edge|6A5A4A E8642A F4F0EA|u
Blue Metalmark|rounded|desert mesa|sheen|4A6AC8 1E1A16 9AB0F0|r
Rawson's Metalmark|rounded|desert|checker|E8902A 3A2A1A F4F0EA|u
Ares Metalmark|rounded|desert mesa|checker|C87A3A 3A2A1A F4F0EA|r
Sword-tailed Beautymark|kite|jungle|stripes|E8E0D0 2A2A20 E8642A|r
Punchinello|rounded|forest|spotted|5A4030 2A1E14 F4F0EA|u
Plum Judy|rounded|jungle forest|band|6A4A30 3A2A1A F4F0EA|u
Common Pierrot|rounded|jungle savanna|spotted|F4F0EA 1E1A16 1E1A16|c

# Skippers
Mediterranean Skipper|skipper|mesa meadow|spotted|7A6A50 4A3A28 F4F0DA|u
Hammock Skipper|skipper|jungle beach|patch|6A4A30 3A2A1A F4F0EA|u
Red-underwing Skipper|skipper|meadow mountains|split|5A4A3A 2A2018 E8642A|u
Safflower Skipper|skipper|mountains meadow|checker|3A3A3A F4F2EA F4F2EA|u
Olive Skipper|skipper|mountains meadow|checker|5A5A3A F4F2EA E8E8D0|u
Oberthur's Grizzled Skipper|skipper|mountains|checker|4A4A4A F4F2EA F4F2EA|u
Rosy Grizzled Skipper|skipper|mesa meadow|checker|5A4A4A F4E8E8 F0B0B0|r
Large Grizzled Skipper|skipper|meadow mountains|checker|3A3A3A F4F2EA E8E8E0|u
Marbled Skipper|skipper|mesa meadow|marble|8A7A6A 4A3A2E F4F0DA|u
Tufted Marbled Skipper|skipper|mesa|marble|9A8A70 4A3A2E F4F0DA|u
Dingy Skipper|skipper|meadow|dusk|4A3E34 2A2018 B0A090 1E1A16|c
Pygmy Skipper|skipper|mesa desert|speckle|8A7A5A 4A3A2E C8B890|c
Small Checkered Skipper|skipper|meadow|checker|3A2A1A E8B84A F4D080|u
Northern Chequered Skipper|skipper|taiga swamp|checker|3A2A1A E8B84A E8B84A|u
Large Chequered Skipper|skipper|swamp meadow|checker|4A3A2A E8C860 F4E0A0|r
Juvenal's Duskywing|skipper|forest|spotted|5A4A3A 2A2018 F4F0EA|c
Common Roadside-Skipper|skipper|forest|spotted|4A3A30 2A2018 F4F0DA|c
Least Skipper|skipper|swamp river|gradient|E8902A F0B060 F4F0DA 3A2A1A|c
Delaware Skipper|skipper|meadow swamp|edge|E89A2A 3A2210 F0A040|c
Crossline Skipper|skipper|plains meadow|edge|C88A3A 4A3018 F0B060|c
Leonard's Skipper|skipper|meadow|patch|8A4A2A 3A1E10 F4E0A0|u
Indian Skipper|skipper|meadow mountains|edge|E8902A 3A2210 F4E0A0|u
Dun Skipper|skipper|meadow river|dusk|4A3A2A 2A2018 B0A080 1E1A16|c
Two-spotted Skipper|skipper|swamp|spotted|6A4A30 3A2A1A F0B040|u
Black Dash|skipper|swamp|band|E8902A 3A2210 2A1A0E|u
Long Dash|skipper|meadow taiga|band|E8902A 3A2210 3A2210|u
Arogos Skipper|skipper|plains|edge|E8A040 3A2210 F2C860|r
Dotted Skipper|skipper|plains savanna|spotted|8A6A4A 4A3A2A F4F0DA|r
Swarthy Skipper|skipper|plains meadow|gradient|6A5A40 8A7A5A C8B890 3A2A1A|c
Clouded Skipper|skipper|forest swamp|dusk|3A3028 1E1A16 A89880 1E1A16|c
Eufala Skipper|skipper|plains desert|spotted|8A7A6A 4A3A2E F4F0DA|c
Common Banded Awl|skipper|jungle forest|band|6A4A30 3A2A1A F4F0EA|c
Orange Awlet|skipper|jungle|gradient|E8762A F0A040 F4F0EA 3A1A0A|u
Brown Awl|skipper|jungle|gradient|7A5A40 9A7A5A F4F0EA 3A2A1A|c
Indian Palm Bob|skipper|jungle bamboo|patch|5A4030 2A1E14 F2D84A|c
Grass Demon|skipper|jungle plains|spotted|3A2A1E 1E1610 F2D84A|c
Chestnut Bob|skipper|jungle|gradient|8A4A2A C87A3A F4D080 2A1A0E|c
Pale Palm Dart|skipper|plains jungle|stripes|E8902A 3A2210 F2C860|c
Water Snow Flat|skipper|jungle river|spotted|3A2A1E 1E1610 F4F0EA|u
Tricolour Pied Flat|skipper|jungle forest|patch|2A1E14 1E1610 F4F0EA E8862A|u

# Rainforest
Common Morpho|classic|jungle|band|1E1A16 0E0A08 4AB0F0|c
Godart's Morpho|classic|jungle|sheen|2A8AF0 1E1A16 B0E8FF|r
Deidamia Morpho|classic|jungle|band|3A2A1E 1E1A16 4AB0F0|u
Hecuba Morpho|classic|jungle|gradient|E8862A F0A040 1E1A16 1E1A16|l
Telemachus Morpho|classic|jungle|sheen|1A6AE8 1E1A16 7AE0FF|r
Theseus Morpho|classic|jungle mountains|gradient|9AA0A8 C8D0D8 F4F0EA 3A3A40|u
Helena Morpho|classic|jungle|band|1E1A16 0E0A08 7AE0FF|l
Anaxibia Morpho|classic|jungle|sheen|2A7AE8 1E1A16 9AE0FF|r
Pale Owl|classic|jungle|ocelli|C8B898 7A6A50 F4F0EA 1E1A16|u
Idomeneus Giant Owl|classic|jungle roofed|eyes|6A5040 3A2E24 E8C060 1E1A16|u
Atreus Owl|classic|jungle|eyes|4A3A6A 2A1E3A F2D080 1E1A16|r
Mexican Owl|classic|jungle|eyes|7A6A50 4A3A28 E8C060 1E1A16|u
Pink Glasswing|longwing|jungle|glass|F0D0E0 6A4A5A F07AC0|u
Amber Phantom|rounded|jungle|glass|F0D8B0 6A4A2A E8902A|r
Blushing Phantom|rounded|jungle|glass|F0D0D8 6A5A60 E86A8A|r
Rusted Clearwing Satyr|rounded|jungle|glass|E8D8C0 6A5040 E8862A|u
Crystal-winged Satyr|rounded|jungle roofed|glass|E0E8F0 5A6A70 E8E0F0|r
Tiger-striped Leafwing|leaf|jungle|tiger|E8862A 1E1A16 F2D84A|u
Angled Leafwing|leaf|jungle|gradient|8A4A2A C87A3A F0A040 2A1A0E|u
Blue Leafwing|leaf|jungle|sheen|2A2A40 1E1A16 4A8AF0|u
Purple Leafwing|leaf|jungle|sheen|3A2A40 1E1A16 9A6AF0|r
Florida Leafwing|leaf|swamp jungle|gradient|D8602A F08A3A F0A040 3A1A0A|r
Starry Night Cracker|classic|jungle|speckle|1E2A5A 7AA0F0 0E1430|u
Glaucous Cracker|classic|jungle|speckle|8AA0B0 2A2A30 F4F2EA|c
Gray Cracker|classic|jungle savanna|speckle|9A9AA0 2A2A30 F4F2EA|c
Variable Cracker|classic|jungle|speckle|7A8AA0 2A2A30 E8C070|c
Blomfild's Beauty|classic|jungle|band|1E1A16 0E0A08 E8642A 4AB0F0|r
Smooth-banded Sister|classic|jungle|band|3A2A1E 1E1A16 F4F0EA E8862A|u
Waiter Daggerwing|leaf|jungle|stripes|F4F0EA 6A4A2A E8902A|u
Orange Daggerwing|leaf|jungle|stripes|E8762A 3A1A0A F4A040|u
Tropical Leafwing|leaf|jungle savanna|gradient|C8602A E8902A F0A040 2A1A0E|c
Golden Helicon|longwing|jungle|tiger|F2C84A 1E1A16 E8642A|u
Wallace's Longwing|longwing|jungle|sheen|1E1A16 0E0A08 4A8AF0|u
Small Postman|longwing|jungle|longwing|1E1A16 0E0A08 E83A3A F2D84A|c
Sapho Longwing|longwing|jungle|longwing|1E1A16 3A6AC8 F4F0EA|u
Hewitson's Longwing|longwing|jungle|zebra|1E1A16 F2E080 F2E080|c
Hecuba Longwing|longwing|jungle mountains|longwing|1E1A16 0E0A08 F2D84A F4F0EA|u
Ismenius Tiger|longwing|jungle|tiger|E8902A 1E1A16 F2D84A|c
Numata Longwing|longwing|jungle|tiger|E8762A 1E1A16 F2D84A|u
Hecalesia Longwing|longwing|jungle|longwing|3A1A1E 1E0A0E E83A3A F2D84A|u
Small Flambeau|longwing|jungle|gradient|E8642A F0902A F4F0EA 2A1A0E|u
Mexican Silverspot|longwing|jungle savanna|edge|E8762A 1E1A16 F4F0EA|c
Ethilia Longwing|longwing|jungle|stripes|E8862A 1E1A16 F2D84A|u
Grecian Shoemaker|classic|jungle|patch|1E1A16 0E0A08 4AB0F0 F4F0EA|r
Red Anartia|classic|jungle|band|2A1A14 0E0A08 E83A3A F4F0EA|u
Blue Doctor|classic|jungle|band|1E1A16 0E0A08 4A8AF0 E83A3A|u
Blue-frosted Catone|rounded|jungle|sheen|2A1E3A 1E1A16 B07AF0|u
Mosaic|classic|jungle|band|1E1A16 0E0A08 4AB0F0 E8862A|r
Bamboo Page|classic|jungle bamboo|patch|1E1A16 0E0A08 7AE0A0|u
Rusty Page|pointed|jungle|tip|C8602A 1E1A16 F4F0EA|c
Silver Emperor|classic|jungle|sheen|8A8A98 3A3A48 E8E8F0|r
Blue-banded Purplewing|classic|jungle|band|1E1A16 0E0A08 4A8AF0|c
Dirce Beauty|classic|jungle|zebra|3A2A1E F2E080 F2E080|u
Orange-banded Shoemaker|classic|jungle|band|1E1A16 0E0A08 E8862A|u
Cattleheart White|classic|jungle|patch|F4F0EA 1E1A16 E83A4A|u
Painted Courtesan|classic|jungle|split|E8862A 1E1A16 F4F0EA|u
Banded Yeoman|classic|jungle|band|E8862A 1E1A16 F4F0EA|c
Common Nawab|classic|jungle forest|band|3A2A1E 1E1A16 F2E080|u
Tawny Rajah|classic|jungle|gradient|C8803A E8A04A F4F0EA 2A1A0E|u
Black Rajah|classic|jungle|band|1E1A16 0E0A08 F4F0EA|u
Great Nawab|classic|jungle mountains|split|F2E080 2A2018 E8642A|r
Common Map Butterfly|classic|jungle|stripes|F4F0EA 1E1A16 E8902A|c
Vagrant|classic|jungle|tip|E8902A 1E1A16 F4F0EA|c
Common Castor|classic|jungle|stripes|E8862A 1E1A16 F4F0EA|c
Angled Castor|classic|jungle|stripes|E8902A 3A1A0A F4F0EA|c
Small Leopard|classic|jungle|edge|E8762A 1E1A16 F4F0EA|c
Common Duffer|classic|jungle bamboo|sheen|3A2A1E 1E1A16 7A5AC8|u
Common Faun|classic|jungle bamboo|ocelli|C8803A 6A4A2A F4F0EA 1E1A16|u
Jungle Queen|classic|jungle|gradient|3A3A6A 6A6AC8 F4F0EA 1E1A16|r
Common Palmfly|classic|jungle|patch|3A2A1E 1E1A16 E8862A|c

# Savanna & Desert
White-banded Swallowtail|swallowtail|savanna jungle|band|1E1A16 0E0A08 F4F0EA|u
Green-veined Emperor|classic|savanna|rays|E8E8C0 3A8A5A F4F0EA|r
White-barred Charaxes|classic|savanna|band|3A2A1E 1E1A16 F4F0EA|u
Flame-bordered Charaxes|classic|savanna|edge|3A2A1E 1E1A16 E8642A|r
Demon Charaxes|classic|savanna|sheen|1E1A16 0E0A08 4A8AF0|r
Blue-spotted Charaxes|classic|savanna jungle|spotted|1E1A16 0E0A08 4AB0F0|u
Giant Charaxes|classic|savanna|gradient|C8602A E8902A F4F0DA 2A1A0E|r
Pearl Emperor|classic|savanna|crescent|E8D0A0 E8642A F4F0EA|u
Guineafowl|classic|savanna jungle|spotted|1E1A16 0E0A08 F4F0EA|c
African Joker|classic|savanna|edge|E8862A 1E1A16 F4F0EA|c
Bush Beauty|rounded|savanna|ocelli|C8803A 6A4A2A F4F0EA 1E1A16|c
Brown Pansy|rounded|savanna|ocelli|8A5A30 4A2A14 E8A040 1E1A16|c
Soldier Pansy|rounded|savanna|ocelli|5A4030 2A1E14 E8862A 1E1A16|c
Dark Blue Pansy|rounded|savanna|patch|1E1A16 0E0A08 4A8AF0|u
Eyed Pansy|rounded|savanna jungle|eyes|E8862A 3A2A1A 4A7AD8 1E1A16|c
African Map|classic|savanna|stripes|F4F0EA 1E1A16 E8902A|u
Common Acraea|longwing|savanna|spotted|E8862A 1E1A16 1E1A16|c
Garden Acraea|longwing|savanna plains|spotted|E87A5A 1E1A16 1E1A16|c
Dusky-veined Acraea|longwing|savanna|rays|E8A060 3A2A1A F4F0EA|c
Clearwing Acraea|longwing|savanna|glass|E8D8C0 3A2A1A E8862A|u
Wandering Donkey Acraea|longwing|savanna|rays|C8803A 3A2A1A F4F0EA|c
Large Spotted Acraea|longwing|savanna desert|spotted|E8A060 1E1A16 1E1A16|u
Golden Piper|classic|savanna|band|1E1A16 0E0A08 F2C84A|u
Novice|pointed|savanna jungle|rays|E8A060 1E1A16 F4F0EA|c
Friar|pointed|savanna|band|3A2A1E 1E1A16 F4F0EA|u
Layman|pointed|savanna jungle|rays|F4F0EA 1E1A16 F4F0EA|u
Desert Babul Blue|rounded|desert savanna|stripes|8A7AD0 4A3A6A F4F0EA|c
Desert Grass Yellow|rounded|desert|tip|F2E080 3A3A20 F8E89A|c
Sooty Orange Tip|classic|desert savanna|tip|F4F2EA 3A2A2A E8862A|r
Desert White|classic|desert|marble|F4F2EA 7A8A6A 3A3A3A|u
Millet Skipper|skipper|desert|speckle|8A7A5A 4A3A2E C8B890|c
Sandy Grizzled Skipper|skipper|desert mesa|checker|8A7A5A F4F0DA F4F0DA|u
Mojave Sootywing|skipper|desert mesa|spotted|2A2420 1A1612 F4F2EA|u
Desert Checkered Skipper|skipper|desert|checker|4A4A4A F4F2EA F4F2EA|c
Sonoran Blue|rounded|desert mesa|patch|5A8AE8 2A2A3A E8642A|r
Small Dotted Blue|rounded|desert|spotted|8AA0E8 2A2A3A 1E1A16|u
Arizona Hairstreak|hairstreak|desert mesa|gradient|6A9A3A 9AC85A F4F0EA 3A2A1A|u
Chiricahua White|classic|mesa mountains|edge|F4F2EA 2A2A2A E8902A|r
Theona Checkerspot|rounded|desert mesa|checker|E8902A 2A1A0E F4F0EA|u
Dotted Checkerspot|rounded|desert plains|spotted|E8902A 2A1A0E 1E1A16|u

# Mountains & Tundra
Rocky Mountain Parnassian|rounded|mountains|eyes|F4F2EA 3A3A3A E83A2A 1E1A16|r
Eversmann's Parnassian|rounded|mountains frozen|spotted|F4F2EA 4A4A4A E83A2A|r
False Apollo|rounded|mountains mesa|spotted|F4F2EA 3A3A3A E8642A|r
Arctic White|classic|mountains|marble|F4F2EA 6A6A6A 3A3A3A|u
Moorland Clouded Yellow|classic|swamp mountains|edge|F2E8A0 4A5A3A F4F2EA|r
Mariposa Copper|rounded|mountains|edge|F0702A 3A1A0E F49A4A|u
Alpine Heath|rounded|mountains|ocelli|9A7A50 5A4A30 F2D080 1E1A16|u
Darwin's Heath|rounded|mountains|ocelli|C8A070 7A5A3A F4F0EA 1E1A16|u
Large Ringlet|rounded|mountains grove|ocelli|3A2A1E 1E1610 E8862A 1E1A16|u
Swiss Brassy Ringlet|rounded|mountains|ocelli|3A2A1E 1E1610 E8A040 1E1A16|r
Silky Ringlet|rounded|mountains grove|eyes|3A2A1E 1E1610 E8862A 1E1A16|u
Sooty Ringlet|rounded|mountains|dusk|2A2420 1A1612 9A8A7A 1E1A16|u
Arctic Woodland Ringlet|rounded|frozen grove|ocelli|4A3A2A 2A1E14 E87A3A 1E1A16|u
Alpine Grayling|classic|mountains frozen|speckle|9A8A7A 5A4A40 F4F0EA|r
Norse Grayling|classic|taiga frozen|eyes|9A8A6A 5A4A30 E8B070 1E1A16|r
Titania's Fritillary|rounded|mountains grove|checker|E8902A 2A1A0E B8A0C0|u
Cranberry Fritillary|rounded|swamp frozen|checker|E8902A 3A2210 E8C0C0|r
Thor's Fritillary|rounded|frozen mountains|checker|D88A3A 2A1A0E F4F0EA|r
Astarte Fritillary|rounded|mountains frozen|crescent|E8902A 2A1A0E F4F0EA|r
Greater Banded Apollo|rounded|mountains frozen|glass|F4F2EA 6A6A70 E83A2A|l

# Wetlands & Coasts
Dorcas Copper|rounded|swamp|edge|F0702A 2A1A0E F49A4A|r
Swamp Tiger|pointed|swamp mangrove_swamp|tiger|E8862A 1E1A16 F4F0EA|u
Mangrove Blue|rounded|mangrove_swamp beach|basal|8AA0E8 3A3A4A F4F0EA|u
Disguised Scrub-Hairstreak|hairstreak|mangrove_swamp|crescent|8A8A90 E8642A F4F0EA|u
Great Copper|rounded|beach swamp|crescent|C8803A E8642A F4E0B0|u
Coastal Green Hairstreak|hairstreak|beach|gradient|6A9A3A 9AC85A F4F0EA 3A2A1A|u
Yuma Skipper|skipper|beach desert|speckle|B89A70 6A5030 F4F0DA|c
Mulberry Wing|skipper|swamp|marble|6A4A30 3A2A1A F2C860|u
Sedge Skipper|skipper|swamp river|edge|C8862A 4A3018 F2C860|u
Duke's Skipper|skipper|swamp river|dusk|5A4A3A 2A2018 B0A080 1E1A16|r
Rare Skipper|skipper|swamp mangrove_swamp|edge|C8862A 3A2210 F2C860|r
Eyed Brown|classic|swamp river|ocelli|C8B898 7A6A50 F4F0EA 1E1A16|c
Smoky Eyed Brown|classic|swamp|ocelli|8A7A60 5A4A30 F4F0EA 1E1A16|u
Tree Grayling|classic|swamp beach|eyes|8A7A6A 4A3A2E E8C070 1E1A16|u
Mimic|classic|beach savanna|tiger|E8862A 1E1A16 F4F0EA|u

# Wonders of the World
Sunflower Sentinel|classic|plains|gradient|F2C82A F8E86A 8A5A14 3A2A10|u
Dandelion Puff|rounded|plains meadow|speckle|F4E04A F4F2EA 8A7A20|c
Poppy Petal|classic|plains flower_forest|patch|E83A2A 3A1A12 1E1A16|c
Cornflower Courier|classic|flower_forest meadow|sheen|4A6AD8 1E2A5A 9AB0F0|u
Allium Wisp|rounded|flower_forest|speckle|B07AD8 7A4AA8 E8C8F0|u
Oxeye Glider|classic|plains meadow|tip|F4F2EA F2C82A F4F2EA|c
Azure Bluet|rounded|plains|basal|E8F0F4 9AB0D0 F2E080|c
Lily of the Valley|longwing|forest flower_forest|glass|F4F4EC 8AA06A F4F4EC|u
Blue Orchid Swallowtail|swallowtail|swamp|gradient|4AA8E8 9AD8F8 F4F0EA 1E3A5A|u
Peony Puff|rounded|forest flower_forest|gradient|F0A8C8 F8D0E0 F4F0EA 8A4A6A|u
Lilac Lacewing|classic|forest flower_forest|speckle|C8A0D8 8A6AA8 F4E0FF|u
Rose Bush Swallowtail|swallowtail|forest plains|patch|1E1A16 0E0A08 E83A3A|u
Sweet Berry Skipper|skipper|taiga|spotted|3A5A2A 1E3A14 E83A3A|c
Glow Lichen Wing|classic|lush_caves deep_dark|speckle|3A4A3A 8AE0B0 1A2A1A|u
Big Dripleaf|leaf|lush_caves|gradient|4A8A2A 7AB84A 2A5A14 1E3A0E|c
Hanging Root|longwing|lush_caves|rays|8A6A4A 4A3A2A C8A880|c
Calcite Glimmer|classic|mountains|marble|E8E8E0 B8B8B0 9A6AD8|u
Tuff Skipper|skipper|mountains|speckle|6A6A60 4A4A40 9A9A90|c
Dripleaf Duskwing|skipper|lush_caves|dusk|3A5A2A 1E3A14 8AC04A 1E1A16|u
Copper Bulb|rounded|mountains|basal|C8703A F8C860 4AB89A|r
Oxidized Copper Kite|kite|mountains river|gradient|4AB89A 7AD8C0 C8703A 1E3A30|r
Trial Spawner Flame|pointed|mountains|flame|1A1A2A E8862A F8D84A 0A0A14|r
Breeze Wing|longwing|mountains|rays|C8E0F0 6A8AD0 F4F0FF|r
Ominous Bottle|rounded|mountains|jewel|2A1A3A 140A1E 4AE0A0 0A0414|r
Armadillo Scute|skipper|savanna mesa|checker|C8803A 6A4A2A E8A060|u
Wolf Armor|classic|taiga forest|edge|9A9A90 4A4A40 E8E8E0|u
Bee Nest Flutter|rounded|flower_forest plains|stripes|F2C82A 2A1A0E F8E08A|c
Honey Bottle|classic|flower_forest|gradient|F2A82A F8D86A F8E89A 6A3A0A|u
Axolotl Pink|rounded|lush_caves|basal|F0A0C0 E8642A F8D0E0|u
Glow Squid Ink|longwing|river deep_dark|speckle|0E3A3A 4AF0D0 0A2020|r
Turtle Scute|classic|beach|checker|4A8A2A 2A5A14 8AC04A|u
Coral Reef|scalloped|beach|patch|E86A8A 8A2A3A F2D84A 4AA8E8|r
Tropical Fish|classic|beach|split|E8862A F4F0EA 1E1A16|u
Nautilus Shell|rounded|beach|stripes|F0E0C8 C8703A F4F0EA|u
Sea Pickle Glow|rounded|beach|spotted|4A6A2A 2A4A14 C8F06A|c
Kelp Drifter|longwing|beach river|stripes|3A6A2A 2A4A14 6A9A3A|c
Mangrove Propagule|leaf|mangrove_swamp|gradient|4A6A2A 7A9A3A C8D86A 2A3A14|c
Mud Brick|rounded|mangrove_swamp|checker|8A6A4A 5A4030 B89A70|c
Frogspawn|rounded|swamp mangrove_swamp|spotted|5A7A6A 2A3A30 1E1A16|c
Froglight Glow|classic|mangrove_swamp swamp|gradient|F2E080 F8F0B0 E8A0D0 6A5A30|r
Suspicious Sand|classic|desert beach|speckle|E8D8A0 B8A060 F4F0D0|u
Pottery Sherd|classic|desert mesa|band|C8703A 6A3A1A 2A1A0E|u
Sniffer Moss|skipper|flower_forest meadow|speckle|6A8A3A 3A5A1A E8642A|u
Pink Petals|rounded|cherry_grove|speckle|F6BCD6 FFF0F6 E07AA8|c
Cherry Leaf Swallowtail|swallowtail|cherry_grove|gradient|F6BCD6 FFF0F6 F4F0EA 8A3A5A|u
Snow Golem|classic|frozen grove|edge|F4F4F4 C8D0D8 E8862A|u
Powder Snow|rounded|frozen grove|glass|F4F8FC 9AB0C8 E8F0F8|r
Blue Ice|classic|frozen|sheen|7AA8E8 3A6AB8 C8E8FF|r
Mooshroom Wing|classic|mooshroom_island|spotted|C83A2A 6A1A14 F4F0EA|r
Ancient City Echo|longwing|deep_dark|jewel|0E2A30 0A1A20 2ADFE0 05141A|l
"""
