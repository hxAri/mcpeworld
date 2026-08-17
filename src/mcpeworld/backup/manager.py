import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import MutableSequence, Optional

from mcpeworld import Bool, Str
from mcpeworld.constant import BackupsDir, WorldsDir
from mcpeworld.util.path import isValidWorldFolder


def createBackup( worldFolder:Path ) -> Path:
    worldId = worldFolder.name
    backupRoot = BackupsDir / worldId
    backupRoot.mkdir( parents=True, exist_ok=True )
    timestamp = datetime.now( timezone.utc ).strftime( "%Y%m%d_%H%M%S" )
    backupPath = backupRoot / timestamp
    shutil.copytree( worldFolder, backupPath )
    return backupPath


def listBackups( worldFolder:Path ) -> MutableSequence[Path]:
    worldId = worldFolder.name
    backupRoot = BackupsDir / worldId
    if not backupRoot.is_dir():
        return []
    backups = sorted( backupRoot.iterdir(), reverse=True )
    return [b for b in backups if b.is_dir()]


def restoreBackup( backupPath:Path, worldFolder:Path ) -> Bool:
    if not backupPath.is_dir():
        return False
    if worldFolder.exists():
        shutil.rmtree( worldFolder )
    shutil.copytree( backupPath, worldFolder )
    return True


def importWorldFromPath( sourcePath:Path, destName:Optional[Str] = None ) -> Path:
    if not isValidWorldFolder( sourcePath ):
        raise ValueError( f"Not a valid world folder: {sourcePath}" )
    WorldsDir.mkdir( parents=True, exist_ok=True )
    targetName = destName or sourcePath.name
    targetPath = WorldsDir / targetName
    if targetPath.exists():
        timestamp = datetime.now( timezone.utc ).strftime( "%Y%m%d_%H%M%S" )
        targetPath = WorldsDir / f"{targetName}_{timestamp}"
    shutil.copytree( sourcePath, targetPath )
    return targetPath


def importWorldFromMcworld( mcworldFile:Path, destName:Optional[Str] = None ) -> Path:
    if not mcworldFile.is_file():
        raise FileNotFoundError( f"File not found: {mcworldFile}" )
    WorldsDir.mkdir( parents=True, exist_ok=True )
    baseName = destName or mcworldFile.stem
    targetPath = WorldsDir / baseName
    if targetPath.exists():
        timestamp = datetime.now( timezone.utc ).strftime( "%Y%m%d_%H%M%S" )
        targetPath = WorldsDir / f"{baseName}_{timestamp}"
    targetPath.mkdir( parents=True, exist_ok=True )
    with zipfile.ZipFile( mcworldFile, "r" ) as archive:
        for member in archive.infolist():
            try:
                archive.extract( member, targetPath )
            except zipfile.BadZipFile:
                continue
    innerDirs = [d for d in targetPath.iterdir() if d.is_dir()]
    if len( innerDirs ) == 1 and isValidWorldFolder( innerDirs[0] ):
        tempPath = targetPath.with_name( targetPath.name + "_tmp" )
        shutil.move( str( innerDirs[0] ), str( tempPath ) )
        shutil.rmtree( targetPath )
        shutil.move( str( tempPath ), str( targetPath ) )
    if not isValidWorldFolder( targetPath ):
        raise ValueError( f"Extracted archive does not contain a valid world: {mcworldFile}" )
    return targetPath


def exportWorldToMcworld( worldFolder:Path ) -> Path:
    WorldsDir.mkdir( parents=True, exist_ok=True )
    outputPath = WorldsDir / f"{worldFolder.name}.mcworld"
    with zipfile.ZipFile( outputPath, "w", zipfile.ZIP_DEFLATED ) as archive:
        for entry in worldFolder.rglob( "*" ):
            arcName = entry.relative_to( worldFolder )
            archive.write( entry, arcName )
    return outputPath
