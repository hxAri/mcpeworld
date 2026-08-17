from pathlib import Path
from typing import MutableSequence, Optional

import amulet_nbt

from mcpeworld import Bool, Int, Str
from mcpeworld.backup.manager import createBackup
from mcpeworld.editor.entity import loadAllEntities
from mcpeworld.editor.inventory import (
    loadArmorSlots,
    loadInventory,
    saveArmorSlot,
    saveInventorySlot,
    clearSlot,
)
from mcpeworld.editor.leveldat import (
    loadWorldParameters,
    saveWorldParameters,
)
from mcpeworld.editor.tileentity import loadAllTileEntities
from mcpeworld.model.entity import EntityItem
from mcpeworld.model.item import ActiveEffect, BEGameItem
from mcpeworld.model.result import OperationOutcome, WorldOperationResult
from mcpeworld.model.slot import InventoryType, SlotType
from mcpeworld.model.tileentity import TileEntityItem
from mcpeworld.model.world import WorldItem, WorldParameters
from mcpeworld.nbt.leveldb import BedrockLevelDb


class WorldEditor:

    def __init__( self, world:WorldItem ) -> None:
        self.world = world
        self.db:Optional[BedrockLevelDb] = None
        self.playerNbt:Optional[amulet_nbt.CompoundTag] = None
        self.parameters:Optional[WorldParameters] = None
        self._initialHealth:Float = 0.0
        self._initialLevel:Float = 0.0

    def open( self ) -> OperationOutcome:
        if not self.world.levelDat.is_file():
            return OperationOutcome(
                result=WorldOperationResult.ErrorNullWorld,
                message="level.dat not found"
            )
        if not self.world.entityDb.is_dir():
            return OperationOutcome(
                result=WorldOperationResult.ErrorNullWorld,
                message="Database folder not found"
            )
        try:
            self.db = BedrockLevelDb( self.world.entityDb )
            self.db.open()
        except Exception as error:
            return OperationOutcome(
                result=WorldOperationResult.ErrorDbOpen,
                message=f"Failed to open LevelDB: {error}"
            )
        playerTag = self.db.readPlayerNbt()
        if playerTag is not None:
            self.playerNbt = playerTag.compound
        try:
            self.parameters = loadWorldParameters(
                self.world.levelDat,
                self.playerNbt
            )
        except Exception as error:
            return OperationOutcome(
                result=WorldOperationResult.ErrorRead,
                message=f"Failed to read level.dat: {error}"
            )
        if self.parameters is not None:
            self._initialHealth = self.parameters.playerHealth
            self._initialLevel = self.parameters.playerLevel
        return OperationOutcome( result=WorldOperationResult.Success )

    def close( self ) -> None:
        if self.db is not None:
            self.db.close()
            self.db = None

    def backup( self ) -> Path:
        return createBackup( self.world.folder )

    def getParameters( self ) -> Optional[WorldParameters]:
        return self.parameters

    def saveParameters( self ) -> OperationOutcome:
        if self.parameters is None:
            return OperationOutcome(
                result=WorldOperationResult.ErrorNullWorld,
                message="No parameters loaded"
            )
        try:
            saveWorldParameters( self.world.levelDat, self.parameters )
            playerChanged = (
                self.parameters.playerHealth != self._initialHealth
                or self.parameters.playerLevel != self._initialLevel
            )
            if playerChanged and self.playerNbt is not None and self.db is not None:
                self._savePlayerAttributes()
                self.db.writePlayerNbt( amulet_nbt.NamedTag( self.playerNbt, "" ) )
                self._initialHealth = self.parameters.playerHealth
                self._initialLevel = self.parameters.playerLevel
            return OperationOutcome( result=WorldOperationResult.Success )
        except Exception as error:
            return OperationOutcome(
                result=WorldOperationResult.ErrorWrite,
                message=f"Failed to save: {error}"
            )

    def getInventory( self ) -> MutableSequence[BEGameItem]:
        if self.playerNbt is None:
            return []
        return loadInventory( self.playerNbt, InventoryType.Inventory )

    def getEnderChest( self ) -> MutableSequence[BEGameItem]:
        if self.playerNbt is None:
            return []
        return loadInventory( self.playerNbt, InventoryType.EnderChestInventory )

    def getArmor( self ) -> MutableSequence[BEGameItem]:
        if self.playerNbt is None:
            return []
        return loadArmorSlots( self.playerNbt )

    def setInventorySlot( self, slotIndex:Int, item:BEGameItem ) -> OperationOutcome:
        if self.playerNbt is None or self.db is None:
            return OperationOutcome(
                result=WorldOperationResult.ErrorNullWorld,
                message="Player data not loaded"
            )
        try:
            saveInventorySlot( self.playerNbt, InventoryType.Inventory, slotIndex, item )
            self.db.writePlayerNbt( amulet_nbt.NamedTag( self.playerNbt, "" ) )
            return OperationOutcome( result=WorldOperationResult.Success )
        except Exception as error:
            return OperationOutcome(
                result=WorldOperationResult.ErrorWrite,
                message=f"Failed to save slot: {error}"
            )

    def setEnderChestSlot( self, slotIndex:Int, item:BEGameItem ) -> OperationOutcome:
        if self.playerNbt is None or self.db is None:
            return OperationOutcome(
                result=WorldOperationResult.ErrorNullWorld,
                message="Player data not loaded"
            )
        try:
            saveInventorySlot( self.playerNbt, InventoryType.EnderChestInventory, slotIndex, item )
            self.db.writePlayerNbt( amulet_nbt.NamedTag( self.playerNbt, "" ) )
            return OperationOutcome( result=WorldOperationResult.Success )
        except Exception as error:
            return OperationOutcome(
                result=WorldOperationResult.ErrorWrite,
                message=f"Failed to save ender chest slot: {error}"
            )

    def setArmorSlot( self, slotType:SlotType, item:BEGameItem ) -> OperationOutcome:
        if self.playerNbt is None or self.db is None:
            return OperationOutcome(
                result=WorldOperationResult.ErrorNullWorld,
                message="Player data not loaded"
            )
        try:
            saveArmorSlot( self.playerNbt, slotType, item )
            self.db.writePlayerNbt( amulet_nbt.NamedTag( self.playerNbt, "" ) )
            return OperationOutcome( result=WorldOperationResult.Success )
        except Exception as error:
            return OperationOutcome(
                result=WorldOperationResult.ErrorWrite,
                message=f"Failed to save armor slot: {error}"
            )

    def clearInventorySlot( self, slotIndex:Int ) -> OperationOutcome:
        if self.playerNbt is None or self.db is None:
            return OperationOutcome(
                result=WorldOperationResult.ErrorNullWorld,
                message="Player data not loaded"
            )
        try:
            clearSlot( self.playerNbt, InventoryType.Inventory, slotIndex )
            self.db.writePlayerNbt( amulet_nbt.NamedTag( self.playerNbt, "" ) )
            return OperationOutcome( result=WorldOperationResult.Success )
        except Exception as error:
            return OperationOutcome(
                result=WorldOperationResult.ErrorWrite,
                message=f"Failed to clear slot: {error}"
            )

    def getEntities( self ) -> MutableSequence[EntityItem]:
        if self.db is None:
            return []
        return loadAllEntities( self.db )

    def getTileEntities( self ) -> MutableSequence[TileEntityItem]:
        if self.db is None:
            return []
        return loadAllTileEntities( self.db )

    def getActiveEffects( self ) -> MutableSequence[ActiveEffect]:
        if self.playerNbt is None:
            return []
        effectList = self.playerNbt.get( "ActiveEffects", None )
        if effectList is None or not isinstance( effectList, amulet_nbt.ListTag ):
            return []
        effects:MutableSequence[ActiveEffect] = []
        for tag in effectList:
            if not isinstance( tag, amulet_nbt.CompoundTag ):
                continue
            effects.append( ActiveEffect(
                effectId=int( tag.get( "Id", amulet_nbt.ByteTag( 0 ) ) ) & 0xFF,
                amplifier=int( tag.get( "Amplifier", amulet_nbt.ByteTag( 0 ) ) ) & 0xFF,
                duration=int( tag.get( "Duration", amulet_nbt.IntTag( 0 ) ) ),
                ambient=bool( int( tag.get( "Ambient", amulet_nbt.ByteTag( 0 ) ) ) ),
                showParticles=bool( int( tag.get( "ShowParticles", amulet_nbt.ByteTag( 1 ) ) ) ),
            ) )
        return effects

    def setActiveEffects( self, effects:MutableSequence[ActiveEffect] ) -> OperationOutcome:
        if self.playerNbt is None or self.db is None:
            return OperationOutcome(
                result=WorldOperationResult.ErrorNullWorld,
                message="Player data not loaded"
            )
        try:
            effectList = amulet_nbt.ListTag()
            for effect in effects:
                tag = amulet_nbt.CompoundTag()
                tag["Id"] = amulet_nbt.ByteTag( effect.effectId )
                tag["Amplifier"] = amulet_nbt.ByteTag( effect.amplifier )
                tag["Duration"] = amulet_nbt.IntTag( effect.duration )
                tag["DurationEasy"] = amulet_nbt.IntTag( effect.duration )
                tag["DurationNormal"] = amulet_nbt.IntTag( effect.duration )
                tag["DurationHard"] = amulet_nbt.IntTag( effect.duration )
                tag["Ambient"] = amulet_nbt.ByteTag( int( effect.ambient ) )
                tag["ShowParticles"] = amulet_nbt.ByteTag( int( effect.showParticles ) )
                effectList.append( tag )
            self.playerNbt["ActiveEffects"] = effectList
            self.db.writePlayerNbt( amulet_nbt.NamedTag( self.playerNbt, "" ) )
            return OperationOutcome( result=WorldOperationResult.Success )
        except Exception as error:
            return OperationOutcome(
                result=WorldOperationResult.ErrorWrite,
                message=f"Failed to save effects: {error}"
            )

    def _savePlayerAttributes( self ) -> None:
        if self.playerNbt is None or self.parameters is None:
            return
        if "Attributes" not in self.playerNbt:
            self.playerNbt["Attributes"] = amulet_nbt.ListTag()
        attributes = self.playerNbt["Attributes"]
        if not isinstance( attributes, amulet_nbt.ListTag ):
            return
        healthFound = False
        levelFound = False
        for attr in attributes:
            if not isinstance( attr, amulet_nbt.CompoundTag ):
                continue
            attrName = attr.get( "Name", amulet_nbt.StringTag( "" ) ).py_str
            if attrName == "minecraft:health":
                attr["Current"] = amulet_nbt.FloatTag( self.parameters.playerHealth )
                attr["Base"] = amulet_nbt.FloatTag( self.parameters.playerHealth )
                healthFound = True
            elif attrName == "minecraft:player.level":
                attr["Current"] = amulet_nbt.FloatTag( self.parameters.playerLevel )
                attr["Base"] = amulet_nbt.FloatTag( self.parameters.playerLevel )
                levelFound = True
        if not healthFound:
            healthAttr = amulet_nbt.CompoundTag()
            healthAttr["Name"] = amulet_nbt.StringTag( "minecraft:health" )
            healthAttr["Base"] = amulet_nbt.FloatTag( self.parameters.playerHealth )
            healthAttr["Current"] = amulet_nbt.FloatTag( self.parameters.playerHealth )
            healthAttr["Max"] = amulet_nbt.FloatTag( 20.0 )
            healthAttr["Min"] = amulet_nbt.FloatTag( 0.0 )
            attributes.append( healthAttr )
        if not levelFound:
            levelAttr = amulet_nbt.CompoundTag()
            levelAttr["Name"] = amulet_nbt.StringTag( "minecraft:player.level" )
            levelAttr["Base"] = amulet_nbt.FloatTag( self.parameters.playerLevel )
            levelAttr["Current"] = amulet_nbt.FloatTag( self.parameters.playerLevel )
            levelAttr["Max"] = amulet_nbt.FloatTag( 24791.0 )
            levelAttr["Min"] = amulet_nbt.FloatTag( 0.0 )
            attributes.append( levelAttr )
        self.playerNbt["PlayerLevel"] = amulet_nbt.IntTag( int( self.parameters.playerLevel ) )
        self.playerNbt["PlayerLevelProgress"] = amulet_nbt.FloatTag( 0.0 )

    def savePlayerData( self ) -> OperationOutcome:
        if self.playerNbt is None or self.db is None:
            return OperationOutcome(
                result=WorldOperationResult.ErrorNullWorld,
                message="Player data not loaded"
            )
        try:
            self.db.writePlayerNbt( amulet_nbt.NamedTag( self.playerNbt, "" ) )
            return OperationOutcome( result=WorldOperationResult.Success )
        except Exception as error:
            return OperationOutcome(
                result=WorldOperationResult.ErrorWrite,
                message=f"Failed to save player data: {error}"
            )
