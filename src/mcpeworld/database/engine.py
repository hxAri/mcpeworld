from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker

from mcpeworld import Str
from mcpeworld.constant import DatabasePath
from mcpeworld.database.model import Base


def createEngine( databaseUrl:Str = "" ) -> Engine:
    if not databaseUrl:
        DatabasePath.parent.mkdir( parents=True, exist_ok=True )
        databaseUrl = f"sqlite:///{DatabasePath}"
    engine = create_engine( databaseUrl, echo=False )
    Base.metadata.create_all( engine )
    return engine


def createSession( engine:Engine ) -> Session:
    factory = sessionmaker( bind=engine )
    return factory()
