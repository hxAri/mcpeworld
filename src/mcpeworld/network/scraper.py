import re
from datetime import datetime, timezone
from typing import MutableMapping, MutableSequence, Optional, Tuple

from bs4 import BeautifulSoup, Tag
from curl_cffi import requests as curlRequests

from mcpeworld import Bool, Int, Str
from mcpeworld.database.model import (
    EffectRecord,
    EnchantmentRecord,
    ItemRecord,
    TrimMaterialRecord,
    TrimPatternRecord,
)
from mcpeworld.database.repository import (
    EffectRepository,
    EnchantmentRepository,
    ItemRepository,
    TrimMaterialRepository,
    TrimPatternRepository,
    UpdateMetaRepository,
)

import json

BedrockDataValuesUrl:Str = "https://minecraft.wiki/w/Bedrock_Edition_data_values"
BedrockItemsUrl:Str = "https://minecraft.wiki/w/Bedrock_Edition_data_values/Items"
EffectPageUrl:Str = "https://minecraft.wiki/w/Effect"
EnchantmentPageUrl:Str = "https://wiki.bedrock.dev/items/enchantments"
WikiApiUrl:Str = "https://minecraft.wiki/api.php"

BedrockEnchantmentIds:MutableMapping[Int, Tuple[Str, Str, Int]] = {
    0: ( "protection", "Protection", 4 ),
    1: ( "fire_protection", "Fire Protection", 4 ),
    2: ( "feather_falling", "Feather Falling", 4 ),
    3: ( "blast_protection", "Blast Protection", 4 ),
    4: ( "projectile_protection", "Projectile Protection", 4 ),
    5: ( "thorns", "Thorns", 3 ),
    6: ( "respiration", "Respiration", 3 ),
    7: ( "depth_strider", "Depth Strider", 3 ),
    8: ( "aqua_affinity", "Aqua Affinity", 1 ),
    9: ( "sharpness", "Sharpness", 5 ),
    10: ( "smite", "Smite", 5 ),
    11: ( "bane_of_arthropods", "Bane of Arthropods", 5 ),
    12: ( "knockback", "Knockback", 2 ),
    13: ( "fire_aspect", "Fire Aspect", 2 ),
    14: ( "looting", "Looting", 3 ),
    15: ( "efficiency", "Efficiency", 5 ),
    16: ( "silk_touch", "Silk Touch", 1 ),
    17: ( "unbreaking", "Unbreaking", 3 ),
    18: ( "fortune", "Fortune", 3 ),
    19: ( "power", "Power", 5 ),
    20: ( "punch", "Punch", 2 ),
    21: ( "flame", "Flame", 1 ),
    22: ( "infinity", "Infinity", 1 ),
    23: ( "luck_of_the_sea", "Luck of the Sea", 3 ),
    24: ( "lure", "Lure", 3 ),
    25: ( "frost_walker", "Frost Walker", 2 ),
    26: ( "mending", "Mending", 1 ),
    27: ( "curse_of_binding", "Curse of Binding", 1 ),
    28: ( "curse_of_vanishing", "Curse of Vanishing", 1 ),
    29: ( "impaling", "Impaling", 5 ),
    30: ( "riptide", "Riptide", 3 ),
    31: ( "loyalty", "Loyalty", 3 ),
    32: ( "channeling", "Channeling", 1 ),
    33: ( "multishot", "Multishot", 1 ),
    34: ( "piercing", "Piercing", 4 ),
    35: ( "quick_charge", "Quick Charge", 3 ),
    36: ( "soul_speed", "Soul Speed", 3 ),
    37: ( "swift_sneak", "Swift Sneak", 3 ),
    38: ( "wind_burst", "Wind Burst", 3 ),
    39: ( "density", "Density", 5 ),
    40: ( "breach", "Breach", 4 ),
}


def fetchPage( url:Str ) -> Str:
    response = curlRequests.get( url, impersonate="chrome" )
    response.raise_for_status()
    return response.text


def fetchWikitext( page:Str ) -> Str:
    url = f"{WikiApiUrl}?action=parse&page={page}&prop=wikitext&format=json"
    response = curlRequests.get( url, impersonate="chrome" )
    response.raise_for_status()
    data = json.loads( response.text )
    return data["parse"]["wikitext"]["*"]


SkippedTableHeaders = frozenset( {
    "biome", "entity", "effect", "enchantment",
    "state value", "alias id",
} )


def _extractTableRows(
    table:Tag,
    resourceIndex:Int,
    nameIndex:Int
) -> MutableSequence[ItemRecord]:
    records:MutableSequence[ItemRecord] = []
    rows = table.find_all( "tr" )
    for row in rows[1:]:
        if not isinstance( row, Tag ):
            continue
        cells = row.find_all( ["td", "th"] )
        if len( cells ) <= max( resourceIndex, nameIndex ):
            continue
        resourceCell = cells[resourceIndex] if resourceIndex < len( cells ) else None
        nameCell = cells[nameIndex] if nameIndex < len( cells ) else None
        if not resourceCell or not nameCell:
            continue
        resourceText = resourceCell.get_text( strip=True )
        nameText = nameCell.get_text( strip=True )
        if not resourceText or not nameText:
            continue
        resourceText = re.sub( r"^minecraft:", "", resourceText )
        resourceText = resourceText.strip( "`" ).strip()
        if not resourceText or resourceText == "—":
            continue
        record = ItemRecord()
        record.idName = resourceText
        record.fullName = nameText
        record.namespace = "minecraft"
        record.maxStackSize = 64
        record.category = ""
        records.append( record )
    return records


def parseItemsFromWiki( html:Str ) -> MutableSequence[ItemRecord]:
    soup = BeautifulSoup( html, "lxml" )
    records:MutableSequence[ItemRecord] = []
    tables = soup.find_all( "table", class_="wikitable" )
    for table in tables:
        if not isinstance( table, Tag ):
            continue
        headerRow = table.find( "tr" )
        if not headerRow or not isinstance( headerRow, Tag ):
            continue
        headers = [th.get_text( strip=True ).lower() for th in headerRow.find_all( "th" )]
        if any( h in SkippedTableHeaders for h in headers ):
            continue
        hasResource = any( h in headers for h in ( "resource location", "identifier", "string id" ) )
        hasName = any( h in headers for h in ( "block", "item", "in-game name" ) )
        if not hasResource or not hasName:
            continue
        resourceIndex = next(
            ( i for i, h in enumerate( headers )
              if h in ( "resource location", "identifier", "string id" ) ),
            -1
        )
        nameIndex = next(
            ( i for i, h in enumerate( headers )
              if h in ( "block", "item", "in-game name" ) ),
            -1
        )
        records.extend( _extractTableRows( table, resourceIndex, nameIndex ) )
    return records


def parseItemsFromSubPage( html:Str ) -> MutableSequence[ItemRecord]:
    soup = BeautifulSoup( html, "lxml" )
    records:MutableSequence[ItemRecord] = []
    tables = soup.find_all( "table" )
    for table in tables:
        if not isinstance( table, Tag ):
            continue
        headerRow = table.find( "tr" )
        if not headerRow or not isinstance( headerRow, Tag ):
            continue
        headers = [th.get_text( strip=True ).lower() for th in headerRow.find_all( "th" )]
        if "identifier" not in headers or "item" not in headers:
            continue
        resourceIndex = headers.index( "identifier" )
        nameIndex = headers.index( "item" )
        records.extend( _extractTableRows( table, resourceIndex, nameIndex ) )
    return records


def parseEffectsFromWiki( html:Str ) -> MutableSequence[EffectRecord]:
    soup = BeautifulSoup( html, "lxml" )
    records:MutableSequence[EffectRecord] = []
    tables = soup.find_all( "table", class_="wikitable" )
    for table in tables:
        if not isinstance( table, Tag ):
            continue
        headerRow = table.find( "tr" )
        if not headerRow or not isinstance( headerRow, Tag ):
            continue
        headers = [th.get_text( strip=True ).lower() for th in headerRow.find_all( "th" )]
        hasName = any( "name" in h or "effect" in h or "display" in h for h in headers )
        hasId = any( "id" in h or "be" in h for h in headers )
        if not hasName or not hasId:
            continue
        nameIndex = next(
            ( i for i, h in enumerate( headers )
              if "name" in h or "display" in h or "effect" in h ),
            -1
        )
        idIndex = next(
            ( i for i, h in enumerate( headers )
              if h in ( "be num. id", "numeric id", "be id", "id" ) or "be" in h ),
            -1
        )
        identifierIndex = next(
            ( i for i, h in enumerate( headers )
              if "identifier" in h or "resource" in h or "string" in h ),
            -1
        )
        rows = table.find_all( "tr" )
        for row in rows[1:]:
            if not isinstance( row, Tag ):
                continue
            cells = row.find_all( ["td", "th"] )
            if len( cells ) <= max( nameIndex, idIndex ):
                continue
            nameText = cells[nameIndex].get_text( strip=True ) if nameIndex < len( cells ) else ""
            idText = cells[idIndex].get_text( strip=True ) if idIndex < len( cells ) else ""
            identifierText = ""
            if identifierIndex >= 0 and identifierIndex < len( cells ):
                identifierText = cells[identifierIndex].get_text( strip=True )
            if not nameText or not idText:
                continue
            try:
                numericId = int( re.sub( r"[^\d-]", "", idText ) )
            except ( ValueError, IndexError ):
                continue
            if not identifierText:
                identifierText = re.sub( r"\s+", "_", nameText.lower() )
            identifierText = identifierText.strip( "`" ).strip()
            identifierText = re.sub( r"^minecraft:", "", identifierText )
            record = EffectRecord()
            record.numericId = numericId
            record.idName = identifierText
            record.fullName = nameText
            records.append( record )
    return records


TrimMaterialNameMap:MutableMapping[Str, Str] = {
    "amethyst shard": "amethyst",
    "copper ingot": "copper",
    "diamond": "diamond",
    "emerald": "emerald",
    "gold ingot": "gold",
    "iron ingot": "iron",
    "lapis lazuli": "lapis",
    "nether quartz": "quartz",
    "netherite ingot": "netherite",
    "redstone dust": "redstone",
    "resin brick": "resin",
}


def parseTrimPatternsFromWikitext( wikitext:Str ) -> MutableSequence[TrimPatternRecord]:
    records:MutableSequence[TrimPatternRecord] = []
    seen:set = set()
    for match in re.finditer( r"Armor Trim (\w+) \(sample model\)", wikitext ):
        patternName = match.group( 1 )
        idName = patternName.lower()
        if idName in seen:
            continue
        seen.add( idName )
        record = TrimPatternRecord()
        record.idName = idName
        record.fullName = patternName
        records.append( record )
    return records


def parseTrimMaterialsFromWikitext( wikitext:Str ) -> MutableSequence[TrimMaterialRecord]:
    records:MutableSequence[TrimMaterialRecord] = []
    seen:set = set()
    for match in re.finditer( r"\{\{TrimPalette\|([^}|]+)", wikitext ):
        itemName = match.group( 1 ).strip().lower()
        if itemName in seen:
            continue
        seen.add( itemName )
        idName = TrimMaterialNameMap.get( itemName, "" )
        if not idName:
            idName = itemName.split()[0]
        fullName = idName.title()
        record = TrimMaterialRecord()
        record.idName = idName
        record.fullName = fullName
        record.itemName = itemName.replace( " ", "_" )
        records.append( record )
    return records


class WikiScraper:

    def __init__(
        self,
        itemRepository:ItemRepository,
        enchantmentRepository:EnchantmentRepository,
        effectRepository:EffectRepository,
        updateMetaRepository:UpdateMetaRepository,
        trimMaterialRepository:Optional[TrimMaterialRepository] = None,
        trimPatternRepository:Optional[TrimPatternRepository] = None
    ) -> None:
        self.itemRepository = itemRepository
        self.enchantmentRepository = enchantmentRepository
        self.effectRepository = effectRepository
        self.updateMetaRepository = updateMetaRepository
        self.trimMaterialRepository = trimMaterialRepository
        self.trimPatternRepository = trimPatternRepository

    def updateItems( self ) -> Int:
        print( "Fetching item data from Minecraft Wiki..." )
        html = fetchPage( BedrockDataValuesUrl )
        records = parseItemsFromWiki( html )
        seen = { r.idName for r in records }
        try:
            itemsHtml = fetchPage( BedrockItemsUrl )
            subRecords = parseItemsFromSubPage( itemsHtml )
            for record in subRecords:
                if record.idName not in seen:
                    records.append( record )
                    seen.add( record.idName )
        except Exception:
            print( "Warning: could not fetch items sub-page." )
        if records:
            self.itemRepository.upsertBulk( records )
            timestamp = datetime.now( timezone.utc ).isoformat()
            self.updateMetaRepository.setLastUpdated( "items", timestamp )
            print( f"Updated {len( records )} items." )
        else:
            print( "No items found on page." )
        return len( records )

    def updateEnchantments( self ) -> Int:
        print( "Loading Bedrock enchantment data..." )
        records:MutableSequence[EnchantmentRecord] = []
        for numericId, ( idName, fullName, maxLevel ) in BedrockEnchantmentIds.items():
            record = EnchantmentRecord()
            record.numericId = numericId
            record.idName = idName
            record.fullName = fullName
            record.maxLevel = maxLevel
            records.append( record )
        if records:
            self.enchantmentRepository.upsertBulk( records )
            timestamp = datetime.now( timezone.utc ).isoformat()
            self.updateMetaRepository.setLastUpdated( "enchantments", timestamp )
            print( f"Updated {len( records )} enchantments." )
        return len( records )

    def updateEffects( self ) -> Int:
        print( "Loading Bedrock effect data..." )
        records = self._loadDefaultEffects()
        if records:
            self.effectRepository.upsertBulk( records )
            timestamp = datetime.now( timezone.utc ).isoformat()
            self.updateMetaRepository.setLastUpdated( "effects", timestamp )
            print( f"Updated {len( records )} effects." )
        return len( records )

    def updateTrims( self ) -> Int:
        if not self.trimMaterialRepository or not self.trimPatternRepository:
            print( "Trim repositories not configured." )
            return 0
        print( "Fetching trim data from Minecraft Wiki..." )
        patternWikitext = fetchWikitext( "Smithing_Template" )
        patterns = parseTrimPatternsFromWikitext( patternWikitext )
        materialWikitext = fetchWikitext( "Smithing" )
        materials = parseTrimMaterialsFromWikitext( materialWikitext )
        total = 0
        if patterns:
            self.trimPatternRepository.upsertBulk( patterns )
            total += len( patterns )
            print( f"  Updated {len( patterns )} trim patterns." )
        if materials:
            self.trimMaterialRepository.upsertBulk( materials )
            total += len( materials )
            print( f"  Updated {len( materials )} trim materials." )
        if total:
            timestamp = datetime.now( timezone.utc ).isoformat()
            self.updateMetaRepository.setLastUpdated( "trims", timestamp )
        else:
            print( "  No trim data found." )
        return total

    def updateAll( self ) -> None:
        self.updateItems()
        self.updateEnchantments()
        self.updateEffects()
        self.updateTrims()

    def needsUpdate( self, key:Str ) -> Bool:
        meta = self.updateMetaRepository.getLastUpdated( key )
        return meta is None

    def _loadDefaultEffects( self ) -> MutableSequence[EffectRecord]:
        defaults:MutableMapping[Int, Tuple[Str, Str]] = {
            1: ( "speed", "Speed" ),
            2: ( "slowness", "Slowness" ),
            3: ( "haste", "Haste" ),
            4: ( "mining_fatigue", "Mining Fatigue" ),
            5: ( "strength", "Strength" ),
            6: ( "instant_health", "Instant Health" ),
            7: ( "instant_damage", "Instant Damage" ),
            8: ( "jump_boost", "Jump Boost" ),
            9: ( "nausea", "Nausea" ),
            10: ( "regeneration", "Regeneration" ),
            11: ( "resistance", "Resistance" ),
            12: ( "fire_resistance", "Fire Resistance" ),
            13: ( "water_breathing", "Water Breathing" ),
            14: ( "invisibility", "Invisibility" ),
            15: ( "blindness", "Blindness" ),
            16: ( "night_vision", "Night Vision" ),
            17: ( "hunger", "Hunger" ),
            18: ( "weakness", "Weakness" ),
            19: ( "poison", "Poison" ),
            20: ( "wither", "Wither" ),
            21: ( "health_boost", "Health Boost" ),
            22: ( "absorption", "Absorption" ),
            23: ( "saturation", "Saturation" ),
            24: ( "levitation", "Levitation" ),
            25: ( "fatal_poison", "Fatal Poison" ),
            26: ( "slow_falling", "Slow Falling" ),
            27: ( "conduit_power", "Conduit Power" ),
            28: ( "bad_omen", "Bad Omen" ),
            29: ( "village_hero", "Hero of the Village" ),
            30: ( "darkness", "Darkness" ),
            31: ( "trial_omen", "Trial Omen" ),
            32: ( "raid_omen", "Raid Omen" ),
            33: ( "wind_charged", "Wind Charged" ),
            34: ( "weaving", "Weaving" ),
            35: ( "oozing", "Oozing" ),
            36: ( "infested", "Infested" ),
        }
        records:MutableSequence[EffectRecord] = []
        for numericId, ( idName, fullName ) in defaults.items():
            record = EffectRecord()
            record.numericId = numericId
            record.idName = idName
            record.fullName = fullName
            records.append( record )
        return records
