from typing import Any, MutableMapping, MutableSequence, Optional

import amulet_nbt

from mcpeworld import Float, Int, Str
from mcpeworld.constant import (
    ContainerTileEntities,
    TileEntityBanner,
    TileEntityBed,
    TileEntityCampfire,
    TileEntityCommandBlock,
    TileEntityGlowItemFrame,
    TileEntityHangingSign,
    TileEntityItemFrame,
    TileEntityMobSpawner,
    TileEntitySign,
)
from mcpeworld.model.entity import EntityVectorPos
from mcpeworld.model.tileentity import TileEntityItem
from mcpeworld.nbt.leveldb import BedrockLevelDb


ColorNames:MutableMapping[Int, Str] = {
    0: "White", 1: "Orange", 2: "Magenta", 3: "Light Blue",
    4: "Yellow", 5: "Lime", 6: "Pink", 7: "Gray",
    8: "Light Gray", 9: "Cyan", 10: "Purple", 11: "Blue",
    12: "Brown", 13: "Green", 14: "Red", 15: "Black",
}


def _extractItemName( compound:amulet_nbt.CompoundTag ) -> Str:
    if "Name" in compound:
        name = compound["Name"].py_str
        if name.startswith( "minecraft:" ):
            return name[10:]
        return name
    return ""


def extractTileOverlay( compound:amulet_nbt.CompoundTag, tileId:Str ) -> Str:
    if tileId in ( TileEntitySign, TileEntityHangingSign ):
        parts = []
        if "FrontText" in compound:
            frontText = compound["FrontText"]
            if isinstance( frontText, amulet_nbt.CompoundTag ) and "Text" in frontText:
                text = frontText["Text"].py_str.strip()
                if text:
                    parts.append( f"Front: {text}" )
        if "BackText" in compound:
            backText = compound["BackText"]
            if isinstance( backText, amulet_nbt.CompoundTag ) and "Text" in backText:
                text = backText["Text"].py_str.strip()
                if text:
                    parts.append( f"Back: {text}" )
        if not parts and "Text" in compound:
            text = compound["Text"].py_str.strip()
            if text:
                parts.append( text )
        return " | ".join( parts ) if parts else "(blank)"
    if tileId == TileEntityCommandBlock:
        if "Command" in compound:
            cmd = compound["Command"].py_str
            if len( cmd ) > 50:
                return cmd[:47] + "..."
            return cmd if cmd else "(empty)"
        return "(empty)"
    if tileId in ( TileEntityItemFrame, TileEntityGlowItemFrame ):
        if "Item" in compound:
            itemTag = compound["Item"]
            if isinstance( itemTag, amulet_nbt.CompoundTag ):
                name = _extractItemName( itemTag )
                if name:
                    return name.replace( "_", " " ).title()
        return "(empty frame)"
    if tileId == TileEntityMobSpawner:
        if "EntityIdentifier" in compound:
            entityId = compound["EntityIdentifier"].py_str
            if entityId.startswith( "minecraft:" ):
                entityId = entityId[10:]
            return entityId.replace( "_", " " ).title() if entityId else "(none)"
        return "(none)"
    if tileId == TileEntityBed:
        if "color" in compound:
            colorVal = int( compound["color"] ) & 0xFF
            colorName = ColorNames.get( colorVal, str( colorVal ) )
            return colorName
        return ""
    if tileId in ContainerTileEntities:
        if "Items" in compound:
            itemsList = compound["Items"]
            if isinstance( itemsList, amulet_nbt.ListTag ):
                count = len( itemsList )
                if count == 0:
                    return "Empty"
                if count <= 3:
                    names = []
                    for itemTag in itemsList:
                        if isinstance( itemTag, amulet_nbt.CompoundTag ):
                            name = _extractItemName( itemTag )
                            if name:
                                names.append( name.replace( "_", " " ).title() )
                    if names:
                        return ", ".join( names )
                return f"{count} items"
        return "Empty"
    if tileId == TileEntityCampfire:
        items = []
        for key in ( "Item1", "Item2", "Item3", "Item4" ):
            if key in compound:
                itemTag = compound[key]
                if isinstance( itemTag, amulet_nbt.CompoundTag ):
                    name = _extractItemName( itemTag )
                    if name:
                        items.append( name.replace( "_", " " ).title() )
        if items:
            return f"{len( items )}/4: {', '.join( items )}"
        return "Empty"
    if tileId == TileEntityBanner:
        parts = []
        if "Base" in compound:
            baseVal = int( compound["Base"] ) & 0xFF
            parts.append( ColorNames.get( baseVal, str( baseVal ) ) )
        if "Patterns" in compound:
            patternList = compound["Patterns"]
            if isinstance( patternList, amulet_nbt.ListTag ) and len( patternList ) > 0:
                parts.append( f"{len( patternList )} patterns" )
        return ", ".join( parts ) if parts else ""
    if tileId == "Lectern":
        if "book" in compound:
            bookTag = compound["book"]
            if isinstance( bookTag, amulet_nbt.CompoundTag ):
                name = _extractItemName( bookTag )
                if name:
                    return name.replace( "_", " " ).title()
        return "(empty)"
    if tileId == "Jukebox":
        if "RecordItem" in compound:
            recordTag = compound["RecordItem"]
            if isinstance( recordTag, amulet_nbt.CompoundTag ):
                name = _extractItemName( recordTag )
                if name:
                    return name.replace( "_", " " ).title()
        return "(empty)"
    if tileId == "Skull":
        if "SkullType" in compound:
            skullTypes = {
                0: "Skeleton", 1: "Wither Skeleton", 2: "Zombie",
                3: "Player", 4: "Creeper", 5: "Dragon",
            }
            skullVal = int( compound["SkullType"] )
            return skullTypes.get( skullVal, f"Type {skullVal}" )
        return ""
    if tileId == "FlowerPot":
        if "PlantBlock" in compound:
            plantTag = compound["PlantBlock"]
            if isinstance( plantTag, amulet_nbt.CompoundTag ) and "name" in plantTag:
                name = plantTag["name"].py_str
                if name.startswith( "minecraft:" ):
                    name = name[10:]
                return name.replace( "_", " " ).title()
        return "(empty)"
    if tileId == "Beehive":
        occupants = 0
        if "Occupants" in compound:
            occupantsList = compound["Occupants"]
            if isinstance( occupantsList, amulet_nbt.ListTag ):
                occupants = len( occupantsList )
        return f"{occupants} bee(s)"
    if tileId == "Beacon":
        parts = []
        if "primary" in compound:
            primary = int( compound["primary"] )
            if primary > 0:
                parts.append( f"Primary: {primary}" )
        if "secondary" in compound:
            secondary = int( compound["secondary"] )
            if secondary > 0:
                parts.append( f"Secondary: {secondary}" )
        return ", ".join( parts ) if parts else "(inactive)"
    return ""


def parseTilePosition( compound:amulet_nbt.CompoundTag ) -> EntityVectorPos:
    x = int( compound.get( "x", amulet_nbt.IntTag( 0 ) ) )
    y = int( compound.get( "y", amulet_nbt.IntTag( 0 ) ) )
    z = int( compound.get( "z", amulet_nbt.IntTag( 0 ) ) )
    return EntityVectorPos( x=float( x ), y=float( y ), z=float( z ) )


def loadAllTileEntities( db:BedrockLevelDb ) -> MutableSequence[TileEntityItem]:
    tileEntities:MutableSequence[TileEntityItem] = []
    for chunkKey, rawData in db.iterateTileEntities():
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
                tileId = ""
                if "id" in compound:
                    tileId = compound["id"].py_str
                position = parseTilePosition( compound )
                overlay = extractTileOverlay( compound, tileId )
                tile = TileEntityItem(
                    chunkKey=chunkKey,
                    tileIdentifier=tileId,
                    position=position,
                    overlayData=overlay,
                    nbtData=compound,
                )
                tileEntities.append( tile )
                offset += bytesRead
        except Exception:
            continue
    return tileEntities


def editSignText(
    compound:amulet_nbt.CompoundTag,
    frontText:Optional[Str] = None,
    backText:Optional[Str] = None
) -> None:
    if frontText is not None:
        if "FrontText" not in compound:
            compound["FrontText"] = amulet_nbt.CompoundTag()
        frontTag = compound["FrontText"]
        if isinstance( frontTag, amulet_nbt.CompoundTag ):
            frontTag["Text"] = amulet_nbt.StringTag( frontText )
    if backText is not None:
        if "BackText" not in compound:
            compound["BackText"] = amulet_nbt.CompoundTag()
        backTag = compound["BackText"]
        if isinstance( backTag, amulet_nbt.CompoundTag ):
            backTag["Text"] = amulet_nbt.StringTag( backText )


def editCommandBlock( compound:amulet_nbt.CompoundTag, command:Str ) -> None:
    compound["Command"] = amulet_nbt.StringTag( command )


def editMobSpawner( compound:amulet_nbt.CompoundTag, entityIdentifier:Str ) -> None:
    compound["EntityIdentifier"] = amulet_nbt.StringTag( entityIdentifier )


def editBedColor( compound:amulet_nbt.CompoundTag, color:Int ) -> None:
    compound["color"] = amulet_nbt.ByteTag( color )


def saveTileEntity( db:BedrockLevelDb, tile:TileEntityItem ) -> None:
    if tile.nbtData is None:
        return
    namedTag = amulet_nbt.NamedTag( tile.nbtData, "" )
    nbtBytes = namedTag.to_nbt(
        compressed=False,
        little_endian=True,
        string_encoder=amulet_nbt.utf8_encoder
    )
    db.put( tile.chunkKey, nbtBytes )
