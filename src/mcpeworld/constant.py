import os
from pathlib import Path

from mcpeworld import Bytes, Int, Str


InfiniteDuration:Int = 2147483647

MinecraftPackage:Str = "minecraft:"
MinecraftNamespace:Str = "minecraft"
MinecraftFolders:Str = "minecraftWorlds"
LevelDatFileName:Str = "level.dat"
LevelNameFileName:Str = "levelname.txt"
WorldIconFileName:Str = "world_icon.jpeg"
DbFolderName:Str = "db"
PlayerDataKey:Bytes = b"~local_player"
InventoryVersionKey:Str = "InventoryVersion"
LastEditedKey:Str = "LastEdited"

ChunkTypeEntity:int = 50
ChunkTypeEntityLegacy:int = 102
ChunkTypeTileEntity:int = 49

ProjectRoot:Path = Path( __file__ ).resolve().parent.parent.parent
ResourcesDir:Path = ProjectRoot / "resources"
WorldsDir:Path = ResourcesDir / "mcworlds"
BackupsDir:Path = WorldsDir / ".backups"
DatabasePath:Path = ResourcesDir / "mcpeworld.db"

TileEntitySign:Str = "Sign"
TileEntityHangingSign:Str = "HangingSign"
TileEntityCommandBlock:Str = "CommandBlock"
TileEntityItemFrame:Str = "ItemFrame"
TileEntityGlowItemFrame:Str = "GlowItemFrame"
TileEntityFlowerPot:Str = "FlowerPot"
TileEntityBed:Str = "Bed"
TileEntityMobSpawner:Str = "MobSpawner"
TileEntityChest:Str = "Chest"
TileEntityFurnace:Str = "Furnace"
TileEntityBarrel:Str = "Barrel"
TileEntityBrewingStand:Str = "BrewingStand"
TileEntityBlastFurnace:Str = "BlastFurnace"
TileEntitySmoker:Str = "Smoker"
TileEntityShulkerBox:Str = "ShulkerBox"
TileEntityChiseledBookshelf:Str = "ChiseledBookshelf"
TileEntityCampfire:Str = "Campfire"
TileEntityBanner:Str = "Banner"
TileEntityEnderChest:Str = "EnderChest"
TileEntityPistonArm:Str = "PistonArm"

ContainerTileEntities:tuple[Str,...] = (
    TileEntityChest,
    TileEntityFurnace,
    TileEntityBarrel,
    TileEntityBrewingStand,
    TileEntityBlastFurnace,
    TileEntitySmoker,
    TileEntityShulkerBox,
    TileEntityChiseledBookshelf,
)

NbtKeyInventory:Str = "Inventory"
NbtKeyEnderChest:Str = "EnderChestInventory"
NbtKeyCount:Str = "Count"
NbtKeyDamage:Str = "Damage"
NbtKeyId:Str = "id"
NbtKeyName:Str = "Name"
NbtKeySlot:Str = "Slot"
NbtKeyTag:Str = "tag"
NbtKeyLevelName:Str = "LevelName"
NbtKeyLastPlayed:Str = "LastPlayed"

ArmorKey:Str = "Armor"
OffHandKey:Str = "Offhand"
