import enum
from typing import Optional

from mcpeworld import Int, Str


class SlotType( enum.Enum ):

    Head = 0
    ChestPlate = 1
    Legs = 2
    Boots = 3
    OffHand = 4
    CommonSlot = -1

    @classmethod
    def byId( cls, slotId:Int ) -> "SlotType":
        for member in cls:
            if member.value == slotId:
                return member
        return cls.CommonSlot


class InventoryType( enum.Enum ):

    Non = ""
    Inventory = "Inventory"
    EnderChestInventory = "EnderChestInventory"

    @property
    def inventoryName( self ) -> Str:
        return self.value
