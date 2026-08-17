from dataclasses import dataclass, field
from typing import MutableMapping, MutableSequence

from mcpeworld import Bool, Int, Str


@dataclass
class Ench:

    enchantId:Int
    level:Int = 1

    def __repr__( self ) -> Str:
        return f"Ench(id={self.enchantId}, level={self.level})"


@dataclass
class ActiveEffect:

    effectId:Int
    amplifier:Int = 0
    duration:Int = 600
    ambient:Bool = False
    showParticles:Bool = True

    def __repr__( self ) -> Str:
        return f"ActiveEffect(id={self.effectId}, amp={self.amplifier}, dur={self.duration})"


@dataclass
class BEGameItem:

    itemName:Str = ""
    stackSize:Int = 1
    displayName:Str = ""
    damage:Int = -1
    states:MutableMapping[Str, Str] = field( default_factory=dict )
    tags:MutableMapping[Str, Str] = field( default_factory=dict )
    enchantments:MutableSequence[Ench] = field( default_factory=list )
    belongsTo:Str = "minecraft"
    iconName:Str = ""
    slot:Int = -1
    trimMaterial:Str = ""
    trimPattern:Str = ""

    def __post_init__( self ) -> None:
        if ":" in self.itemName:
            parts = self.itemName.split( ":", 1 )
            self.belongsTo = parts[0]
            self.itemName = parts[1]
        if not self.iconName:
            self.iconName = self.itemName

    @property
    def isEmpty( self ) -> bool:
        return not self.itemName or self.itemName == "null" or self.itemName == "empty"

    @property
    def fullIdentifier( self ) -> Str:
        return f"{self.belongsTo}:{self.itemName}"

    def __repr__( self ) -> Str:
        return f"BEGameItem({self.fullIdentifier}, x{self.stackSize})"
