from pathlib import Path
from typing import MutableSequence

from mcpeworld import Str
from mcpeworld.constant import (
    DbFolderName,
    LevelDatFileName,
    LevelNameFileName,
    WorldsDir,
)
from mcpeworld.model.world import WorldItem
from mcpeworld.nbt.leveldat import readLevelDat


def isValidWorldFolder( folder: Path ) -> bool:
    levelDat = folder / LevelDatFileName
    dbFolder = folder / DbFolderName
    return levelDat.is_file() and dbFolder.is_dir()


def readWorldName( folder: Path ) -> Str:
    levelNameFile = folder / LevelNameFileName
    if levelNameFile.is_file():
        return levelNameFile.read_text( encoding="utf-8" ).strip()
    return folder.name


def scanWorlds( directory: Path = WorldsDir ) -> MutableSequence[WorldItem]:
    worlds: MutableSequence[WorldItem] = []
    if not directory.is_dir():
        return worlds
    for entry in sorted( directory.iterdir() ):
        if not entry.is_dir():
            continue
        if entry.name.startswith( "." ):
            continue
        if not isValidWorldFolder( entry ):
            continue
        worldName = readWorldName( entry )
        world = WorldItem( folder=entry, worldName=worldName )
        try:
            namedTag = readLevelDat( entry / LevelDatFileName )
            rootTag = namedTag.compound
            if "LastPlayed" in rootTag:
                world.lastPlayedTime = int( rootTag["LastPlayed"] )
            if "lastOpenedWithVersion" in rootTag:
                world.lastEditedTime = int( rootTag.get( "LastPlayed", 0 ) )
        except Exception:
            world.canBeOpened = False
        worlds.append( world )
    return worlds
