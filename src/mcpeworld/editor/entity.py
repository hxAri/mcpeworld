from typing import MutableSequence, Optional, Tuple

import amulet_nbt

from mcpeworld import Bool, Bytes, Float, Int, Str
from mcpeworld.model.entity import EntityItem, EntityVectorPos
from mcpeworld.nbt.leveldb import BedrockLevelDb


def parseEntityPosition( compound:amulet_nbt.CompoundTag ) -> EntityVectorPos:
    pos = EntityVectorPos()
    if "Pos" in compound:
        posList = compound["Pos"]
        if isinstance( posList, amulet_nbt.ListTag ) and len( posList ) >= 3:
            pos.x = float( posList[0] )
            pos.y = float( posList[1] )
            pos.z = float( posList[2] )
    return pos


def extractEntityHealth( compound:amulet_nbt.CompoundTag ) -> Tuple[Float, Float]:
    health = 0.0
    maxHealth = 0.0
    if "Attributes" in compound:
        attributes = compound["Attributes"]
        if isinstance( attributes, amulet_nbt.ListTag ):
            for attr in attributes:
                if isinstance( attr, amulet_nbt.CompoundTag ) and "Name" in attr:
                    attrName = attr["Name"].py_str
                    if attrName == "minecraft:health":
                        health = float( attr.get( "Current", amulet_nbt.FloatTag( 0.0 ) ) )
                        maxHealth = float( attr.get( "Max", amulet_nbt.FloatTag( 0.0 ) ) )
                        break
    if health == 0.0 and "Health" in compound:
        health = float( compound["Health"] )
    return health, maxHealth


def loadAllEntities( db:BedrockLevelDb ) -> MutableSequence[EntityItem]:
    entities:MutableSequence[EntityItem] = []
    for chunkKey, rawData in db.iterateEntities():
        try:
            offset = 0
            while offset < len( rawData ):
                result = amulet_nbt.load(
                    rawData[offset:],
                    compressed=False,
                    little_endian=True,
                    offset=True,
                    string_decoder=amulet_nbt.utf8_decoder
                )
                namedTag = result[0]
                bytesRead = result[1]
                compound = namedTag.compound
                identifier = ""
                if "identifier" in compound:
                    identifier = compound["identifier"].py_str
                if not identifier:
                    offset += bytesRead
                    continue
                position = parseEntityPosition( compound )
                uniqueId = int( compound.get( "UniqueID", amulet_nbt.LongTag( 0 ) ) )
                customName = ""
                if "CustomName" in compound:
                    customName = compound["CustomName"].py_str
                health, maxHealth = extractEntityHealth( compound )
                isBaby = bool( int( compound.get( "IsBaby", amulet_nbt.ByteTag( 0 ) ) ) )
                isTamed = bool( int( compound.get( "IsTamed", amulet_nbt.ByteTag( 0 ) ) ) )
                variant = int( compound.get( "Variant", amulet_nbt.IntTag( -1 ) ) )
                color = int( compound.get( "Color", amulet_nbt.ByteTag( -1 ) ) ) & 0xFF
                if color == 255:
                    color = -1
                entity = EntityItem(
                    chunkKey=chunkKey,
                    identifier=identifier,
                    position=position,
                    uniqueId=uniqueId,
                    customName=customName,
                    health=health,
                    maxHealth=maxHealth,
                    isBaby=isBaby,
                    isTamed=isTamed,
                    variant=variant,
                    color=color,
                    nbtData=compound,
                )
                entities.append( entity )
                offset += bytesRead
        except Exception:
            continue
    return entities


def saveEntitiesForChunk(
    db:BedrockLevelDb,
    allEntities:MutableSequence[EntityItem],
    chunkKey:Bytes,
) -> None:
    chunkEntities = [e for e in allEntities if e.chunkKey == chunkKey]
    combined = b""
    for entity in chunkEntities:
        if entity.nbtData is not None:
            namedTag = amulet_nbt.NamedTag( entity.nbtData, "" )
            nbtBytes = namedTag.to_nbt(
                compressed=False,
                little_endian=True,
                string_encoder=amulet_nbt.utf8_encoder
            )
            combined += nbtBytes
    if combined:
        db.put( chunkKey, combined )
    else:
        db.delete( chunkKey )


def setEntityHealth(
    compound:amulet_nbt.CompoundTag,
    health:Float,
) -> None:
    if "Attributes" in compound:
        attributes = compound["Attributes"]
        if isinstance( attributes, amulet_nbt.ListTag ):
            for attr in attributes:
                if isinstance( attr, amulet_nbt.CompoundTag ) and "Name" in attr:
                    if attr["Name"].py_str == "minecraft:health":
                        attr["Current"] = amulet_nbt.FloatTag( health )
                        break
    if "Health" in compound:
        compound["Health"] = amulet_nbt.IntTag( int( health ) )


def setEntityPosition(
    compound:amulet_nbt.CompoundTag,
    x:Float,
    y:Float,
    z:Float,
) -> None:
    posList = amulet_nbt.ListTag()
    posList.append( amulet_nbt.FloatTag( x ) )
    posList.append( amulet_nbt.FloatTag( y ) )
    posList.append( amulet_nbt.FloatTag( z ) )
    compound["Pos"] = posList


def setEntityCustomName(
    compound:amulet_nbt.CompoundTag,
    name:Str,
) -> None:
    if name:
        compound["CustomName"] = amulet_nbt.StringTag( name )
        compound["CustomNameVisible"] = amulet_nbt.ByteTag( 1 )
    else:
        if "CustomName" in compound:
            del compound["CustomName"]
        if "CustomNameVisible" in compound:
            del compound["CustomNameVisible"]
