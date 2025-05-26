import logging
from typing import Dict, Optional

import conf

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    Float,
    Numeric,
    Interval,
    DateTime,
    create_engine,
    delete,
    insert,
    update,
)
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.sql import func

logger = logging.getLogger("app")


class DatabaseManager:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.metadata = MetaData()
        self.engine = create_engine(database_url)
        self.Session = scoped_session(sessionmaker(bind=self.engine))

        self.tramites = Table("tramites", self.metadata, *self._get_tramites_columns())
        self.users = Table("users", self.metadata, *self._get_user_columns())

        self.metadata.create_all(self.engine)

    def _get_user_columns(self):
        return [
            Column("id", BigInteger, primary_key=True),
            Column("username", String(100)),
            Column("first_name", String(100), nullable=False),
            Column("last_name", String(100)),
            Column("time_zone", String(50)),
            Column("is_active", Boolean, nullable=False, default=True),
        ]

    def _get_tramites_columns(self):
        return [
            Column("id", BigInteger, primary_key=True),
            Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            Column("operation", String(15), nullable=False),
            Column("current_balance", Float, default=0.0),
            Column("money_deposited", Float),
            Column("money_extracted", Float),
            Column("previous_balance", Float),
            Column("type", String(3), nullable=False),
            Column("date", TIMESTAMP(), default=func.now()),
        ]

    def connect(self):
        self.session = self.Session()
        logger.info("Connected to database")

    def disconnect(self):
        if hasattr(self, "session"):
            self.session.close()
            logger.info("Disconnected from database")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        

    # Generic CRUD
    def create_model(self, data: Dict, table: Table, debug_info: str = None) -> int:
        if debug_info:
            logger.debug(debug_info)

        # Si es la tabla users, usa ON CONFLICT DO NOTHING
        if table.name == "users":
            query = pg_insert(table).values(data).on_conflict_do_nothing(index_elements=['id'])
        else:
            query = insert(table).values(data)

        result = self.session.execute(query)
        self.session.commit()
        # Puede que no haya insertado nada si ya existía, así que maneja ese caso:
        if result.inserted_primary_key:
            return result.inserted_primary_key[0]
        return None

    def get_model(self, id: int, table: Table, debug_info: str = None) -> Optional[Dict]:
        if debug_info:
            logger.debug(debug_info)

        query = table.select().where(table.c.id == id)
        result = self.session.execute(query)
        return result.fetchone()._asdict() if result.rowcount else None

    def update_model(
        self, id: int, data: Dict, table: Table, debug_info: str = None
    ) -> bool:
        if debug_info:
            logger.debug(debug_info)

        query = update(table).where(table.c.id == id).values(data)
        result = self.session.execute(query)
        self.session.commit()
        return result.rowcount > 0

    def delete_model(self, id: int, table: Table, debug_info: str = None) -> bool:
        if debug_info:
            logger.debug(debug_info)

        query = delete(table).where(table.c.id == id)
        result = self.session.execute(query)
        self.session.commit()
        return result.rowcount > 0


    #aditional methods
    def get_last_id(self, user_id):
        query = self.tramites.select().where(self.tramites.c.user_id == user_id).order_by(self.tramites.c.id.desc()).limit(1)
        result = self.session.execute(query).fetchone()
        return result.id if result else None

    def get_current_balance(self, last_id):
        if last_id is None:
            return 0.0
        query = self.tramites.select().where(self.tramites.c.id == last_id)
        result = self.session.execute(query).fetchone()
        return result.current_balance if result else 0.0

    def get_coin_type(self, last_id, field="type"):
        if last_id is None:
            return "CUP"
        query = self.tramites.select().where(self.tramites.c.id == last_id)
        result = self.session.execute(query).fetchone()
        return getattr(result, field) if result else "CUP"

db = DatabaseManager(conf.DATABASE_URL)
