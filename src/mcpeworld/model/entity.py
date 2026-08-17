from dataclasses import dataclass, field
from typing import Optional

from mcpeworld import Bool, Bytes, Float, Int, Str


@dataclass
class EntityVectorPos:

    x:Float = 0.0
    y:Float = 0.0
    z:Float = 0.0

    def __repr__( self ) -> Str:
        return f"({self.x:.1f}, {self.y:.1f}, {self.z:.1f})"


@dataclass
class EntityItem:

    chunkKey:Bytes = field( default_factory=bytes )
    identifier:Str = ""
    position:EntityVectorPos = field( default_factory=EntityVectorPos )
    uniqueId:Str = ""
    customName:Str = ""
    health:Float = 0.0
    maxHealth:Float = 0.0
    isBaby:Bool = False
    isTamed:Bool = False
    variant:Int = -1
    color:Int = -1
    nbtData:Optional[object] = None

    @property
    def shortId( self ) -> Str:
        if self.identifier.startswith( "minecraft:" ):
            return self.identifier[10:]
        return self.identifier

    @property
    def displayName( self ) -> Str:
        if self.customName:
            return f"{self.customName} ({self.identifier})"
        return self.identifier

    def __repr__( self ) -> Str:
        return f"EntityItem({self.identifier} at {self.position})"
