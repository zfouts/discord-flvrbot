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
        logger.debug(f"Our db connection string is {self.db_url}")
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
        def transaction(session):
            query = session.query(User)
            if guild_id is not None:
                query = query.filter_by(guild_id=guild_id)
            if user_id is not None:
                query = query.filter_by(user_id=user_id)
            # Convert data to dictionary with user id as key
            result = {user.id: {
                "display_name": user.display_name,
                "last_seen": user.last_seen
            } for user in query.all()}
            logger.debug(f"Result: {result}")
            return result
        return self.execute_transaction(transaction)

    def add_user(self, guild_id, user_id, display_name, joined_guild):
        logger.info("Adding user to database...")
        def transaction(session):
            user = User(guild_id=guild_id, user_id=user_id, display_name=display_name, guild_joined=joined_guild)
            session.add(user)
            logger.info("User added successfully.")
        self.execute_transaction(transaction)

    def update_user(self, user_id, guild_id, display_name=None, last_seen=None):
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
                logger.info("User updated successfully.")
            else:
                logger.warning(f"User with user_id {user_id} and guild_id {guild_id} not found.")
        self.execute_transaction(transaction)

    # stats CRUD
    def update_stats(self, guild_id, user_id, module, data):
        logger.info("Updating stats.")
        def transaction(session):
            stats = session.query(Stats).filter_by(guild_id=guild_id, user_id=user_id, module=module).first()
            existing_data = json.loads(stats.data) if stats and stats.data else {}  # Load existing data as dictionary
            for key, value in data.items():
                existing_data[key] = existing_data.get(key, 0) + value
            if stats:
                stats.data = json.dumps(existing_data)  # Convert the updated data back to JSON format
            else:
                stats = Stats(guild_id=guild_id, user_id=user_id, module=module, data=json.dumps(existing_data))
                session.add(stats)
            logger.info("Stats updated successfully.")
        self.execute_transaction(transaction)

    def get_stats(self, guild_id, module=None):
        logger.info("Fetching stats...")
        def transaction(session):
            stats = session.query(Stats).filter_by(guild_id=guild_id, module=module).all()
            if stats:
                logger.info("Stats fetched successfully.")
                return {stat.user_id: json.loads(stat.data) for stat in stats}
            else:
                logger.warning(f"No stats found for guild_id {guild_id}, and module {module}.")
                return {}
        return self.execute_transaction(transaction)

    def get_valid_modules_and_sort_options(self):
        logger.info("Fetching valid modules and sort options...")
        def transaction(session):
            results = session.query(Stats.module, Stats.data).all()
            valid_modules = {}
            for module, data in results:
                data_keys = json.loads(data).keys()
                if module in valid_modules:
                    valid_modules[module].update(data_keys)
                else:
                    valid_modules[module] = set(data_keys)
            return valid_modules
        return self.execute_transaction(transaction)
    """
    # config table CRUD
    def add_config(self, guild_id, channel_id, module, data):
        logger.info("Adding config to database...")
        def transaction(session):
            config = Config(guild_id=guild_id, channel_id=channel_id, module=module, data=data)
            session.add(config)
            logger.info("Config added successfully.")
        self.execute_transaction(transaction)

    def update_config(self, guild_id, channel_id, module, data):
        logger.info("Updating config...")
        def transaction(session):
            config = session.query(Config).filter_by(guild_id=guild_id, channel_id=channel_id, module=module).first()
            if config:
                config.data = data
                logger.info("Config updated successfully.")
            else:
                logger.warning(f"Config not found for guild_id {guild_id}, channel_id {channel_id}, and module {module}.")
        self.execute_transaction(transaction)

    def get_config(self, guild_id, channel_id, module=None):
        logger.info("Fetching config...")
        def transaction(session):
            config = session.query(Config).filter_by(guild_id=guild_id, channel_id=channel_id, module=module).first()
            if config:
                logger.info("Config fetched successfully.")
                return config
            else:
                logger.warning(f"No config found for guild_id {guild_id}, channel_id {channel_id}, and module {module}.")
                return None
        return self.execute_transaction(transaction)

    def delete_config(self, guild_id, channel_id, module):
        logger.info("Deleting config...")
        def transaction(session):
            config = session.query(Config).filter_by(guild_id=guild_id, channel_id=channel_id, module=module).first()
            if config:
                session.delete(config)
                logger.info("Config deleted successfully.")
            else:
                logger.warning(f"Config not found for guild_id {guild_id}, channel_id {channel_id}, and module {module}.")
        self.execute_transaction(transaction)

    def get_all_configs(self, guild_id, module=None):
        logger.info("Fetching all configs...")
        def transaction(session):
            configs = session.query(Config).filter_by(guild_id=guild_id, module=module).all()
            if configs:
                logger.info("Configs fetched successfully.")
                return configs
            else:
                logger.warning(f"No configs found for guild_id {guild_id} and module {module}.")
                return []
        return self.execute_transaction(transaction)
    """
