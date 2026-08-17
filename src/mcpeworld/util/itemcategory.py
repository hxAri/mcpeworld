from typing import MutableMapping, MutableSequence, Set

from mcpeworld import Int, Str

ItemCategory = Str

Sword: ItemCategory = "sword"
Axe: ItemCategory = "axe"
Pickaxe: ItemCategory = "pickaxe"
Shovel: ItemCategory = "shovel"
Hoe: ItemCategory = "hoe"
Bow: ItemCategory = "bow"
Crossbow: ItemCategory = "crossbow"
Trident: ItemCategory = "trident"
FishingRod: ItemCategory = "fishing_rod"
Helmet: ItemCategory = "helmet"
Chestplate: ItemCategory = "chestplate"
Leggings: ItemCategory = "leggings"
Boots: ItemCategory = "boots"
Shears: ItemCategory = "shears"
Shield: ItemCategory = "shield"
Mace: ItemCategory = "mace"
Elytra: ItemCategory = "elytra"
Unknown: ItemCategory = "unknown"

AllEquipment: Set[Str] = {
    Sword, Axe, Pickaxe, Shovel, Hoe, Bow, Crossbow, Trident,
    FishingRod, Helmet, Chestplate, Leggings, Boots, Shears,
    Shield, Mace, Elytra,
}

AllArmor: Set[Str] = { Helmet, Chestplate, Leggings, Boots }

AllTools: Set[Str] = { Pickaxe, Shovel, Axe, Hoe }

AllMelee: Set[Str] = { Sword, Axe, Pickaxe, Shovel, Hoe }

EnchantmentApplicability: MutableMapping[Int, Set[Str]] = {
    0: AllArmor,
    1: AllArmor,
    2: { Boots },
    3: AllArmor,
    4: AllArmor,
    5: AllArmor,
    6: { Helmet },
    7: { Boots },
    8: { Helmet },
    9: AllMelee,
    10: AllMelee,
    11: AllMelee,
    12: AllMelee,
    13: AllMelee,
    14: AllMelee,
    15: AllTools | { Shears },
    16: AllTools,
    17: AllEquipment,
    18: AllTools,
    19: { Bow },
    20: { Bow },
    21: { Bow },
    22: { Bow },
    23: { FishingRod },
    24: { FishingRod },
    25: { Boots },
    26: AllEquipment,
    27: AllArmor | { Elytra },
    28: AllEquipment,
    29: { Trident },
    30: { Trident },
    31: { Trident },
    32: { Trident },
    33: { Crossbow },
    34: { Crossbow },
    35: { Crossbow },
    36: { Boots },
    37: { Leggings },
    38: { Mace },
    39: { Mace },
    40: { Mace },
}


def detectItemCategory( itemName: Str ) -> Str:
    name = itemName.lower().removeprefix( "minecraft:" )
    if name.endswith( "_sword" ) or name == "sword":
        return Sword
    if name.endswith( "_axe" ) or name == "axe":
        return Axe
    if name.endswith( "_pickaxe" ) or name == "pickaxe":
        return Pickaxe
    if name.endswith( "_shovel" ) or name == "shovel":
        return Shovel
    if name.endswith( "_hoe" ) or name == "hoe":
        return Hoe
    if name.endswith( "_helmet" ) or name in ( "helmet", "turtle_helmet" ):
        return Helmet
    if name.endswith( "_chestplate" ) or name == "chestplate":
        return Chestplate
    if name.endswith( "_leggings" ) or name == "leggings":
        return Leggings
    if name.endswith( "_boots" ) or name == "boots":
        return Boots
    if name == "bow":
        return Bow
    if name == "crossbow":
        return Crossbow
    if name == "trident":
        return Trident
    if name == "fishing_rod":
        return FishingRod
    if name == "shears":
        return Shears
    if name == "shield":
        return Shield
    if name == "mace":
        return Mace
    if name == "elytra":
        return Elytra
    return Unknown


def getApplicableEnchantments( itemName: Str ) -> MutableSequence[Int]:
    category = detectItemCategory( itemName )
    if category == Unknown:
        return list( EnchantmentApplicability.keys() )
    result: MutableSequence[Int] = []
    for enchId, categories in EnchantmentApplicability.items():
        if category in categories:
            result.append( enchId )
    return result
