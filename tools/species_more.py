"""The second wave of butterflies: 300 more for the Overworld, 50 for the Nether and 50 for the End.

One line per species:  Name | wing shape | habitats | pattern | colours | rarity
Colours are base, pattern, accent and an optional fourth (eye centres, borders).
Rarity: c = common, u = uncommon, r = rare, l = legendary.
"""

TABLE = """
# Meadows & Fields
Small White|classic|plains meadow|tip|F4F2EA 5A5A5A F4F2EA|c
Green-veined White|classic|meadow river|rays|F4F2EA 8AA05A FFFFFF|c
Wood White|rounded|forest meadow|tip|F6F4EC 9A9A8A FFFFFF|u
Large White|classic|plains|tip|F2F0E6 2A2A2A F2F0E6|c
Black-veined White|classic|meadow mountains|rays|F4F2EA 1E1A16 FFFFFF|u
Pale Clouded Yellow|classic|plains meadow|tip|F2EAA0 4A3A2A F8B040|u
Orange Sulphur|classic|plains savanna|tip|F4A428 3A2A1A F8D85A|c
Little Yellow|rounded|plains savanna|tip|F6D82A 2A2418 F8E89A|c
Sleepy Orange|classic|plains savanna|edge|F08A1E 3A2A14 F4B04A|c
Dainty Sulphur|rounded|desert plains|split|F4E05A 2A2A2A E8902A|c
Dark Green Fritillary|classic|meadow mountains|checker|E8902A 3A2210 F4F2EA|u
High Brown Fritillary|classic|meadow forest|checker|E07A1E 2A1A0E F2E2B8|r
Queen of Spain Fritillary|pointed|plains meadow|checker|E89A30 2A1A0E E8E8F0|u
Heath Fritillary|rounded|meadow|checker|E07A2A 2A1A12 F2D8A0|u
Glanville Fritillary|rounded|beach meadow|checker|E8942E 2A1A0E F4E4B0|u
Variable Checkerspot|rounded|mountains meadow|checker|2A1A12 E8642A F4F0DA|u
Silvery Checkerspot|rounded|river meadow|edge|E8962E 2A1A0E F4F2EA|c
Northern Crescent|rounded|meadow plains|crescent|E8822A 2A1A0E F2E0B0|c
Phaon Crescent|rounded|plains river|band|E07A2A 2A1A0E F4EEDC|c
Small Heath|rounded|plains meadow|eyes|E8B060 8A6A3A F4E8C0 1E1A16|c
Gatekeeper|classic|meadow plains|eyes|E8862A 5A3A20 1E1A16 FFFFFF|c
Large Heath|rounded|swamp meadow|ocelli|D8A060 7A5A3A F2E4C0 1E1A16|u
Common Wood-Nymph|classic|meadow plains|patch|6A4A30 3A2A1A E8C860|c
Grayling|classic|beach desert|eyes|8A7A6A 4A3A2E E8C070 1E1A16|u
Common Ringlet|rounded|meadow plains|gradient|D8A860 F4E0A8 F4F0E0 6A4A2A|c
Duke of Burgundy|rounded|meadow forest|checker|5A3A20 E89A3A F4F0E0|r
Small Pearl-bordered Fritillary|classic|meadow swamp|checker|E8882A 2A180E F4F2EA|u
Field Crescent|rounded|meadow mountains|stripes|2A1A12 E8822A F4E0B0|c
Mexican Yellow|classic|plains desert|tip|F4D82A 1E1A16 F8E89A|u
Clouded Sulphur|classic|plains meadow|edge|F4E86A 3A3A20 F2A040|c
Berger's Clouded Yellow|classic|meadow|tip|F4E890 3A3A2A F8A040|u
American Snout|leaf|plains river|patch|7A5A3A 2A1A12 F0A040|u
Lesser Marbled Fritillary|classic|meadow swamp|checker|E89838 2A1A0E F0E0B0|u
Cardinal|pointed|plains meadow|gradient|E8962E 7A9A6A F4F2EA 2A1A0E|r
Southern Small White|classic|plains|tip|F4F2EA 4A4A4A FFFFFF|c
West Coast Lady|classic|meadow plains|edge|E8862A 2A1A0E F2E2C0|u
Grey Pansy|rounded|plains savanna|ocelli|B8B4A8 6A6A60 E8902A 1E1A16|c
Lemon Pansy|rounded|plains savanna|ocelli|E8C840 6A5A30 E8642A 1E1A16|c
Peacock Pansy|rounded|swamp plains|eyes|E8862A 2A1A0E 4A7AD8 1E1A16|u
Chocolate Pansy|rounded|plains forest|ocelli|8A5A30 4A2A14 E8A040 1E1A16|c

# Swallowtails
Anise Swallowtail|swallowtail|meadow mountains|band|1E1A16 0E0A08 F2D84A E85A2A|u
Western Tiger Swallowtail|swallowtail|forest river|stripes|F2D04A 1E1A16 5A7AD0|c
Two-tailed Swallowtail|swallowtail|mountains forest|stripes|F4D84A 1E1A16 E88A3A|u
Pale Swallowtail|swallowtail|mountains forest|stripes|F4F0DA 1E1A16 5A7AD0|u
Indra Swallowtail|swallowtail|mountains mesa|band|1E1A16 0E0A08 F2E2A0 5A7AD0|r
Thoas Swallowtail|swallowtail|jungle savanna|band|1E1A16 0E0A08 F2D84A|c
Gold Rim Swallowtail|rounded|jungle plains|edge|1E1A16 0E0A08 F2D84A|c
Ruby-spotted Swallowtail|swallowtail|jungle|patch|1E1A16 0E0A08 E83A4A|u
Fluminense Swallowtail|swallowtail|swamp jungle|band|1E1A16 0E0A08 F4F0DA|r
Paris Peacock|swallowtail|jungle bamboo|jewel|1A2A1E 2A1E12 3AD0A8 0E0A08|r
Blue Mormon|classic|jungle bamboo|sheen|1A1612 0E0A08 4A7AE8|u
Common Mormon|swallowtail|jungle plains|band|1E1A16 0E0A08 F4F0DA|c
Red Helen|classic|jungle|patch|1E1A16 0E0A08 F4F0DA E83A2A|u
Common Mime|classic|jungle|spotted|1E1A16 0E0A08 F0F0EA|c
Citrus Swallowtail|swallowtail|savanna jungle|spotted|1E1A16 0E0A08 F2E080|c
Mocker Swallowtail|swallowtail|savanna forest|split|F4F0DA 1E1A16 E8A040|u
Green-banded Swallowtail|swallowtail|savanna forest|band|1E1A16 0E0A08 4AD08A|u
Glassy Bluebottle|classic|jungle|glass|9AD8E8 1E1A16 4AA8E8|u
Spot Swordtail|kite|jungle bamboo|stripes|F4F0DA 1E1A16 E8642A|u
Fourbar Swordtail|kite|jungle|stripes|E8F0E0 2A2A20 E85A2A|u
Scarlet Swallowtail|swallowtail|jungle|patch|1E1A16 0E0A08 E83A3A|u
Chinese Peacock|swallowtail|bamboo cherry_grove|jewel|1E2A1E 2A1E12 3AE0B8 0E0A08|r
Japanese Luehdorfia|swallowtail|cherry_grove forest|stripes|F2D84A 1E1A16 E83A2A|r
Krishna Peacock|swallowtail|mountains bamboo|jewel|1A2618 2A1E12 4AE8B0 0E0A08|l
Short-tailed Swallowtail|swallowtail|beach plains|band|1E1A16 0E0A08 F2D84A|u
Schaus' Swallowtail|swallowtail|mangrove_swamp|band|1E1A16 0E0A08 F2D84A E8902A|r
Bahamian Swallowtail|swallowtail|beach mangrove_swamp|band|2A2018 0E0A08 F2E080|u
Androgeus Swallowtail|swallowtail|savanna jungle|split|F2D84A 1E1A16 F2D84A|u
Dusky Swallowtail|swallowtail|jungle|dusk|3A3A30 1E1A16 E8C070 1E1A16|u
White Dragontail|kite|jungle river|glass|F4F0EA 1E1A16 4AE0B0|r

# Woodland
White-letter Hairstreak|hairstreak|forest|crescent|5A4030 F4F0EA E8642A|u
Brown Hairstreak|hairstreak|forest birch|patch|5A3A20 2A1A0E F0A040|u
Black Hairstreak|hairstreak|forest|crescent|6A4A30 E8862A F4F0EA|r
Banded Hairstreak|hairstreak|forest|stripes|7A6A5A 2A2018 F4F0EA|c
Striped Hairstreak|hairstreak|forest birch|stripes|8A7A6A 2A2018 F4F0EA|u
Lesser Purple Emperor|classic|forest river|sheen|3A2A20 1E1A16 B07AF0|r
Poplar Admiral|classic|forest birch|band|2A2018 1E1A16 F4F0EA E8642A|r
Southern White Admiral|classic|forest|band|1E1A16 0E0A08 F4F0EA|u
Hungarian Glider|classic|forest|band|2A1E14 0E0A08 F4F0EA|u
Common Glider|classic|forest river|stripes|1E1A16 F4F0EA E8E0C0|c
Hackberry Emperor|classic|forest river|spotted|8A6A4A 3A2A1A F4F0EA|c
Tawny Emperor|classic|forest river|edge|C8803A 3A2A1A F0C070|c
Goatweed Leafwing|leaf|forest plains|gradient|D8602A F08A3A F0A040 3A1A0A|u
Eastern Comma|scalloped|forest river|speckle|D8822A 3A2210 F4E0B0|c
Grey Comma|scalloped|forest taiga|speckle|C87A3A 3A2A1A E8D0A0|u
Green Comma|scalloped|taiga|speckle|D8902A 2A1A0E 9AB86A|u
Compton Tortoiseshell|scalloped|taiga birch|edge|C87A2A 2A1A0E F4F0EA|r
Milbert's Tortoiseshell|scalloped|taiga mountains|band|3A2A1A 1E1A16 F0A040 E8642A|u
Large Tortoiseshell|scalloped|forest|edge|D8822A 2A1A0E 4A7AD8|r
Southern Festoon|classic|meadow forest|zebra|F2D84A 1E1A16 E83A2A|r
Spanish Festoon|classic|mesa meadow|zebra|F2C84A 1E1A16 E83A2A|r
Woodland Ringlet|rounded|forest taiga|ocelli|4A3A2A 2A1E14 E87A3A 1E1A16|c
Northern Pearly-eye|classic|forest|ocelli|9A8A6A 5A4A30 F4E8C0 1E1A16|c
Little Wood Satyr|rounded|forest|eyes|8A7050 5A4A30 F2D080 1E1A16|c
Woodland Brown|classic|forest roofed|ocelli|5A4030 2A1E14 F2D080 1E1A16|r
Scarce Heath|rounded|forest swamp|ocelli|9A7A50 5A4A30 F2D080 1E1A16|r
Freyer's Purple Emperor|classic|forest river|sheen|2A2018 1E1A16 9A6AF0|r
Nettle-tree Butterfly|leaf|forest mountains|speckle|8A5A30 3A2A1A E8A040|u
Woodland Grayling|classic|forest roofed|dusk|6A5A4A 3A2E24 F2E0B0 1E1A16|u
Eastern Pine Elfin|hairstreak|taiga|stripes|8A5A3A 3A2A1A E8C080|u
Henry's Elfin|hairstreak|forest|gradient|6A4A30 9A7050 F4F0EA 2A1E14|u
Juniper Hairstreak|hairstreak|taiga mesa|gradient|6A9A3A 9AC85A F4F0EA 3A2A1A|u
Early Hairstreak|hairstreak|birch forest|ocelli|8AA0A8 4A5A60 E8642A 1E1A16|r
Coral Hairstreak|rounded|forest meadow|crescent|8A7A6A E8642A F4F0EA|c
Edwards' Hairstreak|hairstreak|forest|crescent|8A7A6A E8862A 2A2018|u

# Blues & Coppers
Chalkhill Blue|rounded|meadow mountains|edge|9AC4E0 3A3A3A F4F2EA|u
Silver-studded Blue|rounded|meadow plains|basal|5A7AD8 2A2A3A F4F2EA|c
Small Blue|rounded|meadow|basal|6A6A70 7A9AE0 F4F2EA|c
Large Blue|rounded|meadow mountains|spotted|6A8AD8 2A3A5A 1E2A4A|r
Brown Argus|rounded|meadow plains|crescent|6A4A30 E8862A F4F2EA|c
Northern Brown Argus|rounded|mountains|ocelli|6A4A30 4A3020 F4F2EA 1E1A16|u
Mazarine Blue|rounded|meadow|gradient|4A6AC8 7A9AE8 F4F2EA 1E2A4A|u
Eastern Tailed-Blue|hairstreak|plains meadow|basal|6A7AE0 3A3A4A E8862A|c
Western Tailed-Blue|hairstreak|mountains forest|basal|8A9AE8 3A3A4A F4F2EA|u
Silvery Blue|rounded|meadow mountains|sheen|7A9AE8 2A3A5A D0E0FF|c
Cranberry Blue|rounded|swamp|basal|7A6AC0 3A2A4A F4F2EA|r
Long-tailed Blue|hairstreak|plains beach|sheen|8A7AD8 3A3A4A C8D0FF|u
Lang's Short-tailed Blue|hairstreak|beach plains|stripes|9A8AB8 5A4A6A F4F2EA|u
Turquoise Blue|rounded|meadow mountains|sheen|4AA8D8 1E4A6A B0F0FF|r
Zephyr Blue|rounded|mountains|edge|7AA0E8 2A2A3A F4F2EA|u
Idas Blue|rounded|taiga meadow|basal|6A8AD8 1E2A4A F4F2EA|u
Glandon Blue|rounded|mountains frozen|gradient|8AA0C0 C8D8E8 F4F2EA 3A4A5A|r
Purple-shot Copper|rounded|meadow|sheen|E07A2A 3A2A1A B07AF0|u
Scarce Copper|rounded|meadow mountains|edge|F0702A 3A1A0E F49A4A|u
Sooty Copper|rounded|meadow|speckle|5A4A3A 2A1E14 E8862A|c
Purple-edged Copper|rounded|swamp meadow|basal|E8862A 7A4AC0 3A1A0E|r
Lesser Fiery Copper|rounded|desert mesa|spotted|F0702A 3A1A0E 2A1A0E|u
Bronze Copper|rounded|swamp river|crescent|C8803A E8642A F4E0B0|u
Purplish Copper|rounded|mountains meadow|sheen|C8703A 3A1E14 C08AF0|c
American Copper|rounded|plains meadow|split|F0702A 6A6A70 F0702A|c
Tailed Copper|hairstreak|mountains forest|crescent|8A6A50 E8642A F4F0EA|u
Green-underside Blue|rounded|meadow|basal|7A9AE8 4A8A5A F4F2EA|u
Baton Blue|rounded|mesa meadow|stripes|7A9AE8 2A2A3A F4F2EA|u
Amanda's Blue|rounded|meadow|gradient|5A8AE8 8AB0F0 F4F2EA 2A2A3A|u
Summer Azure|rounded|forest meadow|gradient|9AB8F0 D0E0FF F4F2EA 3A3A4A|c

# Skippers
Small Skipper|skipper|meadow plains|edge|E88A2A 6A3A14 F0A040|c
Essex Skipper|skipper|meadow|edge|E8902A 3A2210 F0A040|c
Lulworth Skipper|skipper|beach meadow|crescent|C8902A F2C860 6A4A20|u
Grizzled Skipper|skipper|meadow|checker|3A3A3A F4F2EA F4F2EA|c
Mallow Skipper|skipper|plains|speckle|8A6A5A 4A3A30 C8B8A8|u
Common Sootywing|skipper|plains|spotted|2A2420 1A1612 F4F2EA|c
Hobomok Skipper|skipper|forest meadow|patch|E8902A 4A3018 F4B860|c
Peck's Skipper|skipper|plains meadow|spotted|6A4A2A 3A2A1A F0B040|c
Tawny-edged Skipper|skipper|meadow|edge|5A4A3A 2A2018 E8902A|c
Zabulon Skipper|skipper|forest|split|E8A030 6A4A2A F4D080|u
Sachem|skipper|plains savanna|marble|D8A040 6A4A20 F4E0A0|c
Ocola Skipper|skipper|swamp plains|spotted|7A6A50 4A3A28 F4F0DA|c
Hoary Edge|skipper|forest|patch|4A3A2A 2A2018 F4F0EA|u
Golden Banded-Skipper|skipper|forest river|band|5A4A30 2A2018 F2C840|r
Northern Cloudywing|skipper|plains forest|spotted|4A3A30 2A2018 F4F0DA|c
Wild Indigo Duskywing|skipper|meadow|dusk|4A3E34 2A2018 B0A090 1E1A16|c
Arctic Skipper|skipper|taiga frozen|checker|3A2A1A E8A040 F4D080|u
Mangrove Skipper|skipper|mangrove_swamp|sheen|2A2A3A 1A1A20 5A9AE8|r
Brazilian Skipper|skipper|swamp jungle|spotted|8A6A4A 4A3A2A F4F0DA|u
Guava Skipper|skipper|jungle|jewel|4A3A2A 6A8AD8 F2D84A 1E1A16|r

# Rainforest
Menelaus Blue Morpho|classic|jungle|sheen|2A8AF0 1E1A16 9AE0FF|r
Achilles Morpho|classic|jungle|band|1E1A16 0E0A08 3AA8F0|u
Cypris Morpho|classic|jungle|stripes|3A9AF0 1E2A5A F4F2EA|l
Rhetenor Morpho|classic|jungle|jewel|1A6AE8 1E1A16 7AE0FF 0E0A08|l
Peleides Morpho|classic|jungle bamboo|band|1E1A16 0E0A08 4AB0F0|c
Giant Owl|classic|jungle|ocelli|8A7050 4A3A28 F2D080 1E1A16|u
Forest Giant Owl|classic|jungle roofed|eyes|6A5A4A 3A2E24 E8C060 1E1A16|r
Cracker|classic|jungle|speckle|8A9AA8 2A2A30 F4F2EA|c
Blue Cracker|classic|jungle|speckle|3A6AC8 1E1A16 9AC8F0|u
Red Cracker|classic|jungle savanna|speckle|3A2A40 E83A3A 1E1A16|r
Mexican Bluewing|classic|jungle|band|1E1A16 0E0A08 4A9AF0|u
Common Banner|classic|jungle|band|1E1A16 0E0A08 E8642A|c
Red Rim|classic|jungle savanna|edge|1E1A16 0E0A08 E83A3A|u
Eighty-eight|rounded|jungle river|split|E83A3A 1E1A16 4A9AF0|r
Cramer's Eighty-eight|rounded|jungle|patch|1E1A16 0E0A08 E83A3A 4AD0F0|r
Rusty-tipped Page|pointed|jungle|tip|E87A2A 1E1A16 F4F0EA|c
Scarlet Peacock|classic|jungle|ocelli|8A2A1E 4A1A10 F4F0EA 1E1A16|u
White Peacock|classic|jungle swamp|ocelli|F4F0EA C8A890 E8902A 1E1A16|c
Banded Peacock|classic|jungle|band|1E1A16 0E0A08 E8864A|u
Pink-tipped Satyr|rounded|jungle roofed|glass|E0D8E0 6A5A60 F07AC0|r
Rusty Clearwing|longwing|jungle|glass|E8D0B0 6A3A1A E8862A|u
Tiger Clearwing|longwing|jungle|longwing|1E1A16 E8902A F2D84A|u
Hecale Longwing|longwing|jungle|longwing|E87A2A 1E1A16 F2D84A|c
Red Postman|longwing|jungle|longwing|1E1A16 0E0A08 E83A3A F2D84A|c
Cydno Longwing|longwing|jungle|longwing|1E1A16 0E0A08 F4F0EA|u
Blue-and-white Longwing|longwing|jungle|longwing|1E1A16 3A6AC8 F4F0EA|u
Melpomene Longwing|longwing|jungle|rays|1E1A16 E8642A F2D84A|u
Isabella's Longwing|longwing|jungle savanna|tiger|E8862A 1E1A16 F2D84A|c
Mechanitis Tigerwing|longwing|jungle|tiger|E8902A 1E1A16 F2E080|c
Clearwing Mimic|longwing|jungle|glass|D8E8F0 1E1A16 E8902A|u
Crimson Patch|rounded|jungle savanna|patch|1E1A16 0E0A08 E83A2A|c
Red Lacewing|classic|jungle|edge|E83A2A 1E1A16 F4F0EA|u
Cruiser|classic|jungle|gradient|E8862A F0A040 F4F0EA 2A1A0E|u
Clipper|classic|jungle bamboo|spotted|3A5A9A 1E1A16 F4F0EA|u
Blue Glassy Tiger|longwing|jungle|rays|9AC8E8 1E1A16 F4F0EA|c
Chestnut Tiger|longwing|jungle mountains|rays|8A3A1A 1E1A16 C8E0F0|u
Tree Nymph|longwing|jungle mangrove_swamp|spotted|F4F0EA 1E1A16 1E1A16|u
Common Crow|classic|jungle|spotted|3A2A20 1E1A16 F4F0EA|c
Striped Blue Crow|classic|jungle|sheen|2A2A40 1E1A16 5A8AF0|u
Autumn Leaf|leaf|jungle|gradient|E8862A F0B040 E8D080 3A1A0A|u
Orange Oakleaf|leaf|jungle bamboo|band|3A4A8A 1E1A16 F0902A|r
Common Sailer|rounded|jungle|stripes|1E1A16 F4F0EA F4F0EA|c
Archduke|classic|jungle|sheen|3A3A2A 1E1A16 7AE0C0|r
Common Lascar|rounded|jungle bamboo|stripes|1E1A16 E8902A E8902A|c
Malay Lacewing|classic|jungle|zebra|E8642A 1E1A16 F4F0EA|r
Green Imperial|hairstreak|jungle|gradient|3AA06A 6AD08A F4F0EA 1E1A16|r
Moonbeam|rounded|jungle|split|F4F0EA E8862A 1E1A16|u
Common Imperial|hairstreak|jungle|basal|1E1A16 4A9AE8 F4F0EA|u
Wallace's Golden Birdwing|birdwing|jungle|split|1E1A16 F2C83A 0E0A08|l
Cairns Birdwing|birdwing|jungle|split|1E1A16 3AD07A F2D84A|l

# Savanna & Desert
African Monarch|pointed|savanna desert|tiger|E8862A 1E1A16 F4F0EA|c
Gaudy Commodore|classic|savanna|ocelli|E83A2A 1E1A16 4A9AF0 1E1A16|u
Garden Commodore|classic|savanna|eyes|E8862A 3A2A1A 4A9AF0 1E1A16|c
African Leopard|classic|savanna|spotted|E8902A 2A1A0E 1E1A16|c
Foxy Charaxes|classic|savanna|gradient|C8602A E8902A F4F0DA 2A1A0E|u
Green-veined Charaxes|classic|savanna jungle|rays|E8E8C0 3A8A5A F4F0EA|r
Pearl Charaxes|classic|savanna|crescent|E8D0A0 E8642A F4F0EA|u
African Migrant|classic|savanna desert|edge|F4F0DA 6A6A4A F4F0DA|c
Scarlet Tip|pointed|savanna desert|tip|F4F0EA E83A2A F4F0EA|u
Purple Tip|pointed|savanna desert|tip|F4F0EA 9A4AC8 F4F0EA|r
Desert Orange Tip|classic|desert mesa|tip|F4F0EA E8862A F4F0EA|u
Sara Orangetip|classic|desert mountains|tip|F4F0EA E8642A 4A4A3A|c
Desert Black Swallowtail|swallowtail|desert mesa|band|1E1A16 0E0A08 F2D84A|u
Mormon Metalmark|rounded|desert mesa|spotted|2A2420 1E1A16 F4F0EA|c
Fatal Metalmark|rounded|desert mesa|checker|6A5A4A 2A2018 F4F0EA|u
Palmer's Metalmark|rounded|desert|spotted|C8803A 6A3A1A F4F0EA|u
Arizona Sister|classic|desert mesa|patch|3A2E24 1E1A16 E8902A|u
Empress Leilia|classic|desert|ocelli|B8803A 5A3A20 F4F0EA 1E1A16|u
Texan Crescent|rounded|desert|band|1E1A16 0E0A08 F4F0EA|c
Sandhill Skipper|skipper|desert mesa|edge|C8902A 6A4A20 F4D080|c
Leda Ministreak|hairstreak|desert mesa|crescent|9A9A90 E8642A F4F0EA|u
Great Purple Hairstreak|hairstreak|desert savanna|sheen|3A6AC8 1E1A16 7AD0F0|r
Marine Blue|rounded|desert mesa|stripes|8A7AD0 4A3A6A F4F0EA|c
Cassius Blue|rounded|savanna beach|stripes|9AB0E8 5A6A9A F4F0EA|c
Atala|rounded|beach savanna|jewel|1E1A16 4A6AD8 E8642A 0E0A08|r

# Mountains & Tundra
Small Apollo|rounded|mountains frozen|spotted|F4F2EA 3A3A3A E83A2A|r
Clouded Apollo|rounded|mountains meadow|spotted|F4F2EA 3A3A3A 1E1A16|u
Phoebus Apollo|rounded|mountains|eyes|F4F2EA 3A3A3A E83A2A 1E1A16|r
Mountain Ringlet|rounded|mountains grove|ocelli|4A3A2A 2A1E14 E8862A 1E1A16|u
Scotch Argus|rounded|mountains meadow|ocelli|4A2A1E 2A1A10 E8642A 1E1A16|c
Arran Brown|rounded|mountains|ocelli|5A3A24 2A1A10 E8862A 1E1A16|r
Mountain Fritillary|rounded|mountains frozen|checker|E8902A 2A1A0E F4F0EA|u
Arctic Fritillary|rounded|frozen grove|checker|E8902A 2A1A0E C8D8E0|u
Freija Fritillary|rounded|frozen taiga|edge|D8862A 2A1A0E F4F0EA|u
Polaris Fritillary|rounded|frozen|crescent|E8902A 2A1A0E F4F0EA|r
Arctic Blue|rounded|frozen mountains|gradient|8AA0C8 C0D0E8 F4F2EA 3A4A5A|u
Arctic Ringlet|rounded|frozen grove|eyes|5A4A3A 3A2E24 E8902A 1E1A16|u
Melissa Arctic|classic|mountains frozen|speckle|B8A890 6A5A4A F4F0EA|u
Chryxus Arctic|classic|mountains taiga|eyes|C8904A 6A4A2A F4F0EA 1E1A16|u
Polixenes Arctic|classic|frozen|speckle|C8C0B0 8A8070 F4F2EA|r
Labrador Sulphur|classic|frozen taiga|edge|E8F0A0 4A5A3A F4F2EA|u
Hecla Sulphur|classic|frozen|edge|E8B840 4A3A1A F4F2EA|r
Pale Arctic Clouded Yellow|classic|frozen mountains|tip|F4F0C0 5A5A3A F4F2EA|r
Mountain Clouded Yellow|classic|mountains|gradient|F0E070 F8F0B0 E8862A 4A4A2A|u
Glacial Apollo|rounded|frozen mountains|glass|F4F2EA 6A6A70 E0E8F0|l
Alpine Grizzled Skipper|skipper|mountains grove|checker|4A4A4A F4F2EA F4F2EA|u
Mountain Alcon Blue|rounded|mountains meadow|spotted|7A9AE8 2A3A5A 1E2A4A|r
Shepherd's Fritillary|rounded|mountains grove|checker|E8A040 4A2A10 F4E0B0|u
Bog Fritillary|rounded|swamp taiga|checker|E8902A 3A2210 F2D8A0|u
Old Growth Ringlet|rounded|mega taiga|ocelli|3A2A1E 1E1610 E8A040 1E1A16|u

# Wetlands & Coasts
Mangrove Buckeye|rounded|mangrove_swamp beach|eyes|6A4A30 3A2A1A E8862A 1E1A16|c
Great Southern White|classic|beach mangrove_swamp|tip|F4F2EA 2A2A2A 7AE0E8|c
Florida White|classic|mangrove_swamp|tip|F4F2EA 6A6A60 F4F2EA|u
Swamp Metalmark|rounded|swamp|checker|E8762A 3A2A1A 9AA0A8|r
Georgia Satyr|rounded|swamp|ocelli|9A7A50 5A4A30 F2D080 1E1A16|u
Appalachian Brown|classic|swamp forest|ocelli|8A6A4A 4A3A28 F2D080 1E1A16|u
Dion Skipper|skipper|swamp river|band|C8862A 4A3018 F2C860|u
Broad-winged Skipper|skipper|swamp river|edge|7A5A3A 3A2A1A E8A040|u
Aaron's Skipper|skipper|beach swamp|edge|9A7A5A 4A3A2A E8B040|u
Saltmarsh Skipper|skipper|beach|speckle|B89A70 6A5030 F4F0DA|c
Mangrove Tree Nymph|longwing|mangrove_swamp|spotted|F4F2EA 1E1A16 1E1A16|r
Statira Sulphur|classic|beach mangrove_swamp|split|F4E870 C8B840 F4F2EA|u
Large Orange Sulphur|classic|beach plains|gradient|F09A2A F4C04A F4F2EA 6A3A14|c
Dina Yellow|rounded|beach river|tip|F4C84A 3A2A1A F4F2EA|u
Eastern Pygmy Blue|rounded|beach mangrove_swamp|basal|8A6A4A 5A7AD0 F4F2EA|c
Cuban Crescent|rounded|mangrove_swamp|band|1E1A16 0E0A08 E8902A|r
Ruddy Daggerwing|leaf|mangrove_swamp jungle|stripes|E8762A 3A1A0A F4A040|u
Many-banded Daggerwing|leaf|jungle river|stripes|E89A3A 1E1A16 F4F0EA|u
Martial Scrub-Hairstreak|hairstreak|beach|crescent|7A8A90 E8642A F4F0EA|u
Marsh Ringlet|rounded|swamp river|gradient|C8A060 E8C880 F4F0EA 5A4A30|c
Reedbed Skipper|skipper|river swamp|marble|C8A060 6A5030 F4E0A0|c
Bog Copper|rounded|swamp|crescent|8A7A90 E8642A F4F0EA|u
Bay Checkerspot|rounded|beach meadow|checker|2A1A12 E8642A F4F0DA|r
Tidewater Admiral|classic|beach river|band|1E1A16 0E0A08 E83A2A F4F0EA|u
Coastal Lady|classic|beach plains|edge|E8862A 1E1A16 F4F0EA|c

# Wonders of the World
Pale Garden Ghost|longwing|pale_garden|glass|E8E8E4 6A6A68 F4F4F0|r
Creaking Wing|leaf|pale_garden|eyes|8A8A84 3A3A38 F2A040 1E1A16|r
Eyeblossom|rounded|pale_garden|patch|5A5A58 2A2A28 F2A040|u
Pale Moss Flutter|classic|pale_garden|speckle|C8CCC0 7A7E74 F4F4F0|u
Dripstone Duskwing|skipper|lush_caves|speckle|8A6A50 4A3A2A C8A880|u
Spore Blossom|rounded|lush_caves|patch|3A6A2A 1E3A14 F07AB8|u
Moss Carpet|classic|lush_caves|speckle|5A8A2A 3A5A18 8AC04A|c
Geode Glimmer|classic|lush_caves deep_dark|jewel|6A3AA8 2A1A4A E0C2FF 1A0E2A|r
Warden's Shadow|longwing|deep_dark|rays|0E1A20 2ADFE0 0A2A30|l
Sculk Shrieker Wing|classic|deep_dark|crescent|0E2A30 2ADFE0 E8F0D0|r
Copper Patina|rounded|mountains river|gradient|C8703A 4AB89A E8A070 3A2A1A|u
Redstone Flicker|pointed|mesa desert|flame|8A1A1A E83A2A F87A4A 2A0A0A|r
Lapis Courier|classic|mountains|speckle|2A4AB8 F2D84A 1A2A6A|u
Emerald Trader|swallowtail|mountains plains|jewel|1E6A3A 2A1E12 6AF0A0 0E0A08|r
Honeycomb Wing|classic|flower_forest plains|checker|F2B42A 8A5A14 F8D86A|u
Torchflower Flame|pointed|plains flower_forest|flame|E8642A F2B42A F8E08A 3A1A0A|r
Pitcher Plant Swallowtail|swallowtail|flower_forest swamp|gradient|4A8AB0 7AC0E0 E8A0D0 1E2A3A|r
Sniffer's Friend|classic|flower_forest meadow|marble|E8D8B0 6A8A3A E8642A|u
Mossy Cobble Skipper|skipper|forest lush_caves|speckle|7A7A70 4A6A2A A8A8A0|c
Bamboo Panda Wing|classic|bamboo|split|F4F2EA 1E1A16 1E1A16|u

# The Nether
Blaze Monarch|pointed|nether_wastes basalt_deltas|tiger|E8761C 2A0A0A F8D84A|u
Magma Swallowtail|swallowtail|basalt_deltas|flame|2A1A1A E8642A F8B43A 0E0A08|r
Soulfire Wisp|longwing|soulsand_valley|rays|0E1A20 4AE0F0 9AF8FF|r
Ghast Tear|rounded|soulsand_valley nether_wastes|glass|F4F2EA 8A8A8A C8E8F0|u
Wither Rose Wing|classic|soulsand_valley|patch|1A1612 0E0A08 6A1A2A|r
Shroomlight Glow|rounded|crimson_forest warped_forest|spotted|8A2A1A 3A0E0A F8B43A|c
Weeping Vine Flutter|longwing|crimson_forest|longwing|5A0E14 2A0608 E83A3A F87A4A|c
Twisting Vine Flutter|longwing|warped_forest|longwing|0E4A4A 062A2A 2AD0B0 6AF0E0|c
Netherrack Skipper|skipper|nether_wastes|speckle|6A2A24 3A0E0A A84A3A|c
Quartz Admiral|classic|nether_wastes|band|5A1A1A 2A0A0A F4F0EA|u
Gilded Piglin Wing|classic|crimson_forest nether_wastes|edge|E8B42A 5A3A0A F8E08A|u
Hoglin Hide|scalloped|crimson_forest|marble|A85A4A 5A2A1A E8A080|c
Strider Swallowtail|swallowtail|nether_wastes basalt_deltas|stripes|8A2A3A 4A0E1A E8A0A0|u
Basalt Duskwing|skipper|basalt_deltas|checker|3A3A40 1A1A20 8A8A90|c
Blackstone Gilded|classic|basalt_deltas|jewel|2A2428 1A1418 E8B42A 0E0A0E|r
Ancient Debris Wing|classic|basalt_deltas soulsand_valley|ocelli|5A3A30 3A2420 C8A890 1E1410|l
Netherite Emperor|classic|basalt_deltas|sheen|3A3438 1E1A1E 8A7A90|l
Crimson Nylium|classic|crimson_forest|speckle|8A1A1A E8642A 3A0A0A|c
Warped Nylium|classic|warped_forest|speckle|1A5A5A 3AD0B0 0E2A2A|c
Warped Fungus Wing|rounded|warped_forest|patch|1A6A6A 0E3A3A F08A3A|u
Crimson Fungus Wing|rounded|crimson_forest|patch|8A1A1A 3A0A0A F2D84A|u
Nether Wart Flutter|rounded|crimson_forest soulsand_valley|spotted|6A0E14 2A0608 E83A3A|c
Soul Lantern|classic|soulsand_valley|eyes|2A2420 1A1612 4AE0F0 0E1A20|u
Soul Sand Skipper|skipper|soulsand_valley|marble|6A5040 3A2A20 9AE0F0|c
Lava Lacewing|classic|nether_wastes basalt_deltas|zebra|E8642A 2A0A0A F8D84A|u
Ember Tail|kite|nether_wastes|flame|3A0E0A E83A1A F8B43A 1A0604|r
Fire Charge|rounded|nether_wastes|basal|2A1A14 E8642A F8D84A|u
Bastion Banner|classic|basalt_deltas nether_wastes|checker|2A2428 E8B42A F8E08A|r
Glowstone Sulphur|classic|nether_wastes soulsand_valley|edge|F8D84A 8A5A14 FFF0A0|u
Magma Cream|rounded|basalt_deltas|gradient|E8642A F8B43A F8E08A 3A0E0A|c
Wither Skeleton Skipper|skipper|soulsand_valley nether_wastes|spotted|2A2A2A 141414 6A6A6A|u
Piglin Brute|scalloped|basalt_deltas crimson_forest|band|5A3A20 2A1A0A E8B42A F4F0EA|r
Infernal Morpho|classic|nether_wastes crimson_forest|sheen|8A0E0E 2A0606 F87A4A|r
Smoldering Leafwing|leaf|crimson_forest nether_wastes|gradient|5A1A0E E8642A F8B43A 1A0604|u
Cinder Hairstreak|hairstreak|basalt_deltas|crescent|4A4448 E8642A F8D84A|c
Ash Ringlet|rounded|basalt_deltas soulsand_valley|ocelli|6A6468 3A3438 E8642A 1A1418|c
Soulflame Birdwing|birdwing|soulsand_valley|split|1A1612 2AC8E0 9AF8FF|l
Hellfire Birdwing|birdwing|nether_wastes crimson_forest|split|1A0E0A E8641A F8D84A|l
Crying Obsidian Wing|longwing|crimson_forest soulsand_valley|dusk|2A1240 140828 B05AF0 0A0414|r
Warped Wart Flutter|rounded|warped_forest|basal|1A6A6A 3AF0D0 0E2A2A|c
Zoglin Scourge|scalloped|crimson_forest|rays|8A3A3A 2A0A0A E8A080|u
Nether Brick Wing|classic|nether_wastes|checker|4A1A1E 2A0A0E 8A3A3A|c
Nether Gold Flake|rounded|nether_wastes|speckle|6A2A24 E8B42A 3A0E0A|u
Crimson Kite|kite|crimson_forest|band|3A0A0E 1A0406 E83A3A F87A4A|u
Warped Kite|kite|warped_forest|band|0E2A3A 061A20 2AD0B0 E86AC0|u
Respawn Anchor|classic|nether_wastes soulsand_valley|eyes|1E1430 0E0A1A F87AF0 4A0A6A|r
Fiery Fritillary|classic|nether_wastes|checker|E8642A 3A0A0A F8D84A|c
Soul Torch Swallowtail|swallowtail|soulsand_valley|edge|2A2420 1A1612 4AE0F0|u
Ghastling Glider|classic|soulsand_valley nether_wastes|gradient|F4F2EA D8E8F0 E8642A 6A6A6A|u
Magmaback Skipper|skipper|basalt_deltas nether_wastes|flame|2A1A1A E8642A F8B43A 0E0A08|c

# The End
Chorus Flutter|rounded|the_end|speckle|B07AC8 6A3A8A E8C8F0|c
Chorus Bloom Swallowtail|swallowtail|the_end|gradient|8A5AA8 C8A0E0 F4E0FF 2A1438|u
End Stone Skipper|skipper|the_end|speckle|E8E4B0 B8B080 F4F0D0|c
Purpur Admiral|classic|the_end|band|2A1438 140A1E C88AE0 F4E0FF|u
Shulker Shell|rounded|the_end|basal|9A6AA8 6A3A7A F2E8C0|u
Shulker Glimmer|classic|the_end|sheen|8A5A9A 3A1E4A F2C8FF|r
Void Drifter|longwing|the_end|glass|101018 2A2A40 7AE0E8|r
Dragon's Breath|pointed|the_end|flame|2A0E30 C83AA8 F87AE0 0E0414|r
Ender Dragon Wing|birdwing|the_end|jewel|141018 0A080C D04AF0 050407|l
Elytra Glider|leaf|the_end|gradient|7A7A90 A8A8C0 D0D0E8 3A3A4A|l
Endermite Skipper|skipper|the_end|spotted|3A2A4A 1E1428 C88AE0|c
Ender Pearl|rounded|the_end|eyes|1A3A3A 0E1E1E 2AA88A 0E3A30|u
Eye of Ender|classic|the_end|eyes|2A1A3A 140A1E 4AE0A0 0E2A1E|r
End Gateway|classic|the_end|speckle|0A0A14 F4F0FF 1A1A2E|r
End Rod Glow|longwing|the_end|edge|F4F0EA C8C0E0 FFFFFF|u
Purpur Pillar|classic|the_end|stripes|A87AB8 6A3A8A E8C8F0|c
Chorus Fruit|rounded|the_end|patch|7A4A9A 3A1E4A E8A0F0|c
Popped Chorus|classic|the_end|checker|C8A0D8 6A3A8A F4E0FF|u
End City Banner|swallowtail|the_end|zebra|E8E4B0 6A3A8A F4F0D0|u
Starfield Morpho|classic|the_end|speckle|1A1438 F4F0FF 0A0820|r
Outer Islands Kite|kite|the_end|gradient|3A2A5A 8A6AC8 E0C8FF 140A1E|u
Amethyst Void|classic|the_end|jewel|3A1E5A 140A1E C88AF0 0A0414|r
Levitation Wing|rounded|the_end|glass|E8E0F0 8A6AA8 F4F0FF|u
Dragon Egg|scalloped|the_end|speckle|141018 B03AD8 0A080C|l
Obsidian Pillar|classic|the_end|rays|1A1028 3A2A5A 8A5AC8|c
Crystal Flame|pointed|the_end|eyes|E8A0F0 6A3A8A F4F0FF 3A1E4A|r
End Highlands Ringlet|rounded|the_end|ocelli|C8C090 8A8460 9A5AC8 2A1438|c
Midnight Purpur Hairstreak|hairstreak|the_end|crescent|2A1E3A C88AE0 F4F0D0|c
Ender Blink|classic|the_end|spotted|1A1A2A 0E0E18 C88AF0|c
Shulker Bullet|rounded|the_end|edge|F4F0D0 9A6AA8 FFFFFF|c
Void Swallowtail|swallowtail|the_end|dusk|141020 0A0814 5AE0E8 050408|r
Chorus Stem Skipper|skipper|the_end|stripes|9A7AA8 5A3A6A D8C0E8|c
Dragonfire Birdwing|birdwing|the_end|flame|1A0A20 B03AD8 F07AF0 0A040E|l
Eclipse Wing|classic|the_end|gradient|0A0814 3A2A5A F4F0D0 050408|u
Astral Lacewing|classic|the_end|zebra|1E1438 9A6AF0 F4F0FF|u
Comet Tail|kite|the_end|glass|E0E8F0 3A3A5A 7AE0E8|r
Nebula Admiral|classic|the_end|longwing|1A1438 0A0820 E86AC0 7AE0E8|r
Pale End Sulphur|classic|the_end|tip|F2EEC0 6A3A8A F4F0D0|c
End Stone Brick|rounded|the_end|checker|E8E4B0 9A9468 F4F0D0|c
Purpur Slab Skipper|skipper|the_end|edge|A87AB8 4A2A5A E8C8F0|c
Teleporting Tiger|longwing|the_end|tiger|8A4AC8 140A1E E0C8FF|u
Ender Chest Wing|classic|the_end|basal|1A2A2A 2AA88A 0E1414|u
Voidglass|longwing|the_end|rays|0A1418 2AD0D0 9AF0F0|r
Twilight Crescent|rounded|the_end|crescent|3A2A5A E8A0F0 F4F0FF|c
Starlight Skipper|skipper|the_end|speckle|1A1438 F4F0D0 0A0820|u
Lunar Swallowtail|swallowtail|the_end|split|E8E4F0 8A7AC8 F4F0FF|u
Galactic Peacock|classic|the_end|ocelli|2A1438 140A1E 7AE0E8 E86AC0|r
Indigo Shulker|rounded|the_end|sheen|3A3A8A 1E1E4A 9AA0F0|u
Elder End Wing|birdwing|the_end|ocelli|2A2438 141020 C8C090 0A080E|r
Dragonhead Emperor|scalloped|the_end|band|1A1018 0A080C B03AD8 F4F0D0|r
"""


def rows():
    section = None
    for raw in TABLE.strip().splitlines():
        raw = raw.strip()
        if not raw:
            continue
        if raw.startswith("#"):
            section = raw[1:].strip()
            continue
        name, shape, habitats, pattern, colours, rarity = [f.strip() for f in raw.split("|")]
        yield section, name, shape, habitats.split(), pattern, ["#" + c for c in colours.split()], rarity
