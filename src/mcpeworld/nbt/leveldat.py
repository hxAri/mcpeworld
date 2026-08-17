import struct
from pathlib import Path
from typing import Tuple

import amulet_nbt

from mcpeworld import Bytes, Int, Str


LevelDatVersionTag:Bytes = b"\x08\x00\x00\x00"
LevelDatHeaderSize:Int = 8


def readLevelDat( filePath:Path ) -> amulet_nbt.NamedTag:
    rawData = filePath.read_bytes()
    nbtData = rawData[LevelDatHeaderSize:]
    namedTag = amulet_nbt.load(
        nbtData,
        compressed=False,
        little_endian=True,
        string_decoder=amulet_nbt.utf8_decoder
    )
    return namedTag


def writeLevelDat( filePath:Path, namedTag:amulet_nbt.NamedTag ) -> None:
    nbtBytes = namedTag.to_nbt(
        compressed=False,
        little_endian=True,
        string_encoder=amulet_nbt.utf8_encoder
    )
    sizeBytes = struct.pack( "<I", len( nbtBytes ) )
    filePath.write_bytes( LevelDatVersionTag + sizeBytes + nbtBytes )
