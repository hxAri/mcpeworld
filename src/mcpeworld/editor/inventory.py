from typing import MutableSequence, Optional

import amulet_nbt

from mcpeworld import Int, Str
from mcpeworld.constant import (
    ArmorKey,
    NbtKeyEnderChest,
    NbtKeyInventory,
    OffHandKey,
)
from mcpeworld.model.item import BEGameItem
from mcpeworld.model.slot import InventoryType, SlotType
from mcpeworld.nbt.converter import gameItemToNbt, nbtToGameItem
from mcpeworld.nbt.leveldb import BedrockLevelDb


def loadInventory( playerTag:amulet_nbt.CompoundTag, inventoryType:InventoryType ) -> MutableSequence[BEGameItem]:
    key = inventoryType.value
    if not key or key not in playerTag:
        return []
    inventoryList = playerTag[key]
    if not isinstance( inventoryList, amulet_nbt.ListTag ):
        return []
    items:MutableSequence[BEGameItem] = []
    for compound in inventoryList:
        if isinstance( compound, amulet_nbt.CompoundTag ):
            item = nbtToGameItem( compound )
            items.append( item )
    return items


def loadArmorSlots( playerTag:amulet_nbt.CompoundTag ) -> MutableSequence[BEGameItem]:
    armorItems:MutableSequence[BEGameItem] = []
    if ArmorKey in playerTag:
        armorList = playerTag[ArmorKey]
        if isinstance( armorList, amulet_nbt.ListTag ):
            for i, compound in enumerate( armorList ):
                if i >= 4:
                    break
                if isinstance( compound, amulet_nbt.CompoundTag ):
                    armorItems.append( nbtToGameItem( compound ) )
    while len( armorItems ) < 4:
        armorItems.append( BEGameItem() )
    if OffHandKey in playerTag:
        offHandList = playerTag[OffHandKey]
        if isinstance( offHandList, amulet_nbt.ListTag ) and len( offHandList ) > 0:
            compound = offHandList[0]
            if isinstance( compound, amulet_nbt.CompoundTag ):
                armorItems.append( nbtToGameItem( compound ) )
        else:
            armorItems.append( BEGameItem() )
    else:
        armorItems.append( BEGameItem() )
    return armorItems


def saveInventorySlot(
    playerTag:amulet_nbt.CompoundTag,
    inventoryType:InventoryType,
    slotIndex:Int,
    item:BEGameItem
) -> None:
    key = inventoryType.value
    if not key:
        return
    if key not in playerTag:
        playerTag[key] = amulet_nbt.ListTag()
    inventoryList = playerTag[key]
    if not isinstance( inventoryList, amulet_nbt.ListTag ):
        return
    item.slot = slotIndex
    newCompound = gameItemToNbt( item )
    replaced = False
    for i in range( len( inventoryList ) ):
        existing = inventoryList[i]
        if isinstance( existing, amulet_nbt.CompoundTag ):
            if "Slot" in existing and int( existing["Slot"] ) == slotIndex:
                inventoryList[i] = newCompound
                replaced = True
                break
    if not replaced:
        inventoryList.append( newCompound )


def saveArmorSlot(
    playerTag:amulet_nbt.CompoundTag,
    slotType:SlotType,
    item:BEGameItem
) -> None:
    if slotType == SlotType.OffHand:
        if OffHandKey not in playerTag:
            playerTag[OffHandKey] = amulet_nbt.ListTag()
        offHandList = playerTag[OffHandKey]
        if isinstance( offHandList, amulet_nbt.ListTag ):
            newCompound = gameItemToNbt( item )
            if len( offHandList ) > 0:
                offHandList[0] = newCompound
            else:
                offHandList.append( newCompound )
        return
    if ArmorKey not in playerTag:
        playerTag[ArmorKey] = amulet_nbt.ListTag()
    armorList = playerTag[ArmorKey]
    if not isinstance( armorList, amulet_nbt.ListTag ):
        return
    while len( armorList ) <= slotType.value:
        armorList.append( amulet_nbt.CompoundTag() )
    armorList[slotType.value] = gameItemToNbt( item )


def clearSlot(
    playerTag:amulet_nbt.CompoundTag,
    inventoryType:InventoryType,
    slotIndex:Int
) -> None:
    key = inventoryType.value
    if not key or key not in playerTag:
        return
    inventoryList = playerTag[key]
    if not isinstance( inventoryList, amulet_nbt.ListTag ):
        return
    for i in range( len( inventoryList ) - 1, -1, -1 ):
        existing = inventoryList[i]
        if isinstance( existing, amulet_nbt.CompoundTag ):
            if "Slot" in existing and int( existing["Slot"] ) == slotIndex:
                del inventoryList[i]
                break
