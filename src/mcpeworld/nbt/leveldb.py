from pathlib import Path
from typing import Generator, MutableSequence, Optional, Tuple

import amulet_nbt
import leveldb as amuletLevelDb

from mcpeworld import Bytes, Int, Str
from mcpeworld.constant import (
    ChunkTypeEntity,
    ChunkTypeEntityLegacy,
    ChunkTypeTileEntity,
    PlayerDataKey,
)


class BedrockLevelDb:

    def __init__( self, dbPath:Path ) -> None:
        self.dbPath = dbPath
        self.db:Optional[amuletLevelDb.LevelDB] = None

    def open( self ) -> None:
        self.db = amuletLevelDb.LevelDB( str( self.dbPath ) )

    def close( self ) -> None:
        if self.db is not None:
            self.db.close()
            self.db = None

    def __enter__( self ) -> "BedrockLevelDb":
        self.open()
        return self

    def __exit__( self, excType, excVal, excTb ) -> None:
        self.close()

    def get( self, key:Bytes ) -> Optional[Bytes]:
        if self.db is None:
            return None
        try:
            return self.db.get( key )
        except KeyError:
            return None

    def put( self, key:Bytes, value:Bytes ) -> None:
        if self.db is None:
            return
        self.db.put( key, value )

    def delete( self, key:Bytes ) -> None:
        if self.db is None:
            return
        self.db.delete( key )

    def keys( self ) -> Generator[Bytes, None, None]:
        if self.db is None:
            return
        for key in self.db.keys():
            yield key

    def readPlayerNbt( self ) -> Optional[amulet_nbt.NamedTag]:
        rawData = self.get( PlayerDataKey )
        if rawData is None:
            return None
        return amulet_nbt.load(
            rawData,
            compressed=False,
            little_endian=True,
            string_decoder=amulet_nbt.utf8_decoder
        )

    def writePlayerNbt( self, namedTag:amulet_nbt.NamedTag ) -> None:
        nbtBytes = namedTag.to_nbt(
            compressed=False,
            little_endian=True,
            string_encoder=amulet_nbt.utf8_encoder
        )
        self.put( PlayerDataKey, nbtBytes )

    def iterateChunkKeys( self, chunkType:Int ) -> Generator[Tuple[Bytes, Bytes], None, None]:
        if self.db is None:
            return
        for key in self.db.keys():
            keyLen = len( key )
            if keyLen >= 9 and key[8] == chunkType:
                rawData = self.get( key )
                if rawData is not None:
                    yield key, rawData
            elif keyLen >= 13 and key[12] == chunkType:
                rawData = self.get( key )
                if rawData is not None:
                    yield key, rawData

    def iterateEntities( self ) -> Generator[Tuple[Bytes, Bytes], None, None]:
        yield from self.iterateChunkKeys( ChunkTypeEntity )
        yield from self.iterateChunkKeys( ChunkTypeEntityLegacy )

    def iterateTileEntities( self ) -> Generator[Tuple[Bytes, Bytes], None, None]:
        yield from self.iterateChunkKeys( ChunkTypeTileEntity )
