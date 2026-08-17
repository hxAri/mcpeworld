from pathlib import Path
from typing import MutableSequence, Optional

from mcpeworld import Bool, Int, Str
from mcpeworld.backup.manager import (
    createBackup,
    exportWorldToMcworld,
    importWorldFromMcworld,
    importWorldFromPath,
    listBackups,
    restoreBackup,
)
import amulet_nbt

from mcpeworld.constant import (
    ContainerTileEntities,
    InfiniteDuration,
    TileEntityCampfire,
    TileEntityGlowItemFrame,
    TileEntityItemFrame,
    WorldsDir,
)
from mcpeworld.nbt.converter import gameItemToNbt, nbtToGameItem
from mcpeworld.database import (
    createEngine,
    createSession,
)
from mcpeworld.database.repository import (
    EffectRepository,
    EnchantmentRepository,
    ItemRepository,
    TrimMaterialRepository,
    TrimPatternRepository,
    UpdateMetaRepository,
)
from mcpeworld.editor.banner import (
    BannerColors,
    BannerPatterns,
    getBannerBaseColor,
    loadBannerPatterns,
    saveBannerPatterns,
)
from mcpeworld.editor.leveldat import (
    DifficultyNames,
    GameModeNames,
    GameRuleKeys,
    GeneratorNames,
)
from mcpeworld.editor.entity import (
    saveEntitiesForChunk,
    setEntityCustomName,
    setEntityHealth,
    setEntityPosition,
)
from mcpeworld.editor.tileentity import (
    editBedColor,
    editCommandBlock,
    editMobSpawner,
    editSignText,
    saveTileEntity,
)
from mcpeworld.editor.world import WorldEditor
from mcpeworld.model.item import ActiveEffect, BEGameItem, Ench
from mcpeworld.model.result import WorldOperationResult
from mcpeworld.model.slot import SlotType
from mcpeworld.model.world import WorldItem
from mcpeworld.network.scraper import WikiScraper
from mcpeworld.ui.ascii import renderArmorFront, renderArmorFull, renderWorldIcon
from mcpeworld.ui.display import (
    formatEntityLabel,
    formatEntityList,
    formatItem,
    formatItemDetailed,
    formatTileEntityList,
    formatTimestamp,
    formatWorldParameters,
)
from mcpeworld.ui.menu import (
    confirmAction,
    promptBool,
    promptChoice,
    promptFloat,
    promptInput,
    promptInt,
    promptSearchItem,
    showListMenu,
    showMenu,
)
from mcpeworld.util.itemcategory import getApplicableEnchantments
from mcpeworld.util.path import scanWorlds


class Application:

    def __init__( self ) -> None:
        self.engine = createEngine()
        self.session = createSession( self.engine )
        self.itemRepository = ItemRepository( self.session )
        self.enchantmentRepository = EnchantmentRepository( self.session )
        self.effectRepository = EffectRepository( self.session )
        self.trimMaterialRepository = TrimMaterialRepository( self.session )
        self.trimPatternRepository = TrimPatternRepository( self.session )
        self.updateMetaRepository = UpdateMetaRepository( self.session )
        self.scraper = WikiScraper(
            self.itemRepository,
            self.enchantmentRepository,
            self.effectRepository,
            self.updateMetaRepository,
            self.trimMaterialRepository,
            self.trimPatternRepository,
        )
        self.editor:Optional[WorldEditor] = None

    def run( self ) -> None:
        self._ensureDirectories()
        self._checkFirstRun()
        self._mainMenu()

    def _ensureDirectories( self ) -> None:
        WorldsDir.mkdir( parents=True, exist_ok=True )

    def _checkFirstRun( self ) -> None:
        if self.scraper.needsUpdate( "enchantments" ):
            print( "First run detected. Populating enchantment database..." )
            self.scraper.updateEnchantments()
        if self.scraper.needsUpdate( "effects" ):
            print( "Populating effect database..." )
            self.scraper.updateEffects()
        if self.scraper.needsUpdate( "trims" ):
            print( "Populating trim database..." )
            self.scraper.updateTrims()

    def _mainMenu( self ) -> None:
        while True:
            worlds = scanWorlds()
            worldLabels = [w.displayName for w in worlds]
            extraOptions = [
                ( len( worlds ) + 1, "Import world from folder" ),
                ( len( worlds ) + 2, "Import .mcworld file" ),
                ( len( worlds ) + 3, "Update database" ),
            ]
            choice = showListMenu( "MCPE World Editor", worldLabels, extraOptions )
            if choice == 0:
                break
            elif 1 <= choice <= len( worlds ):
                self._openWorld( worlds[choice - 1] )
            elif choice == len( worlds ) + 1:
                self._importFromFolder()
            elif choice == len( worlds ) + 2:
                self._importFromMcworld()
            elif choice == len( worlds ) + 3:
                self._updateDatabase()

    def _importFromFolder( self ) -> None:
        path = promptInput( "Enter world folder path" )
        if not path:
            return
        try:
            imported = importWorldFromPath( Path( path ) )
            print( f"World imported to: {imported}" )
        except ( ValueError, FileNotFoundError ) as error:
            print( f"Error: {error}" )

    def _importFromMcworld( self ) -> None:
        path = promptInput( "Enter .mcworld file path" )
        if not path:
            return
        try:
            imported = importWorldFromMcworld( Path( path ) )
            print( f"World imported to: {imported}" )
        except ( ValueError, FileNotFoundError ) as error:
            print( f"Error: {error}" )

    def _exportMcworld( self ) -> None:
        outputPath = exportWorldToMcworld( self.editor.world.folder )
        print( f"Exported to: {outputPath}" )

    def _updateDatabase( self ) -> None:
        choice = showMenu( "Update Database", [
            ( "Update items", "Fetch item data from Minecraft Wiki" ),
            ( "Update enchantments", "Reload enchantment data" ),
            ( "Update effects", "Fetch effect data from Minecraft Wiki" ),
            ( "Update trims", "Fetch trim data from Minecraft Wiki" ),
            ( "Update all", "Fetch everything" ),
        ] )
        if choice == 1:
            self.scraper.updateItems()
        elif choice == 2:
            self.scraper.updateEnchantments()
        elif choice == 3:
            self.scraper.updateEffects()
        elif choice == 4:
            self.scraper.updateTrims()
        elif choice == 5:
            self.scraper.updateAll()

    def _openWorld( self, world:WorldItem ) -> None:
        self.editor = WorldEditor( world )
        outcome = self.editor.open()
        if outcome.result != WorldOperationResult.Success:
            print( f"Error opening world: {outcome.message}" )
            return
        existingBackups = listBackups( world.folder )
        if not existingBackups:
            backupPath = self.editor.backup()
            print( f"Auto-backup created: {backupPath.name}" )
        print( f"\nOpened: {world.displayName}" )
        if world.worldIcon.is_file():
            print( renderWorldIcon( world.worldIcon, width=50 ) )
        params = self.editor.getParameters()
        if params:
            print( formatWorldParameters( params ) )
        self._worldMenu()
        self.editor.close()
        self.editor = None

    def _worldMenu( self ) -> None:
        while True:
            choice = showMenu( self.editor.world.displayName, [
                ( "Edit Level.dat", "World settings, game rules, spawn" ),
                ( "Edit Inventory", "Player inventory slots" ),
                ( "Edit Armor", "Head, chest, legs, boots, offhand" ),
                ( "Edit Ender Chest", "Ender chest inventory" ),
                ( "Edit Effects", "Player status effects" ),
                ( "View Entities", "List and inspect entities" ),
                ( "View Tile Entities", "Signs, spawners, chests, etc." ),
                ( "Export .mcworld", "Export world as .mcworld file" ),
                ( "Backups", "Create or restore backups" ),
            ] )
            if choice == 0:
                break
            elif choice == 1:
                self._editLevelDat()
            elif choice == 2:
                self._editInventory()
            elif choice == 3:
                self._editArmor()
            elif choice == 4:
                self._editEnderChest()
            elif choice == 5:
                self._editEffects()
            elif choice == 6:
                self._viewEntities()
            elif choice == 7:
                self._viewTileEntities()
            elif choice == 8:
                self._exportMcworld()
            elif choice == 9:
                self._manageBackups()

    def _editLevelDat( self ) -> None:
        params = self.editor.getParameters()
        if not params:
            print( "Failed to load world parameters." )
            return
        while True:
            choice = showMenu( "Edit Level.dat", [
                ( "World Name", f"Current: {params.levelName}" ),
                ( "Seed", f"Current: {params.seed}" ),
                ( "Game Mode", f"Current: {GameModeNames.get( params.gameMode, '?' )}" ),
                ( "Difficulty", f"Current: {DifficultyNames.get( params.difficulty, '?' )}" ),
                ( "Time", f"Current: {params.time}" ),
                ( "Spawn Position", f"Current: {params.spawnX}, {params.spawnY}, {params.spawnZ}" ),
                ( "Generator", f"Current: {GeneratorNames.get( params.generator, '?' )}" ),
                ( "Cheats", f"Current: {'On' if params.cheatsEnabled else 'Off'}" ),
                ( "Game Rules", "Toggle game rules" ),
                ( "Player Health", f"Current: {params.playerHealth:.1f}" ),
                ( "Player Level", f"Current: {params.playerLevel:.0f}" ),
            ] )
            if choice == 0:
                break
            changed = True
            if choice == 1:
                params.levelName = promptInput( "World name", params.levelName )
            elif choice == 2:
                params.seed = promptInt( "Seed", params.seed )
            elif choice == 3:
                params.gameMode = promptChoice(
                    "Game Mode",
                    list( GameModeNames.items() ),
                    params.gameMode
                )
            elif choice == 4:
                params.difficulty = promptChoice(
                    "Difficulty",
                    list( DifficultyNames.items() ),
                    params.difficulty
                )
            elif choice == 5:
                params.time = promptInt( "Time (ticks)", params.time )
            elif choice == 6:
                params.spawnX = promptInt( "Spawn X", params.spawnX )
                params.spawnY = promptInt( "Spawn Y", params.spawnY )
                params.spawnZ = promptInt( "Spawn Z", params.spawnZ )
            elif choice == 7:
                params.generator = promptChoice(
                    "Generator",
                    list( GeneratorNames.items() ),
                    params.generator
                )
            elif choice == 8:
                params.cheatsEnabled = promptBool( "Enable cheats", params.cheatsEnabled )
            elif choice == 9:
                self._editGameRules( params )
            elif choice == 10:
                params.playerHealth = promptFloat( "Player health", params.playerHealth )
            elif choice == 11:
                params.playerLevel = promptFloat( "Player level", params.playerLevel )
            else:
                changed = False
            if changed:
                outcome = self.editor.saveParameters()
                if outcome.result == WorldOperationResult.Success:
                    print( "  Saved." )
                else:
                    print( f"  Error saving: {outcome.message}" )

    def _editGameRules( self, params ) -> None:
        ruleFields = list( GameRuleKeys.keys() )
        while True:
            options = []
            for field in ruleFields:
                value = getattr( params, field, False )
                status = "On" if value else "Off"
                options.append( ( field, status ) )
            choice = showMenu( "Game Rules", options )
            if choice == 0:
                break
            if 1 <= choice <= len( ruleFields ):
                field = ruleFields[choice - 1]
                current = getattr( params, field, False )
                setattr( params, field, not current )
                status = "On" if not current else "Off"
                print( f"  {field} set to {status}" )
                self.editor.saveParameters()

    def _editInventory( self ) -> None:
        items = self.editor.getInventory()
        if not items:
            print( "No inventory items found." )
            return
        enchantmentNames = self._getEnchantmentNameMap()
        while True:
            labels = [f"Slot {item.slot}: {formatItem( item, enchantmentNames )}" for item in items]
            choice = showListMenu( "Player Inventory", labels )
            if choice == 0:
                break
            if 1 <= choice <= len( items ):
                self._editSlotItem( items[choice - 1], choice - 1, isArmor=False, isEnderChest=False )
                items = self.editor.getInventory()

    def _editEnderChest( self ) -> None:
        items = self.editor.getEnderChest()
        if not items:
            print( "No ender chest items found." )
            return
        enchantmentNames = self._getEnchantmentNameMap()
        while True:
            labels = [f"Slot {item.slot}: {formatItem( item, enchantmentNames )}" for item in items]
            choice = showListMenu( "Ender Chest", labels )
            if choice == 0:
                break
            if 1 <= choice <= len( items ):
                self._editSlotItem( items[choice - 1], choice - 1, isArmor=False, isEnderChest=True )
                items = self.editor.getEnderChest()

    def _editEffects( self ) -> None:
        effects = self.editor.getActiveEffects()
        effectNameMap = self._getEffectNameMap()
        while True:
            labels = []
            for effect in effects:
                name = effectNameMap.get( effect.effectId, f"Unknown ({effect.effectId})" )
                if effect.duration >= InfiniteDuration:
                    durationStr = "Infinite"
                else:
                    durationSec = effect.duration // 20
                    minutes = durationSec // 60
                    seconds = durationSec % 60
                    durationStr = f"{minutes}:{seconds:02d}"
                labels.append(
                    f"{name} - Level {effect.amplifier + 1} ({durationStr})"
                )
            extraOptions = [
                ( len( effects ) + 1, "Add effect" ),
                ( len( effects ) + 2, "Clear all effects" ),
            ]
            choice = showListMenu( "Active Effects", labels, extraOptions )
            if choice == 0:
                break
            elif 1 <= choice <= len( effects ):
                self._editSingleEffect( effects, choice - 1, effectNameMap )
            elif choice == len( effects ) + 1:
                self._addEffect( effects, effectNameMap )
            elif choice == len( effects ) + 2:
                if effects and confirmAction( "Remove all active effects?" ):
                    effects.clear()
                    outcome = self.editor.setActiveEffects( effects )
                    if outcome.result == WorldOperationResult.Success:
                        print( "  All effects cleared." )
                    else:
                        print( f"  Error: {outcome.message}" )

    def _editSingleEffect( self, effects:MutableSequence[ActiveEffect], index:Int, effectNameMap:dict ) -> None:
        effect = effects[index]
        name = effectNameMap.get( effect.effectId, f"Unknown ({effect.effectId})" )
        isInfinite = effect.duration >= InfiniteDuration
        if isInfinite:
            durationDisplay = "Infinite"
        else:
            durationSec = effect.duration // 20
            durationDisplay = f"{durationSec}s ({effect.duration} ticks)"
        print( f"\n  {name}" )
        print( f"  Level: {effect.amplifier + 1}" )
        print( f"  Duration: {durationDisplay}" )
        choice = showMenu( f"Edit {name}", [
            ( "Change level", f"Current: {effect.amplifier + 1}" ),
            ( "Change duration", f"Current: {durationDisplay}" ),
            ( "Set infinite duration", "" ),
            ( "Remove effect", "" ),
        ] )
        if choice == 1:
            level = promptInt( "Effect level (1-255)", effect.amplifier + 1 )
            effect.amplifier = max( 0, min( 255, level - 1 ) )
            outcome = self.editor.setActiveEffects( effects )
            if outcome.result == WorldOperationResult.Success:
                print( "  Effect updated." )
            else:
                print( f"  Error: {outcome.message}" )
        elif choice == 2:
            effect.duration = self._promptEffectDurationValue( effect.duration )
            outcome = self.editor.setActiveEffects( effects )
            if outcome.result == WorldOperationResult.Success:
                print( "  Duration updated." )
            else:
                print( f"  Error: {outcome.message}" )
        elif choice == 3:
            effect.duration = InfiniteDuration
            outcome = self.editor.setActiveEffects( effects )
            if outcome.result == WorldOperationResult.Success:
                print( "  Duration set to infinite." )
            else:
                print( f"  Error: {outcome.message}" )
        elif choice == 4:
            effects.pop( index )
            outcome = self.editor.setActiveEffects( effects )
            if outcome.result == WorldOperationResult.Success:
                print( f"  {name} removed." )
            else:
                print( f"  Error: {outcome.message}" )

    def _promptEffectDurationValue( self, currentTicks:Int = 600 ) -> Int:
        isInfinite = currentTicks >= InfiniteDuration
        defaultStr = "infinite" if isInfinite else str( currentTicks // 20 )
        while True:
            raw = promptInput( "Duration in seconds (or 'infinite')", defaultStr )
            if raw.lower() in ( "infinite", "inf", "forever", "max" ):
                return InfiniteDuration
            try:
                return int( raw ) * 20
            except ValueError:
                print( "  Enter a number or 'infinite'." )

    def _promptEffectDuration( self ) -> Int:
        return self._promptEffectDurationValue( 600 )

    def _addEffect( self, effects:MutableSequence[ActiveEffect], effectNameMap:dict ) -> None:
        allEffects = self.effectRepository.findAll()
        if not allEffects:
            effectId = promptInt( "Effect numeric ID" )
            level = promptInt( "Level", 1 )
            duration = self._promptEffectDuration()
            effects.append( ActiveEffect(
                effectId=effectId,
                amplifier=max( 0, level - 1 ),
                duration=duration,
            ) )
            outcome = self.editor.setActiveEffects( effects )
            if outcome.result == WorldOperationResult.Success:
                print( "  Effect added." )
            else:
                print( f"  Error: {outcome.message}" )
            return
        effectLabels = [f"{r.fullName} ({r.idName})" for r in allEffects]
        choice = showListMenu( "Select Effect", effectLabels )
        if choice == 0:
            return
        if 1 <= choice <= len( allEffects ):
            record = allEffects[choice - 1]
            level = promptInt( "Level (1-255)", 1 )
            duration = self._promptEffectDuration()
            effects.append( ActiveEffect(
                effectId=record.numericId,
                amplifier=max( 0, min( 255, level - 1 ) ),
                duration=duration,
            ) )
            outcome = self.editor.setActiveEffects( effects )
            if outcome.result == WorldOperationResult.Success:
                name = effectNameMap.get( record.numericId, record.fullName )
                print( f"  {name} added." )
            else:
                print( f"  Error: {outcome.message}" )

    def _getEffectNameMap( self ) -> dict:
        allEffects = self.effectRepository.findAll()
        return {r.numericId:r.fullName for r in allEffects}

    def _editArmor( self ) -> None:
        armorItems = self.editor.getArmor()
        enchantmentNames = self._getEnchantmentNameMap()
        slotNames = ["Head", "Chest Plate", "Leggings", "Boots", "Off Hand"]
        while True:
            # print( renderArmorFull( armorItems ) )
            labels = []
            for i, item in enumerate( armorItems ):
                name = slotNames[i] if i < len( slotNames ) else f"Slot {i}"
                labels.append( f"{name}: {formatItem( item, enchantmentNames )}" )
            choice = showListMenu( "Armor Slots", labels )
            if choice == 0:
                break
            if 1 <= choice <= len( armorItems ):
                slotIndex = choice - 1
                slotType = SlotType( slotIndex ) if slotIndex < 5 else SlotType.CommonSlot
                self._editArmorSlotItem( armorItems[slotIndex], slotType )
                armorItems = self.editor.getArmor()

    def _editSlotItem( self, item:BEGameItem, listIndex:Int, isArmor:Bool, isEnderChest:Bool ) -> None:
        enchantmentNames = self._getEnchantmentNameMap()
        print( f"\n{formatItemDetailed( item, enchantmentNames )}" )
        choice = showMenu( "Edit Slot", [
            ( "Change item", "" ),
            ( "Set stack size", "" ),
            ( "Set damage value", "" ),
            ( "Set custom name", "" ),
            ( "Add enchantment", "" ),
            ( "Clear enchantments", "" ),
            ( "Clear slot", "" ),
        ] )
        if choice == 0:
            return
        slotIndex = item.slot if item.slot >= 0 else listIndex
        if choice == 1:
            newItem = self._selectItem()
            if newItem:
                newItem.slot = slotIndex
                newItem.enchantments = item.enchantments
                if isEnderChest:
                    self.editor.backup()
                    self.editor.setEnderChestSlot( slotIndex, newItem )
                else:
                    self.editor.backup()
                    self.editor.setInventorySlot( slotIndex, newItem )
        elif choice == 2:
            item.stackSize = promptInt( "Stack size", item.stackSize )
            self._saveSlotBack( item, slotIndex, isEnderChest )
        elif choice == 3:
            item.damage = promptInt( "Damage value", item.damage )
            self._saveSlotBack( item, slotIndex, isEnderChest )
        elif choice == 4:
            item.displayName = promptInput( "Custom display name", item.displayName )
            self._saveSlotBack( item, slotIndex, isEnderChest )
        elif choice == 5:
            self._addEnchantment( item )
            self._saveSlotBack( item, slotIndex, isEnderChest )
        elif choice == 6:
            item.enchantments.clear()
            self._saveSlotBack( item, slotIndex, isEnderChest )
        elif choice == 7:
            if confirmAction( "Clear this slot?" ):
                self.editor.backup()
                self.editor.clearInventorySlot( slotIndex )

    def _editArmorSlotItem( self, item:BEGameItem, slotType:SlotType ) -> None:
        enchantmentNames = self._getEnchantmentNameMap()
        print( f"\n{formatItemDetailed( item, enchantmentNames )}" )
        if item.trimMaterial and item.trimPattern:
            print( f"  Trim       : {item.trimPattern.title()} ({item.trimPattern}) / {item.trimMaterial.title()} ({item.trimMaterial})" )
        choice = showMenu( "Edit Armor Slot", [
            ( "Change item", "" ),
            ( "Add enchantment", "" ),
            ( "Clear enchantments", "" ),
            ( "Edit trim", "Change armor trim pattern/material" ),
            ( "Clear trim", "" ),
            ( "Clear slot", "" ),
        ] )
        if choice == 0:
            return
        if choice == 1:
            newItem = self._selectItem()
            if newItem:
                newItem.enchantments = item.enchantments
                newItem.trimMaterial = item.trimMaterial
                newItem.trimPattern = item.trimPattern
                self.editor.backup()
                self.editor.setArmorSlot( slotType, newItem )
        elif choice == 2:
            self._addEnchantment( item )
            self.editor.backup()
            self.editor.setArmorSlot( slotType, item )
        elif choice == 3:
            item.enchantments.clear()
            self.editor.backup()
            self.editor.setArmorSlot( slotType, item )
        elif choice == 4:
            self._editArmorTrim( item, slotType )
        elif choice == 5:
            item.trimMaterial = ""
            item.trimPattern = ""
            self.editor.backup()
            self.editor.setArmorSlot( slotType, item )
            print( "  Trim cleared." )
        elif choice == 6:
            if confirmAction( "Clear this slot?" ):
                self.editor.backup()
                self.editor.setArmorSlot( slotType, BEGameItem() )

    def _editArmorTrim( self, item:BEGameItem, slotType:SlotType ) -> None:
        if item.isEmpty:
            print( "  Cannot add trim to empty slot." )
            return
        patterns = self.trimPatternRepository.findAll()
        if not patterns:
            print( "  No trim patterns in database. Run 'Update database' first." )
            return
        materials = self.trimMaterialRepository.findAll()
        if not materials:
            print( "  No trim materials in database. Run 'Update database' first." )
            return
        patternLabels = [f"{r.fullName} ({r.idName})" for r in patterns]
        patternChoice = showListMenu( "Select Trim Pattern", patternLabels )
        if patternChoice == 0:
            return
        if patternChoice < 1 or patternChoice > len( patterns ):
            return
        selectedPattern = patterns[patternChoice - 1]
        materialLabels = [f"{r.fullName} ({r.idName})" for r in materials]
        materialChoice = showListMenu( "Select Trim Material", materialLabels )
        if materialChoice == 0:
            return
        if materialChoice < 1 or materialChoice > len( materials ):
            return
        selectedMaterial = materials[materialChoice - 1]
        item.trimPattern = selectedPattern.idName
        item.trimMaterial = selectedMaterial.idName
        self.editor.backup()
        outcome = self.editor.setArmorSlot( slotType, item )
        if outcome.result == WorldOperationResult.Success:
            print( f"  Trim set: {selectedPattern.fullName} / {selectedMaterial.fullName}" )
        else:
            print( f"  Error: {outcome.message}" )

    def _saveSlotBack( self, item:BEGameItem, slotIndex:Int, isEnderChest:Bool ) -> None:
        self.editor.backup()
        if isEnderChest:
            self.editor.setEnderChestSlot( slotIndex, item )
        else:
            self.editor.setInventorySlot( slotIndex, item )

    def _selectItem( self ) -> Optional[BEGameItem]:
        allItems = self.itemRepository.findAll()
        if not allItems:
            print( "No items in database. Run 'Update database' first." )
            itemName = promptInput( "Enter item ID manually (e.g. diamond_sword)" )
            if itemName:
                return BEGameItem( itemName=itemName )
            return None
        itemNames = [f"{r.fullName} ({r.idName})" for r in allItems]
        selected = promptSearchItem( "Search item (tab to autocomplete)", itemNames )
        if not selected:
            return None
        for record in allItems:
            if selected == f"{record.fullName} ({record.idName})" or selected == record.idName:
                return BEGameItem(
                    itemName=record.idName,
                    stackSize=1,
                    belongsTo=record.namespace,
                )
        if "(" in selected and selected.endswith( ")" ):
            idPart = selected.rsplit( "(", 1 )[1].rstrip( ")" )
            return BEGameItem( itemName=idPart )
        return BEGameItem( itemName=selected )

    def _addEnchantment( self, item:BEGameItem ) -> None:
        allEnchants = self.enchantmentRepository.findAll()
        if not allEnchants:
            enchId = promptInt( "Enchantment numeric ID" )
            level = promptInt( "Level", 1 )
            item.enchantments.append( Ench( enchantId=enchId, level=level ) )
            return
        applicableIds = set( getApplicableEnchantments( item.itemName ) )
        filtered = [r for r in allEnchants if r.numericId in applicableIds]
        if not filtered:
            filtered = allEnchants
        enchLabels = [f"{r.fullName} ({r.idName})" for r in filtered]
        choice = showListMenu( "Select Enchantment", enchLabels )
        if choice == 0:
            return
        if 1 <= choice <= len( filtered ):
            record = filtered[choice - 1]
            level = promptInt( f"Level (max {record.maxLevel})", 1 )
            item.enchantments.append( Ench( enchantId=record.numericId, level=level ) )

    def _getEnchantmentNameMap( self ) -> dict:
        allEnchants = self.enchantmentRepository.findAll()
        return {r.numericId:r.fullName for r in allEnchants}

    def _viewEntities( self ) -> None:
        print( "\nLoading entities..." )
        entities = self.editor.getEntities()
        if not entities:
            print( "No entities found." )
            return
        while True:
            labels = [formatEntityLabel( e ) for e in entities]
            choice = showListMenu( f"Entities ({len( entities )} found)", labels )
            if choice == 0 or choice > len( entities ):
                break
            self._editEntity( entities, choice - 1 )

    def _editEntity( self, entities, index:Int ) -> None:
        entity = entities[index]
        self._printEntityDetail( entity )
        healthDesc = ""
        if entity.health > 0:
            healthDesc = f"Current: {entity.health:.0f}"
        choice = showMenu( f"Edit {entity.shortId.replace( '_', ' ' ).title()}", [
            ( "Set health", healthDesc ),
            ( "Set custom name", f"Current: {entity.customName}" if entity.customName else "" ),
            ( "Set position", f"Current: {entity.position.x:.0f}, {entity.position.y:.0f}, {entity.position.z:.0f}" ),
            ( "Delete entity", "Remove from world" ),
        ] )
        if choice == 0:
            return
        if choice == 1:
            newHealth = promptFloat( "Health", entity.health )
            self.editor.backup()
            setEntityHealth( entity.nbtData, newHealth )
            entity.health = newHealth
            saveEntitiesForChunk( self.editor.db, entities, entity.chunkKey )
            print( f"  Health set to {newHealth:.0f}." )
        elif choice == 2:
            newName = promptInput( "Custom name (empty to clear)", entity.customName )
            self.editor.backup()
            setEntityCustomName( entity.nbtData, newName )
            entity.customName = newName
            saveEntitiesForChunk( self.editor.db, entities, entity.chunkKey )
            if newName:
                print( f"  Name set to \"{newName}\"." )
            else:
                print( "  Custom name cleared." )
        elif choice == 3:
            newX = promptFloat( "X", entity.position.x )
            newY = promptFloat( "Y", entity.position.y )
            newZ = promptFloat( "Z", entity.position.z )
            self.editor.backup()
            setEntityPosition( entity.nbtData, newX, newY, newZ )
            entity.position.x = newX
            entity.position.y = newY
            entity.position.z = newZ
            saveEntitiesForChunk( self.editor.db, entities, entity.chunkKey )
            print( f"  Position set to {newX:.0f}, {newY:.0f}, {newZ:.0f}." )
        elif choice == 4:
            if confirmAction( f"Delete {entity.displayName}?" ):
                self.editor.backup()
                entities.pop( index )
                saveEntitiesForChunk( self.editor.db, entities, entity.chunkKey )
                print( "  Entity deleted." )

    def _printEntityDetail( self, entity ) -> None:
        name = entity.shortId.replace( "_", " " ).title()
        print( f"\n  Name       : {name}" )
        print( f"  Identifier : {entity.identifier}" )
        print( f"  Position   : {entity.position.x:.1f}, {entity.position.y:.1f}, {entity.position.z:.1f}" )
        print( f"  Unique ID  : {entity.uniqueId}" )
        if entity.customName:
            print( f"  Custom Name: {entity.customName}" )
        if entity.health > 0:
            if entity.maxHealth > 0:
                print( f"  Health     : {entity.health:.1f} / {entity.maxHealth:.1f}" )
            else:
                print( f"  Health     : {entity.health:.1f}" )
        if entity.isBaby:
            print( f"  Baby       : Yes" )
        if entity.isTamed:
            print( f"  Tamed      : Yes" )
        if entity.variant > 0:
            print( f"  Variant    : {entity.variant}" )
        if entity.color > 0:
            print( f"  Color      : {entity.color}" )
        compound = entity.nbtData
        if compound is None:
            return
        self._printEntityEquipment( compound )
        if entity.identifier == "minecraft:item" and "Item" in compound:
            itemTag = compound["Item"]
            if isinstance( itemTag, amulet_nbt.CompoundTag ):
                item = nbtToGameItem( itemTag )
                if item.itemName:
                    label = item.itemName
                    if item.stackSize > 1:
                        label += f" x{item.stackSize}"
                    print( f"  Item       : {label}" )
        if "OwnerNew" in compound:
            ownerId = int( compound["OwnerNew"] )
            if ownerId > 0:
                print( f"  Owner ID   : {ownerId}" )
        if "Sitting" in compound and int( compound["Sitting"] ):
            print( f"  Sitting    : Yes" )
        if "Strength" in compound:
            strength = int( compound["Strength"] )
            if strength > 0:
                print( f"  Strength   : {strength}" )
        if "TradeExperience" in compound:
            tradeXp = int( compound["TradeExperience"] )
            if tradeXp > 0:
                print( f"  Trade XP   : {tradeXp}" )
        if "TradeTier" in compound:
            tradeTier = int( compound["TradeTier"] )
            if tradeTier > 0:
                print( f"  Trade Tier : {tradeTier}" )

    def _printEntityEquipment( self, compound ) -> None:
        if "Armor" in compound:
            armorList = compound["Armor"]
            if hasattr( armorList, "__len__" ):
                pieces = []
                for armor in armorList:
                    if "Name" in armor:
                        itemName = armor["Name"].py_str
                        if itemName and itemName != "minecraft:air":
                            if itemName.startswith( "minecraft:" ):
                                itemName = itemName[10:]
                            pieces.append( itemName )
                if pieces:
                    print( f"  Armor      : {', '.join( pieces )}" )
        if "Mainhand" in compound:
            mainhand = compound["Mainhand"]
            if hasattr( mainhand, "__len__" ) and len( mainhand ) > 0:
                slot = mainhand[0]
                if "Name" in slot:
                    itemName = slot["Name"].py_str
                    if itemName and itemName != "minecraft:air":
                        if itemName.startswith( "minecraft:" ):
                            itemName = itemName[10:]
                        print( f"  Mainhand   : {itemName}" )
        if "Offhand" in compound:
            offhand = compound["Offhand"]
            if hasattr( offhand, "__len__" ) and len( offhand ) > 0:
                slot = offhand[0]
                if "Name" in slot:
                    itemName = slot["Name"].py_str
                    if itemName and itemName != "minecraft:air":
                        if itemName.startswith( "minecraft:" ):
                            itemName = itemName[10:]
                        print( f"  Offhand    : {itemName}" )

    def _viewTileEntities( self ) -> None:
        print( "\nLoading tile entities..." )
        tiles = self.editor.getTileEntities()
        if not tiles:
            print( "No tile entities found." )
            return
        tiles = [t for t in tiles if t.tileIdentifier]
        if not tiles:
            print( "No valid tile entities found." )
            return
        print( f"  Found {len( tiles )} tile entities." )
        while True:
            tileTypes = sorted( set( t.tileIdentifier for t in tiles ) )
            typeLabels = [f"{t} ({sum( 1 for x in tiles if x.tileIdentifier == t )})" for t in tileTypes]
            typeChoice = showListMenu( f"Tile Entity Types ({len( tileTypes )})", typeLabels )
            if typeChoice == 0:
                break
            if 1 <= typeChoice <= len( tileTypes ):
                selectedType = tileTypes[typeChoice - 1]
                filtered = [t for t in tiles if t.tileIdentifier == selectedType]
                self._browseTileEntities( filtered, selectedType )

    def _browseTileEntities( self, tiles:MutableSequence, tileType:Str ) -> None:
        while True:
            labels = []
            for t in tiles:
                pos = f"({t.position.x:.0f}, {t.position.y:.0f}, {t.position.z:.0f})"
                overlay = f" - {t.overlayData}" if t.overlayData else ""
                labels.append( f"{pos}{overlay}" )
            choice = showListMenu( f"{tileType} Tile Entities", labels )
            if choice == 0:
                break
            if 1 <= choice <= len( tiles ):
                self._editTileEntity( tiles[choice - 1] )

    def _editTileEntity( self, tile ) -> None:
        tileId = tile.tileIdentifier
        compound = tile.nbtData
        if compound is None:
            print( "No NBT data available." )
            return
        from mcpeworld.constant import (
            TileEntitySign,
            TileEntityHangingSign,
            TileEntityCommandBlock,
            TileEntityMobSpawner,
            TileEntityBed,
            TileEntityBanner,
        )
        if tileId in ( TileEntitySign, TileEntityHangingSign ):
            self._editSign( tile )
        elif tileId == TileEntityCommandBlock:
            self._editCmdBlock( tile )
        elif tileId == TileEntityMobSpawner:
            self._editSpawner( tile )
        elif tileId == TileEntityBed:
            self._editBed( tile )
        elif tileId == TileEntityBanner:
            self._editBannerTile( tile )
        elif tileId in ContainerTileEntities:
            self._editContainerTileEntity( tile )
        elif tileId == TileEntityCampfire:
            self._editCampfireTileEntity( tile )
        elif tileId in ( TileEntityItemFrame, TileEntityGlowItemFrame ):
            self._editItemFrameTileEntity( tile )
        else:
            print( f"\n  Type: {tileId}" )
            print( f"  Position: {tile.position.x:.0f}, {tile.position.y:.0f}, {tile.position.z:.0f}" )
            if tile.overlayData:
                print( f"  Info: {tile.overlayData}" )

    def _editSign( self, tile ) -> None:
        compound = tile.nbtData
        print( f"\n  Current sign text:" )
        if tile.overlayData:
            print( f"  {tile.overlayData}" )
        choice = showMenu( "Edit Sign", [
            ( "Edit front text", "" ),
            ( "Edit back text", "" ),
        ] )
        if choice == 1:
            text = promptInput( "Front text" )
            if text:
                self.editor.backup()
                editSignText( compound, frontText=text )
                saveTileEntity( self.editor.db, tile )
                print( "  Sign updated." )
        elif choice == 2:
            text = promptInput( "Back text" )
            if text:
                self.editor.backup()
                editSignText( compound, backText=text )
                saveTileEntity( self.editor.db, tile )
                print( "  Sign updated." )

    def _editCmdBlock( self, tile ) -> None:
        compound = tile.nbtData
        currentCmd = tile.overlayData or ""
        print( f"\n  Current command: {currentCmd}" )
        newCmd = promptInput( "New command", currentCmd )
        if newCmd != currentCmd:
            self.editor.backup()
            editCommandBlock( compound, newCmd )
            saveTileEntity( self.editor.db, tile )
            print( "  Command block updated." )

    def _editSpawner( self, tile ) -> None:
        compound = tile.nbtData
        currentEntity = tile.overlayData or ""
        print( f"\n  Current entity: {currentEntity}" )
        newEntity = promptInput( "Entity identifier (e.g. minecraft:zombie)", currentEntity )
        if newEntity != currentEntity:
            self.editor.backup()
            editMobSpawner( compound, newEntity )
            saveTileEntity( self.editor.db, tile )
            print( "  Mob spawner updated." )

    def _editBed( self, tile ) -> None:
        compound = tile.nbtData
        print( "\n  Bed colors:" )
        for colorId, colorName in BannerColors.items():
            print( f"    [{colorId}] {colorName}" )
        newColor = promptInt( "Bed color", 0 )
        if 0 <= newColor <= 15:
            self.editor.backup()
            editBedColor( compound, newColor )
            saveTileEntity( self.editor.db, tile )
            print( "  Bed color updated." )

    def _editBannerTile( self, tile ) -> None:
        compound = tile.nbtData
        baseColor = getBannerBaseColor( compound )
        patterns = loadBannerPatterns( compound )
        print( f"\n  Base color: {BannerColors.get( baseColor, str( baseColor ) )}" )
        if patterns:
            print( "  Patterns:" )
            for code, color in patterns:
                patternName = BannerPatterns.get( code, code )
                colorName = BannerColors.get( color, str( color ) )
                print( f"    {patternName} - {colorName}" )
        while True:
            choice = showMenu( "Edit Banner", [
                ( "Change base color", "" ),
                ( "Add pattern", "" ),
                ( "Remove last pattern", "" ),
                ( "Clear all patterns", "" ),
                ( "Save", "" ),
            ] )
            if choice == 0:
                break
            elif choice == 1:
                print( "\n  Colors:" )
                for colorId, colorName in BannerColors.items():
                    print( f"    [{colorId}] {colorName}" )
                baseColor = promptInt( "Base color", baseColor )
            elif choice == 2:
                print( "\n  Pattern codes:" )
                patternCodes = list( BannerPatterns.keys() )
                for i, code in enumerate( patternCodes ):
                    print( f"    [{i + 1}] {code} - {BannerPatterns[code]}" )
                patternIdx = promptInt( "Pattern number", 1 ) - 1
                if 0 <= patternIdx < len( patternCodes ):
                    patternColor = promptInt( "Pattern color (0-15)", 0 )
                    patterns.append( ( patternCodes[patternIdx], patternColor ) )
            elif choice == 3:
                if patterns:
                    patterns.pop()
                    print( "  Last pattern removed." )
            elif choice == 4:
                patterns.clear()
                print( "  All patterns cleared." )
            elif choice == 5:
                self.editor.backup()
                saveBannerPatterns( compound, baseColor, patterns )
                saveTileEntity( self.editor.db, tile )
                print( "  Banner saved." )
                break

    def _editContainerTileEntity( self, tile ) -> None:
        compound = tile.nbtData
        enchantmentNames = self._getEnchantmentNameMap()
        while True:
            items = []
            if "Items" in compound:
                itemsList = compound["Items"]
                if isinstance( itemsList, amulet_nbt.ListTag ):
                    for itemTag in itemsList:
                        if isinstance( itemTag, amulet_nbt.CompoundTag ):
                            items.append( nbtToGameItem( itemTag ) )
            labels = []
            for item in items:
                labels.append( f"Slot {item.slot}: {formatItem( item, enchantmentNames )}" )
            extraOptions = [
                ( len( items ) + 1, "Add item to container" ),
                ( len( items ) + 2, "Clear all items" ),
            ]
            choice = showListMenu(
                f"{tile.tileIdentifier} at ({tile.position.x:.0f}, {tile.position.y:.0f}, {tile.position.z:.0f})",
                labels,
                extraOptions,
            )
            if choice == 0:
                break
            elif 1 <= choice <= len( items ):
                self._editContainerSlot( tile, items, choice - 1 )
            elif choice == len( items ) + 1:
                self._addContainerItem( tile )
            elif choice == len( items ) + 2:
                if confirmAction( "Clear all items from this container?" ):
                    self.editor.backup()
                    compound["Items"] = amulet_nbt.ListTag()
                    saveTileEntity( self.editor.db, tile )
                    tile.overlayData = "Empty"
                    print( "  Container cleared." )

    def _editContainerSlot( self, tile, items, index:Int ) -> None:
        item = items[index]
        enchantmentNames = self._getEnchantmentNameMap()
        print( f"\n{formatItemDetailed( item, enchantmentNames )}" )
        choice = showMenu( "Edit Container Slot", [
            ( "Change item", "" ),
            ( "Set stack size", "" ),
            ( "Set damage value", "" ),
            ( "Add enchantment", "" ),
            ( "Clear slot", "" ),
        ] )
        if choice == 0:
            return
        compound = tile.nbtData
        if choice == 1:
            newItem = self._selectItem()
            if newItem:
                newItem.slot = item.slot
                newItem.enchantments = item.enchantments
                items[index] = newItem
                self._saveContainerItems( tile, items )
        elif choice == 2:
            item.stackSize = promptInt( "Stack size", item.stackSize )
            self._saveContainerItems( tile, items )
        elif choice == 3:
            item.damage = promptInt( "Damage value", item.damage )
            self._saveContainerItems( tile, items )
        elif choice == 4:
            self._addEnchantment( item )
            self._saveContainerItems( tile, items )
        elif choice == 5:
            if confirmAction( "Clear this slot?" ):
                items.pop( index )
                self._saveContainerItems( tile, items )

    def _addContainerItem( self, tile ) -> None:
        newItem = self._selectItem()
        if not newItem:
            return
        slotNum = promptInt( "Slot number", 0 )
        newItem.slot = slotNum
        newItem.stackSize = promptInt( "Stack size", 1 )
        compound = tile.nbtData
        items = []
        if "Items" in compound:
            itemsList = compound["Items"]
            if isinstance( itemsList, amulet_nbt.ListTag ):
                for itemTag in itemsList:
                    if isinstance( itemTag, amulet_nbt.CompoundTag ):
                        items.append( nbtToGameItem( itemTag ) )
        items.append( newItem )
        self._saveContainerItems( tile, items )
        print( f"  Item added to slot {slotNum}." )

    def _saveContainerItems( self, tile, items ) -> None:
        self.editor.backup()
        compound = tile.nbtData
        newList = amulet_nbt.ListTag()
        for item in items:
            newList.append( gameItemToNbt( item ) )
        compound["Items"] = newList
        saveTileEntity( self.editor.db, tile )
        count = len( items )
        tile.overlayData = f"{count} items" if count > 0 else "Empty"

    def _editCampfireTileEntity( self, tile ) -> None:
        compound = tile.nbtData
        slotKeys = ["Item1", "Item2", "Item3", "Item4"]
        while True:
            labels = []
            for key in slotKeys:
                if key in compound:
                    itemTag = compound[key]
                    if isinstance( itemTag, amulet_nbt.CompoundTag ):
                        item = nbtToGameItem( itemTag )
                        if item.itemName:
                            labels.append( f"{key}: {item.itemName}" )
                            continue
                labels.append( f"{key}: (Empty)" )
            extraOptions = [( 5, "Clear all slots" )]
            choice = showListMenu(
                f"Campfire at ({tile.position.x:.0f}, {tile.position.y:.0f}, {tile.position.z:.0f})",
                labels,
                extraOptions,
            )
            if choice == 0:
                break
            elif 1 <= choice <= 4:
                key = slotKeys[choice - 1]
                self._editCampfireSlot( tile, key )
            elif choice == 5:
                if confirmAction( "Clear all campfire slots?" ):
                    self.editor.backup()
                    for key in slotKeys:
                        if key in compound:
                            del compound[key]
                    saveTileEntity( self.editor.db, tile )
                    tile.overlayData = "Empty"
                    print( "  Campfire cleared." )

    def _editCampfireSlot( self, tile, slotKey:Str ) -> None:
        compound = tile.nbtData
        hasItem = slotKey in compound and isinstance( compound[slotKey], amulet_nbt.CompoundTag )
        options = [( "Set item", "" )]
        if hasItem:
            options.append( ( "Clear slot", "" ) )
        choice = showMenu( f"Edit {slotKey}", options )
        if choice == 1:
            newItem = self._selectItem()
            if newItem:
                self.editor.backup()
                compound[slotKey] = gameItemToNbt( newItem )
                saveTileEntity( self.editor.db, tile )
                print( f"  {slotKey} updated." )
        elif choice == 2 and hasItem:
            self.editor.backup()
            del compound[slotKey]
            saveTileEntity( self.editor.db, tile )
            print( f"  {slotKey} cleared." )

    def _editItemFrameTileEntity( self, tile ) -> None:
        compound = tile.nbtData
        currentItem = ""
        if "Item" in compound:
            itemTag = compound["Item"]
            if isinstance( itemTag, amulet_nbt.CompoundTag ):
                item = nbtToGameItem( itemTag )
                currentItem = item.itemName
        print( f"\n  Current item: {currentItem if currentItem else '(empty)'}" )
        choice = showMenu( "Edit Item Frame", [
            ( "Set item", "" ),
            ( "Clear item", "" ),
        ] )
        if choice == 1:
            newItem = self._selectItem()
            if newItem:
                self.editor.backup()
                compound["Item"] = gameItemToNbt( newItem )
                saveTileEntity( self.editor.db, tile )
                tile.overlayData = newItem.itemName
                print( f"  Item frame updated: {newItem.itemName}" )
        elif choice == 2:
            if "Item" in compound:
                self.editor.backup()
                del compound["Item"]
                saveTileEntity( self.editor.db, tile )
                tile.overlayData = "(empty frame)"
                print( "  Item frame cleared." )

    def _manageBackups( self ) -> None:
        while True:
            choice = showMenu( "Backup Management", [
                ( "Create backup", "Backup current world state" ),
                ( "Restore from backup", "Restore a previous backup" ),
                ( "List backups", "Show available backups" ),
            ] )
            if choice == 0:
                break
            elif choice == 1:
                path = self.editor.backup()
                print( f"Backup created: {path.name}" )
            elif choice == 2:
                backups = listBackups( self.editor.world.folder )
                if not backups:
                    print( "No backups available." )
                    continue
                labels = [b.name for b in backups]
                bChoice = showListMenu( "Select Backup to Restore", labels )
                if bChoice == 0:
                    continue
                if 1 <= bChoice <= len( backups ):
                    if confirmAction( "Restore this backup? Current state will be overwritten." ):
                        restoreBackup( backups[bChoice - 1], self.editor.world.folder )
                        print( "Backup restored. Re-opening world..." )
                        self.editor.close()
                        outcome = self.editor.open()
                        if outcome.result != WorldOperationResult.Success:
                            print( f"Error re-opening: {outcome.message}" )
                            break
            elif choice == 3:
                backups = listBackups( self.editor.world.folder )
                if not backups:
                    print( "No backups available." )
                else:
                    for b in backups:
                        print( f"  {b.name}" )
