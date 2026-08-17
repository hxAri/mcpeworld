from dataclasses import dataclass, field
from typing import Any, MutableMapping, Optional

from mcpeworld import Bytes, Float, Int, Str
from mcpeworld.model.entity import EntityVectorPos


@dataclass
class TileEntityItem:

    chunkKey:Bytes = field( default_factory=bytes )
    tileIdentifier:Str = ""
    position:EntityVectorPos = field( default_factory=EntityVectorPos )
    overlayData:Str = ""
    distanceToPlayer:Float = 0.0
    nbtData:Optional[object] = None
    entityData:MutableMapping[Str, Any] = field( default_factory=dict )

    @property
    def displayName( self ) -> Str:
        if self.tileIdentifier:
            return self.tileIdentifier
        return "Undefined Tile"

    def __repr__( self ) -> Str:
        return f"TileEntityItem({self.tileIdentifier} at {self.position})"
