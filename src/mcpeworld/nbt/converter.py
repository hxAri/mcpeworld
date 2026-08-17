from typing import MutableMapping, MutableSequence, Optional

import amulet_nbt

from mcpeworld import Int, Str
from mcpeworld.constant import (
    MinecraftPackage,
    NbtKeyCount,
    NbtKeyDamage,
    NbtKeyName,
    NbtKeySlot,
    NbtKeyTag,
)
from mcpeworld.model.item import BEGameItem, Ench


def nbtToGameItem( compound:amulet_nbt.CompoundTag ) -> BEGameItem:
    item = BEGameItem()
    if NbtKeyName in compound:
        rawName = compound[NbtKeyName].py_str
        if rawName.startswith( MinecraftPackage ):
            rawName = rawName[len( MinecraftPackage ):]
        item.itemName = rawName
    if NbtKeyCount in compound:
        item.stackSize = int( compound[NbtKeyCount] )
    if NbtKeyDamage in compound:
        item.damage = int( compound[NbtKeyDamage] )
    if NbtKeySlot in compound:
        item.slot = int( compound[NbtKeySlot] )
    if "Block" in compound:
        blockTag = compound["Block"]
        if isinstance( blockTag, amulet_nbt.CompoundTag ):
            if "states" in blockTag:
                statesTag = blockTag["states"]
                if isinstance( statesTag, amulet_nbt.CompoundTag ):
                    for key in statesTag:
                        value = statesTag[key]
                        if isinstance( value, amulet_nbt.StringTag ):
                            item.states[key] = value.py_str
                        elif isinstance( value, amulet_nbt.ByteTag ):
                            item.states[key] = str( int( value ) )
                        elif isinstance( value, amulet_nbt.IntTag ):
                            item.states[key] = str( int( value ) )
                        else:
                            item.states[key] = str( value )
    if NbtKeyTag in compound:
        tagCompound = compound[NbtKeyTag]
        if isinstance( tagCompound, amulet_nbt.CompoundTag ):
            if "ench" in tagCompound:
                enchList = tagCompound["ench"]
                if isinstance( enchList, amulet_nbt.ListTag ):
                    for enchTag in enchList:
                        if isinstance( enchTag, amulet_nbt.CompoundTag ):
                            enchId = int( enchTag["id"] ) if "id" in enchTag else 0
                            enchLevel = int( enchTag["lvl"] ) if "lvl" in enchTag else 1
                            item.enchantments.append(
                                Ench( enchantId=enchId, level=enchLevel )
                            )
            if "display" in tagCompound:
                displayTag = tagCompound["display"]
                if isinstance( displayTag, amulet_nbt.CompoundTag ):
                    if NbtKeyName in displayTag:
                        item.displayName = displayTag[NbtKeyName].py_str
            if "Trim" in tagCompound:
                trimTag = tagCompound["Trim"]
                if isinstance( trimTag, amulet_nbt.CompoundTag ):
                    if "Material" in trimTag:
                        mat = trimTag["Material"].py_str
                        item.trimMaterial = mat.removeprefix( "minecraft:" )
                    if "Pattern" in trimTag:
                        pat = trimTag["Pattern"].py_str
                        item.trimPattern = pat.removeprefix( "minecraft:" )
    return item


def gameItemToNbt( item:BEGameItem ) -> amulet_nbt.CompoundTag:
    compound = amulet_nbt.CompoundTag()
    fullName = item.itemName
    if not fullName.startswith( MinecraftPackage ):
        fullName = MinecraftPackage + fullName
    compound[NbtKeyName] = amulet_nbt.StringTag( fullName )
    compound[NbtKeyCount] = amulet_nbt.ByteTag( item.stackSize )
    compound[NbtKeyDamage] = amulet_nbt.ShortTag( item.damage )
    if item.slot >= 0:
        compound[NbtKeySlot] = amulet_nbt.ByteTag( item.slot )
    if item.states:
        statesTag = amulet_nbt.CompoundTag()
        for key, value in item.states.items():
            statesTag[key] = amulet_nbt.StringTag( value )
        blockTag = amulet_nbt.CompoundTag()
        blockTag[NbtKeyName] = amulet_nbt.StringTag( fullName )
        blockTag["states"] = statesTag
        blockTag["version"] = amulet_nbt.IntTag( 17959425 )
        compound["Block"] = blockTag
    hasTags = item.enchantments or item.displayName or ( item.trimMaterial and item.trimPattern )
    if hasTags:
        tagCompound = amulet_nbt.CompoundTag()
        if item.enchantments:
            enchList = amulet_nbt.ListTag()
            for ench in item.enchantments:
                enchTag = amulet_nbt.CompoundTag()
                enchTag["id"] = amulet_nbt.ShortTag( ench.enchantId )
                enchTag["lvl"] = amulet_nbt.ShortTag( ench.level )
                enchList.append( enchTag )
            tagCompound["ench"] = enchList
        if item.displayName:
            displayTag = amulet_nbt.CompoundTag()
            displayTag[NbtKeyName] = amulet_nbt.StringTag( item.displayName )
            tagCompound["display"] = displayTag
        if item.trimMaterial and item.trimPattern:
            trimTag = amulet_nbt.CompoundTag()
            trimTag["Material"] = amulet_nbt.StringTag( f"minecraft:{item.trimMaterial}" )
            trimTag["Pattern"] = amulet_nbt.StringTag( f"minecraft:{item.trimPattern}" )
            tagCompound["Trim"] = trimTag
        compound[NbtKeyTag] = tagCompound
    return compound
