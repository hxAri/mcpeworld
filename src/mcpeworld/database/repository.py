from typing import MutableSequence, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from mcpeworld import Int, Str
from mcpeworld.database.model import (
    EffectRecord,
    EnchantmentRecord,
    ItemRecord,
    TrimMaterialRecord,
    TrimPatternRecord,
    UpdateMetaRecord,
)


class ItemRepository:

    def __init__( self, session:Session ) -> None:
        self.session = session

    def findAll( self ) -> MutableSequence[ItemRecord]:
        statement = select( ItemRecord ).order_by( ItemRecord.fullName )
        return list( self.session.scalars( statement ).all() )

    def findByIdName( self, idName:Str ) -> Optional[ItemRecord]:
        statement = select( ItemRecord ).where( ItemRecord.idName == idName )
        return self.session.scalars( statement ).first()

    def search( self, query:Str ) -> MutableSequence[ItemRecord]:
        pattern = f"%{query}%"
        statement = select( ItemRecord ).where(
            ItemRecord.fullName.ilike( pattern ) | ItemRecord.idName.ilike( pattern )
        ).order_by( ItemRecord.fullName )
        return list( self.session.scalars( statement ).all() )

    def findByCategory( self, category:Str ) -> MutableSequence[ItemRecord]:
        statement = select( ItemRecord ).where(
            ItemRecord.category == category
        ).order_by( ItemRecord.fullName )
        return list( self.session.scalars( statement ).all() )

    def upsert( self, record:ItemRecord ) -> None:
        existing = self.findByIdName( record.idName )
        if existing:
            existing.fullName = record.fullName
            existing.category = record.category
            existing.maxStackSize = record.maxStackSize
            existing.namespace = record.namespace
        else:
            self.session.add( record )

    def upsertBulk( self, records:MutableSequence[ItemRecord] ) -> None:
        for record in records:
            self.upsert( record )
        self.session.commit()

    def count( self ) -> Int:
        statement = select( ItemRecord )
        return len( list( self.session.scalars( statement ).all() ) )


class EnchantmentRepository:

    def __init__( self, session:Session ) -> None:
        self.session = session

    def findAll( self ) -> MutableSequence[EnchantmentRecord]:
        statement = select( EnchantmentRecord ).order_by( EnchantmentRecord.fullName )
        return list( self.session.scalars( statement ).all() )

    def findByNumericId( self, numericId:Int ) -> Optional[EnchantmentRecord]:
        statement = select( EnchantmentRecord ).where(
            EnchantmentRecord.numericId == numericId
        )
        return self.session.scalars( statement ).first()

    def findByIdName( self, idName:Str ) -> Optional[EnchantmentRecord]:
        statement = select( EnchantmentRecord ).where(
            EnchantmentRecord.idName == idName
        )
        return self.session.scalars( statement ).first()

    def search( self, query:Str ) -> MutableSequence[EnchantmentRecord]:
        pattern = f"%{query}%"
        statement = select( EnchantmentRecord ).where(
            EnchantmentRecord.fullName.ilike( pattern ) | EnchantmentRecord.idName.ilike( pattern )
        ).order_by( EnchantmentRecord.fullName )
        return list( self.session.scalars( statement ).all() )

    def upsert( self, record:EnchantmentRecord ) -> None:
        existing = self.findByNumericId( record.numericId )
        if existing:
            existing.idName = record.idName
            existing.fullName = record.fullName
            existing.maxLevel = record.maxLevel
        else:
            self.session.add( record )

    def upsertBulk( self, records:MutableSequence[EnchantmentRecord] ) -> None:
        for record in records:
            self.upsert( record )
        self.session.commit()

    def count( self ) -> Int:
        statement = select( EnchantmentRecord )
        return len( list( self.session.scalars( statement ).all() ) )


class EffectRepository:

    def __init__( self, session:Session ) -> None:
        self.session = session

    def findAll( self ) -> MutableSequence[EffectRecord]:
        statement = select( EffectRecord ).order_by( EffectRecord.fullName )
        return list( self.session.scalars( statement ).all() )

    def findByNumericId( self, numericId:Int ) -> Optional[EffectRecord]:
        statement = select( EffectRecord ).where(
            EffectRecord.numericId == numericId
        )
        return self.session.scalars( statement ).first()

    def findByIdName( self, idName:Str ) -> Optional[EffectRecord]:
        statement = select( EffectRecord ).where(
            EffectRecord.idName == idName
        )
        return self.session.scalars( statement ).first()

    def search( self, query:Str ) -> MutableSequence[EffectRecord]:
        pattern = f"%{query}%"
        statement = select( EffectRecord ).where(
            EffectRecord.fullName.ilike( pattern ) | EffectRecord.idName.ilike( pattern )
        ).order_by( EffectRecord.fullName )
        return list( self.session.scalars( statement ).all() )

    def upsert( self, record:EffectRecord ) -> None:
        existing = self.findByNumericId( record.numericId )
        if existing:
            existing.idName = record.idName
            existing.fullName = record.fullName
        else:
            self.session.add( record )

    def upsertBulk( self, records:MutableSequence[EffectRecord] ) -> None:
        for record in records:
            self.upsert( record )
        self.session.commit()

    def count( self ) -> Int:
        statement = select( EffectRecord )
        return len( list( self.session.scalars( statement ).all() ) )


class TrimMaterialRepository:

    def __init__( self, session:Session ) -> None:
        self.session = session

    def findAll( self ) -> MutableSequence[TrimMaterialRecord]:
        statement = select( TrimMaterialRecord ).order_by( TrimMaterialRecord.fullName )
        return list( self.session.scalars( statement ).all() )

    def findByIdName( self, idName:Str ) -> Optional[TrimMaterialRecord]:
        statement = select( TrimMaterialRecord ).where(
            TrimMaterialRecord.idName == idName
        )
        return self.session.scalars( statement ).first()

    def search( self, query:Str ) -> MutableSequence[TrimMaterialRecord]:
        pattern = f"%{query}%"
        statement = select( TrimMaterialRecord ).where(
            TrimMaterialRecord.fullName.ilike( pattern ) | TrimMaterialRecord.idName.ilike( pattern )
        ).order_by( TrimMaterialRecord.fullName )
        return list( self.session.scalars( statement ).all() )

    def upsert( self, record:TrimMaterialRecord ) -> None:
        existing = self.findByIdName( record.idName )
        if existing:
            existing.fullName = record.fullName
            existing.itemName = record.itemName
        else:
            self.session.add( record )

    def upsertBulk( self, records:MutableSequence[TrimMaterialRecord] ) -> None:
        for record in records:
            self.upsert( record )
        self.session.commit()

    def count( self ) -> Int:
        statement = select( TrimMaterialRecord )
        return len( list( self.session.scalars( statement ).all() ) )


class TrimPatternRepository:

    def __init__( self, session:Session ) -> None:
        self.session = session

    def findAll( self ) -> MutableSequence[TrimPatternRecord]:
        statement = select( TrimPatternRecord ).order_by( TrimPatternRecord.fullName )
        return list( self.session.scalars( statement ).all() )

    def findByIdName( self, idName:Str ) -> Optional[TrimPatternRecord]:
        statement = select( TrimPatternRecord ).where(
            TrimPatternRecord.idName == idName
        )
        return self.session.scalars( statement ).first()

    def search( self, query:Str ) -> MutableSequence[TrimPatternRecord]:
        pattern = f"%{query}%"
        statement = select( TrimPatternRecord ).where(
            TrimPatternRecord.fullName.ilike( pattern ) | TrimPatternRecord.idName.ilike( pattern )
        ).order_by( TrimPatternRecord.fullName )
        return list( self.session.scalars( statement ).all() )

    def upsert( self, record:TrimPatternRecord ) -> None:
        existing = self.findByIdName( record.idName )
        if existing:
            existing.fullName = record.fullName
        else:
            self.session.add( record )

    def upsertBulk( self, records:MutableSequence[TrimPatternRecord] ) -> None:
        for record in records:
            self.upsert( record )
        self.session.commit()

    def count( self ) -> Int:
        statement = select( TrimPatternRecord )
        return len( list( self.session.scalars( statement ).all() ) )


class UpdateMetaRepository:

    def __init__( self, session:Session ) -> None:
        self.session = session

    def getLastUpdated( self, key:Str ) -> Optional[UpdateMetaRecord]:
        statement = select( UpdateMetaRecord ).where(
            UpdateMetaRecord.key == key
        )
        return self.session.scalars( statement ).first()

    def setLastUpdated( self, key:Str, lastUpdated:Str, version:Str = "" ) -> None:
        existing = self.getLastUpdated( key )
        if existing:
            existing.lastUpdated = lastUpdated
            existing.version = version
        else:
            record = UpdateMetaRecord( key=key, lastUpdated=lastUpdated, version=version )
            self.session.add( record )
        self.session.commit()
