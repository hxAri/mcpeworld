from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase

from mcpeworld import Int, Str


class Base( DeclarativeBase ):
    pass


class ItemRecord( Base ):

    __tablename__ = "items"

    id:Int = Column( Integer, primary_key=True, autoincrement=True )
    idName:Str = Column( String( 255 ), nullable=False, unique=True, index=True )
    fullName:Str = Column( String( 255 ), nullable=False, default="" )
    category:Str = Column( String( 128 ), nullable=False, default="" )
    maxStackSize:Int = Column( Integer, nullable=False, default=64 )
    namespace:Str = Column( String( 128 ), nullable=False, default="minecraft" )

    def __repr__( self ) -> Str:
        return f"ItemRecord({self.fullName} ({self.idName}))"


class EnchantmentRecord( Base ):

    __tablename__ = "enchantments"

    id:Int = Column( Integer, primary_key=True, autoincrement=True )
    numericId:Int = Column( Integer, nullable=False, unique=True, index=True )
    idName:Str = Column( String( 255 ), nullable=False, unique=True, index=True )
    fullName:Str = Column( String( 255 ), nullable=False, default="" )
    maxLevel:Int = Column( Integer, nullable=False, default=1 )

    def __repr__( self ) -> Str:
        return f"EnchantmentRecord({self.fullName} ({self.idName}))"


class EffectRecord( Base ):

    __tablename__ = "effects"

    id:Int = Column( Integer, primary_key=True, autoincrement=True )
    numericId:Int = Column( Integer, nullable=False, unique=True, index=True )
    idName:Str = Column( String( 255 ), nullable=False, unique=True, index=True )
    fullName:Str = Column( String( 255 ), nullable=False, default="" )

    def __repr__( self ) -> Str:
        return f"EffectRecord({self.fullName} ({self.idName}))"


class TrimMaterialRecord( Base ):

    __tablename__ = "trim_materials"

    id:Int = Column( Integer, primary_key=True, autoincrement=True )
    idName:Str = Column( String( 255 ), nullable=False, unique=True, index=True )
    fullName:Str = Column( String( 255 ), nullable=False, default="" )
    itemName:Str = Column( String( 255 ), nullable=False, default="" )

    def __repr__( self ) -> Str:
        return f"TrimMaterialRecord({self.fullName} ({self.idName}))"


class TrimPatternRecord( Base ):

    __tablename__ = "trim_patterns"

    id:Int = Column( Integer, primary_key=True, autoincrement=True )
    idName:Str = Column( String( 255 ), nullable=False, unique=True, index=True )
    fullName:Str = Column( String( 255 ), nullable=False, default="" )

    def __repr__( self ) -> Str:
        return f"TrimPatternRecord({self.fullName} ({self.idName}))"


class UpdateMetaRecord( Base ):

    __tablename__ = "update_meta"

    key:Str = Column( String( 64 ), primary_key=True )
    lastUpdated:Str = Column( String( 64 ), nullable=False, default="" )
    version:Str = Column( String( 32 ), nullable=False, default="" )

    def __repr__( self ) -> Str:
        return f"UpdateMetaRecord({self.key}, updated={self.lastUpdated})"
