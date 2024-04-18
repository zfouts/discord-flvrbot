# flvrbot/db.py
import logging
import json
import os
from sqlalchemy import create_engine, Column, Integer, BigInteger, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from datetime import datetime

logger = logging.getLogger(__name__)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger)
    guild_joined = Column(DateTime)
    user_id = Column(BigInteger)
    display_name = Column(JSON, default=[], nullable=False)
    last_seen = Column(DateTime, default=None, nullable=True)
    last_message = Column(Text, nullable=True)


class Stats(Base):
    __tablename__ = 'stats'

    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger)
    user_id = Column(BigInteger)
    module = Column(Text)
    data = Column(JSON)

class DBManager:
    def __init__(self):
        self.db_url = os.environ.get('DB_URL','sqlite:////tmp/flvrbot.db')
        self.engine = create_engine(self.db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.create_tables()

    def create_tables(self):
        logger.info("Creating database tables if they don't exist...")
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully.")
        except OperationalError as e:
            logger.warning(f"Database tables already exist: {e}")

    def execute_transaction(self, transaction_function):
        session = self.Session()
        try:
            result = transaction_function(session)
            session.commit()
            logger.info("Transaction executed successfully.")
            return result
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error executing transaction: {e}")
            raise
        finally:
            session.close()

    # user table CRUD
    def get_users(self, guild_id=None, user_id=None):
        logger.info("Fetching users from database...")
        return self.execute_transaction(lambda session: session.query(User).filter_by(guild_id=guild_id, user_id=user_id).all())
    
    def add_user(self, guild_id, user_id, display_name, joined_guild):
        logger.info("Adding user to database...")
        def transaction(session):
            user = User(guild_id=guild_id, user_id=user_id, display_name=display_name, guild_joined=joined_guild)
            session.add(user)
            logger.info("User added successfully.")
        self.execute_transaction(transaction)

    def update_user(self, user_id, guild_id, display_name=None, last_seen=None, last_message=None):
        logger.info("Updating user...")
        def transaction(session):
            user = session.query(User).filter_by(user_id=user_id, guild_id=guild_id).first()
            if user:
                if display_name is not None:
                    display_names = user.display_name or []
                    display_names.append(display_name)
                    user.display_name = json.dumps(display_names)
                if last_seen is not None:
                    user.last_seen = last_seen
                if last_message is not None:
                    user.last_message = last_message
                logger.info("User updated successfully.")
            else:
                logger.warning(f"User with user_id {user_id} and guild_id {guild_id} not found.")
        self.execute_transaction(transaction)

    def update_stats(self, guild_id, user_id, module, data):
        logger.info("Updating stats.")
        def transaction(session):
            stats = session.query(Stats).filter_by(guild_id=guild_id, user_id=user_id, module=module).first()
            existing_data = json.loads(stats.data) if stats and stats.data else {}
            for key, value in data.items():
                existing_data[key] = existing_data.get(key, 0) + value
            if stats:
                stats.data = json.dumps(existing_data)
            else:
                stats = Stats(guild_id=guild_id, user_id=user_id, module=module, data=json.dumps(existing_data))
                session.add(stats)
            logger.info("Stats updated successfully.")
        self.execute_transaction(transaction)

    def get_stats(self, guild_id, module=None):
        logger.info("Fetching stats...")
        def transaction(session):
            stats = session.query(Stats).filter_by(guild_id=guild_id, module=module).first()
            if stats:
                logger.info("Stats fetched successfully.")
                return json.loads(stats.data) if stats.data else {}
            else:
                logger.warning(f"No stats found for guild_id {guild_id}, and module {module}.")
                return {}
        return self.execute_transaction(transaction)
