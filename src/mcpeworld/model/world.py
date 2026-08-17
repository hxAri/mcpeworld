from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from mcpeworld import Bool, Float, Int, Str
from mcpeworld.constant import (
    DbFolderName,
    LevelDatFileName,
    LevelNameFileName,
    WorldIconFileName,
)


@dataclass
class WorldItem:

    folder:Path = field( default_factory=Path )
    worldName:Optional[Str] = None
    lastPlayedTime:Int = 0
    lastEditedTime:Int = 0
    canBeOpened:Bool = True

    @property
    def worldId( self ) -> Str:
        return self.folder.name

    @property
    def levelDat( self ) -> Path:
        return self.folder / LevelDatFileName

    @property
    def levelNameFile( self ) -> Path:
        return self.folder / LevelNameFileName

    @property
    def worldIcon( self ) -> Path:
        return self.folder / WorldIconFileName

    @property
    def entityDb( self ) -> Path:
        return self.folder / DbFolderName

    @property
    def displayName( self ) -> Str:
        if self.worldName:
            return self.worldName
        return self.folder.name

    def __repr__( self ) -> Str:
        return f"WorldItem({self.displayName})"


@dataclass
class WorldParameters:

    playerHealth:Float = 0.0
    playerLevel:Float = 0.0
    folderName:Str = ""
    levelName:Str = ""
    seed:Int = 0
    lastPlayed:Int = 0
    time:Int = 0
    difficulty:Int = 0
    gameMode:Int = 0
    generator:Int = 0
    spawnX:Int = 0
    spawnY:Int = 0
    spawnZ:Int = 0
    spawnV1Villagers:Bool = False
    cheatsEnabled:Bool = False
    build:Bool = True
    doDaylightCycle:Bool = False
    doEntityDrops:Bool = False
    doFireTick:Bool = False
    doImmediateRespawn:Bool = False
    doInsomnia:Bool = False
    doMobLoot:Bool = False
    doMobSpawning:Bool = False
    doTileDrops:Bool = False
    doWeatherCycle:Bool = False
    drowningDamage:Bool = False
    educationFeaturesEnabled:Bool = False
    fallDamage:Bool = False
    fireDamage:Bool = False
    freezeDamage:Bool = False
    keepInventory:Bool = False
    mobGriefing:Bool = False
    naturalRegeneration:Bool = False
    showCoordinates:Bool = False
    showDeathMessages:Bool = False
    showTags:Bool = False
    spawnMobs:Bool = False
    tntExplodes:Bool = False
