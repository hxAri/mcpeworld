from pathlib import Path
from typing import MutableMapping, Optional

import amulet_nbt

from mcpeworld import Bool, Float, Int, Str
from mcpeworld.model.world import WorldParameters
from mcpeworld.nbt.leveldat import readLevelDat, writeLevelDat


DifficultyNames:MutableMapping[Int, Str] = {
    0: "Peaceful",
    1: "Easy",
    2: "Normal",
    3: "Hard",
}

GameModeNames:MutableMapping[Int, Str] = {
    0: "Survival",
    1: "Creative",
    2: "Adventure",
    3: "Spectator",
}

GeneratorNames:MutableMapping[Int, Str] = {
    0: "Old",
    1: "Infinite",
    2: "Flat",
}

GameRuleKeys:MutableMapping[Str, Str] = {
    "doDaylightCycle": "dodaylightcycle",
    "doEntityDrops": "doentitydrops",
    "doFireTick": "dofiretick",
    "doImmediateRespawn": "doimmediaterespawn",
    "doInsomnia": "doinsomnia",
    "doMobLoot": "domobloot",
    "doMobSpawning": "domobspawning",
    "doTileDrops": "dotiledrops",
    "doWeatherCycle": "doweathercycle",
    "drowningDamage": "drowningdamage",
    "fallDamage": "falldamage",
    "fireDamage": "firedamage",
    "freezeDamage": "freezedamage",
    "keepInventory": "keepinventory",
    "mobGriefing": "mobgriefing",
    "naturalRegeneration": "naturalregeneration",
    "showCoordinates": "showcoordinates",
    "showDeathMessages": "showdeathmessages",
    "showTags": "showtags",
    "tntExplodes": "tntexplodes",
}


def loadWorldParameters( levelDatPath:Path, playerNbt:Optional[amulet_nbt.CompoundTag] = None ) -> WorldParameters:
    namedTag = readLevelDat( levelDatPath )
    root = namedTag.compound
    params = WorldParameters()
    params.folderName = levelDatPath.parent.name
    params.levelName = root.get( "LevelName", amulet_nbt.StringTag( "" ) ).py_str
    params.seed = int( root.get( "RandomSeed", amulet_nbt.LongTag( 0 ) ) )
    params.lastPlayed = int( root.get( "LastPlayed", amulet_nbt.LongTag( 0 ) ) )
    params.time = int( root.get( "Time", amulet_nbt.IntTag( 0 ) ) )
    params.difficulty = int( root.get( "Difficulty", amulet_nbt.IntTag( 0 ) ) )
    params.gameMode = int( root.get( "GameType", amulet_nbt.IntTag( 0 ) ) )
    params.generator = int( root.get( "Generator", amulet_nbt.IntTag( 0 ) ) )
    params.spawnX = int( root.get( "SpawnX", amulet_nbt.IntTag( 0 ) ) )
    params.spawnY = int( root.get( "SpawnY", amulet_nbt.IntTag( 0 ) ) )
    params.spawnZ = int( root.get( "SpawnZ", amulet_nbt.IntTag( 0 ) ) )
    params.spawnV1Villagers = bool( int( root.get( "SpawnV1Villagers", amulet_nbt.ByteTag( 0 ) ) ) )
    params.cheatsEnabled = bool( int( root.get( "commandsEnabled", amulet_nbt.ByteTag( 0 ) ) ) )
    params.educationFeaturesEnabled = bool( int( root.get( "educationFeaturesEnabled", amulet_nbt.ByteTag( 0 ) ) ) )
    params.spawnMobs = bool( int( root.get( "spawnMobs", amulet_nbt.ByteTag( 0 ) ) ) )
    if "abilities" in root:
        abilities = root["abilities"]
        if isinstance( abilities, amulet_nbt.CompoundTag ):
            params.build = bool( int( abilities.get( "build", amulet_nbt.ByteTag( 1 ) ) ) )
    for fieldName, nbtKey in GameRuleKeys.items():
        value = root.get( nbtKey, None )
        if value is not None:
            setattr( params, fieldName, bool( int( value ) ) )
    if playerNbt is not None:
        if "PlayerLevel" in playerNbt:
            params.playerLevel = float( int( playerNbt["PlayerLevel"] ) )
        attributes = playerNbt.get( "Attributes", None )
        if attributes is not None and isinstance( attributes, amulet_nbt.ListTag ):
            for attr in attributes:
                if isinstance( attr, amulet_nbt.CompoundTag ):
                    attrName = attr.get( "Name", amulet_nbt.StringTag( "" ) ).py_str
                    if attrName == "minecraft:health":
                        params.playerHealth = float( attr.get( "Current", amulet_nbt.FloatTag( 0.0 ) ) )
    return params


def saveWorldParameters( levelDatPath:Path, params:WorldParameters ) -> None:
    namedTag = readLevelDat( levelDatPath )
    root = namedTag.compound
    root["LevelName"] = amulet_nbt.StringTag( params.levelName )
    root["RandomSeed"] = amulet_nbt.LongTag( params.seed )
    root["Time"] = amulet_nbt.IntTag( params.time )
    root["Difficulty"] = amulet_nbt.IntTag( params.difficulty )
    root["GameType"] = amulet_nbt.IntTag( params.gameMode )
    root["Generator"] = amulet_nbt.IntTag( params.generator )
    root["SpawnX"] = amulet_nbt.IntTag( params.spawnX )
    root["SpawnY"] = amulet_nbt.IntTag( params.spawnY )
    root["SpawnZ"] = amulet_nbt.IntTag( params.spawnZ )
    root["SpawnV1Villagers"] = amulet_nbt.ByteTag( int( params.spawnV1Villagers ) )
    root["commandsEnabled"] = amulet_nbt.ByteTag( int( params.cheatsEnabled ) )
    root["educationFeaturesEnabled"] = amulet_nbt.ByteTag( int( params.educationFeaturesEnabled ) )
    root["spawnMobs"] = amulet_nbt.ByteTag( int( params.spawnMobs ) )
    if "abilities" in root:
        abilities = root["abilities"]
        if isinstance( abilities, amulet_nbt.CompoundTag ):
            abilities["build"] = amulet_nbt.ByteTag( int( params.build ) )
    for fieldName, nbtKey in GameRuleKeys.items():
        value = getattr( params, fieldName, False )
        root[nbtKey] = amulet_nbt.ByteTag( int( value ) )
    levelNameFile = levelDatPath.parent / "levelname.txt"
    levelNameFile.write_text( params.levelName, encoding="utf-8" )
    writeLevelDat( levelDatPath, namedTag )
