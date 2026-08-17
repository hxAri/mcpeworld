from datetime import datetime, timezone
from typing import MutableSequence

from mcpeworld import Int, Str
from mcpeworld.editor.leveldat import DifficultyNames, GameModeNames, GeneratorNames
from mcpeworld.model.entity import EntityItem
from mcpeworld.model.item import BEGameItem, Ench
from mcpeworld.model.tileentity import TileEntityItem
from mcpeworld.model.world import WorldParameters


def formatTimestamp( timestamp:Int ) -> Str:
    if timestamp <= 0:
        return "Unknown"
    try:
        dt = datetime.fromtimestamp( timestamp, tz=timezone.utc )
        return dt.strftime( "%Y-%m-%d %H:%M:%S UTC" )
    except ( ValueError, OSError ):
        return str( timestamp )


def formatWorldParameters( params:WorldParameters ) -> Str:
    lines = [
        f"  World Name     : {params.levelName}",
        f"  Folder         : {params.folderName}",
        f"  Seed           : {params.seed}",
        f"  Game Mode      : {GameModeNames.get( params.gameMode, str( params.gameMode ) )}",
        f"  Difficulty     : {DifficultyNames.get( params.difficulty, str( params.difficulty ) )}",
        f"  Generator      : {GeneratorNames.get( params.generator, str( params.generator ) )}",
        f"  Last Played    : {formatTimestamp( params.lastPlayed )}",
        f"  Time           : {params.time}",
        f"  Spawn          : {params.spawnX}, {params.spawnY}, {params.spawnZ}",
        f"  Cheats         : {'Enabled' if params.cheatsEnabled else 'Disabled'}",
        f"  Player Health  : {params.playerHealth:.1f}",
        f"  Player Level   : {params.playerLevel:.0f}",
    ]
    return "\n".join( lines )


def formatItem( item:BEGameItem, enchantmentNames:dict = None ) -> Str:
    if item.isEmpty:
        return "(Empty)"
    name = item.displayName if item.displayName else item.itemName
    header = f"{name} ({item.itemName})"
    if item.stackSize > 1:
        header += f" x{item.stackSize}"
    if item.damage > 0:
        header += f" dmg:{item.damage}"
    lines = [header]
    if item.enchantments:
        lines.append( "   -> Enchantments:" )
        for ench in item.enchantments:
            enchName = str( ench.enchantId )
            if enchantmentNames and ench.enchantId in enchantmentNames:
                enchName = enchantmentNames[ench.enchantId]
            lines.append( f"      - {enchName} ({ench.enchantId}) Level {ench.level}" )
    if item.trimPattern and item.trimMaterial:
        lines.append( f"   -> Trim: {item.trimPattern.title()} ({item.trimPattern}) / {item.trimMaterial.title()} ({item.trimMaterial})" )
    return "\n".join( lines )


def formatItemDetailed( item:BEGameItem, enchantmentNames:dict = None ) -> Str:
    if item.isEmpty:
        return "(Empty Slot)"
    lines = [
        f"  Item       : {item.itemName}",
        f"  Namespace  : {item.belongsTo}",
        f"  Stack Size : {item.stackSize}",
        f"  Damage     : {item.damage}",
    ]
    if item.displayName:
        lines.append( f"  Custom Name: {item.displayName}" )
    if item.states:
        lines.append( "  Block States:" )
        for key, value in item.states.items():
            lines.append( f"    {key} = {value}" )
    if item.enchantments:
        lines.append( "  Enchantments:" )
        for ench in item.enchantments:
            name = str( ench.enchantId )
            if enchantmentNames and ench.enchantId in enchantmentNames:
                name = enchantmentNames[ench.enchantId]
            lines.append( f"    {name} Level {ench.level}" )
    return "\n".join( lines )


def formatEntityLabel( entity:EntityItem ) -> Str:
    name = entity.shortId.replace( "_", " " ).title()
    label = f"{name} ({entity.identifier})"
    if entity.customName:
        label = f'"{entity.customName}" {label}'
    pos = f"({entity.position.x:.0f}, {entity.position.y:.0f}, {entity.position.z:.0f})"
    label += f" at {pos}"
    if entity.health > 0:
        if entity.maxHealth > 0:
            label += f" HP:{entity.health:.0f}/{entity.maxHealth:.0f}"
        else:
            label += f" HP:{entity.health:.0f}"
    tags = []
    if entity.isBaby:
        tags.append( "Baby" )
    if entity.isTamed:
        tags.append( "Tamed" )
    if tags:
        label += f" [{', '.join( tags )}]"
    return label


def formatEntityList( entities:MutableSequence[EntityItem] ) -> Str:
    if not entities:
        return "No entities found."
    lines = []
    for i, entity in enumerate( entities ):
        lines.append( f"  [{i + 1}] {formatEntityLabel( entity )}" )
    return "\n".join( lines )


def formatTileEntityList( tiles:MutableSequence[TileEntityItem] ) -> Str:
    if not tiles:
        return "No tile entities found."
    lines = []
    for i, tile in enumerate( tiles ):
        pos = f"({tile.position.x:.0f}, {tile.position.y:.0f}, {tile.position.z:.0f})"
        overlay = f" - {tile.overlayData}" if tile.overlayData else ""
        lines.append( f"  [{i + 1}] {tile.tileIdentifier} at {pos}{overlay}" )
    return "\n".join( lines )
