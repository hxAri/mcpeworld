from typing import MutableMapping, MutableSequence, Tuple

import amulet_nbt

from mcpeworld import Int, Str

BannerColors:MutableMapping[Int, Str] = {
    0: "White",
    1: "Orange",
    2: "Magenta",
    3: "Light Blue",
    4: "Yellow",
    5: "Lime",
    6: "Pink",
    7: "Gray",
    8: "Light Gray",
    9: "Cyan",
    10: "Purple",
    11: "Blue",
    12: "Brown",
    13: "Green",
    14: "Red",
    15: "Black",
}

BannerPatterns: MutableMapping[Str, Str] = {
    "bs": "Bottom Stripe",
    "ts": "Top Stripe",
    "ls": "Left Stripe",
    "rs": "Right Stripe",
    "cs": "Center Stripe (Vertical)",
    "ms": "Middle Stripe (Horizontal)",
    "drs": "Down Right Stripe",
    "dls": "Down Left Stripe",
    "ss": "Small (Vertical) Stripes",
    "cr": "Diagonal Cross",
    "sc": "Square Cross",
    "ld": "Left of Diagonal",
    "rud": "Right of Upside-Down Diagonal",
    "lud": "Left of Upside-Down Diagonal",
    "rd": "Right of Diagonal",
    "vh": "Vertical Half (Left)",
    "vhr": "Vertical Half (Right)",
    "hh": "Horizontal Half (Top)",
    "hhb": "Horizontal Half (Bottom)",
    "bl": "Bottom Left Corner",
    "br": "Bottom Right Corner",
    "tl": "Top Left Corner",
    "tr": "Top Right Corner",
    "bt": "Bottom Triangle",
    "tt": "Top Triangle",
    "bts": "Bottom Triangle Sawtooth",
    "tts": "Top Triangle Sawtooth",
    "mc": "Middle Circle",
    "mr": "Middle Rhombus",
    "bo": "Border",
    "cbo": "Curly Border",
    "bri": "Brick",
    "gra": "Gradient",
    "gru": "Gradient Upside-Down",
    "cre": "Creeper",
    "sku": "Skull",
    "flo": "Flower",
    "moj": "Mojang",
    "glb": "Globe",
    "pig": "Piglin",
    "flw": "Flow",
    "gus": "Guster",
}


def loadBannerPatterns( compound:amulet_nbt.CompoundTag ) -> MutableSequence[Tuple[Str, Int]]:
    patterns:MutableSequence[Tuple[Str, Int]] = []
    if "Patterns" not in compound:
        return patterns
    patternList = compound["Patterns"]
    if not isinstance( patternList, amulet_nbt.ListTag ):
        return patterns
    for entry in patternList:
        if isinstance( entry, amulet_nbt.CompoundTag ):
            pattern = entry.get( "Pattern", amulet_nbt.StringTag( "" ) ).py_str
            color = int( entry.get( "Color", amulet_nbt.IntTag( 0 ) ) )
            patterns.append( ( pattern, color ) )
    return patterns


def saveBannerPatterns(
    compound:amulet_nbt.CompoundTag,
    baseColor:Int,
    patterns:MutableSequence[Tuple[Str, Int]]
) -> None:
    compound["Base"] = amulet_nbt.IntTag( baseColor )
    patternList = amulet_nbt.ListTag()
    for patternCode, color in patterns:
        entry = amulet_nbt.CompoundTag()
        entry["Pattern"] = amulet_nbt.StringTag( patternCode )
        entry["Color"] = amulet_nbt.IntTag( color )
        patternList.append( entry )
    compound["Patterns"] = patternList


def getBannerBaseColor( compound:amulet_nbt.CompoundTag ) -> Int:
    return int( compound.get( "Base", amulet_nbt.IntTag( 0 ) ) )
