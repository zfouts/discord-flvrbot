# flvrbot/db.py
import logging
import json
import os
from sqlalchemy import create_engine, Column, Integer, BigInteger, DateTime, JSON, Text, and_, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from datetime import datetime

logger = logging.getLogger(__name__)

Base = declarative_base()

class Quote(Base):
    __tablename__ = 'quotes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    guild_id = Column(BigInteger, nullable=False)
    message = Column(Text, nullable=False)
    date_submitted = Column(DateTime, nullable=False, default=datetime.utcnow)
    date_last_viewed = Column(DateTime, nullable=True)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger)
    guild_joined = Column(DateTime)
    user_id = Column(BigInteger)
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
        self.db_url = os.environ.get('DB_URL', 'sqlite:////tmp/flvrbot.db')
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
                "user_id": user.user_id,
                "guild_id": user.guild_id,
                "last_seen": user.last_seen
            } for user in query.all()}
            logger.debug(f"Result: {result}")
            return result
        return self.execute_transaction(transaction)

    def add_user(self, guild_id, user_id, joined_guild):
        logger.info("Adding user to database...")
        def transaction(session):
            user = User(guild_id=guild_id, user_id=user_id, guild_joined=joined_guild)
            session.add(user)
            logger.info("User added successfully.")
        self.execute_transaction(transaction)

    def update_user(self, user_id, guild_id, last_seen=None):
        logger.info("Updating user...")
        def transaction(session):
            user = session.query(User).filter_by(user_id=user_id, guild_id=guild_id).first()
            if user:
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

    # Quote CRUD
    def add_quote(self, user_id, guild_id, message):
        logger.info("Adding new quote to the database...")
        def transaction(session):
            quote = Quote(
                user_id=user_id, 
                guild_id=guild_id, 
                message=message,
                date_submitted=datetime.utcnow()
            )
            session.add(quote)
            logger.info("Quote added successfully.")
        self.execute_transaction(transaction)

    def get_quotes(self, user_id=None, guild_id=None):
        logger.info("Fetching quotes from database...")
        def transaction(session):
            query = session.query(Quote)
            if guild_id:
                query = query.filter_by(guild_id=guild_id)
            if user_id:
                query = query.filter_by(user_id=user_id)
            result = [{
                "id": quote.id,
                "user_id": quote.user_id,
                "guild_id": quote.guild_id,
                "message": quote.message,
                "date_submitted": quote.date_submitted,
                "date_last_viewed": quote.date_last_viewed
            } for quote in query.all()]
            logger.debug(f"Quotes fetched: {result}")
            return result
        return self.execute_transaction(transaction)

    def update_quote_last_viewed(self, quote_id, last_viewed_time):
        logger.info("Updating quote's last viewed date...")
        def transaction(session):
            quote = session.query(Quote).filter_by(id=quote_id).first()
            if quote:
                quote.date_last_viewed = last_viewed_time
                logger.info("Quote last viewed date updated successfully.")
            else:
                logger.warning(f"Quote with id {quote_id} not found.")
        self.execute_transaction(transaction)

    def get_quote_by_id(self, quote_id, guild_id):
        logger.info("Fetching quote by ID...")
        def transaction(session):
            quote = session.query(Quote).filter(and_(Quote.id == quote_id, Quote.guild_id == guild_id)).first()
            if quote:
                return {
                    "id": quote.id,
                    "user_id": quote.user_id,
                    "guild_id": quote.guild_id,
                    "message": quote.message,
                    "date_submitted": quote.date_submitted,
                    "date_last_viewed": quote.date_last_viewed
                }
            else:
                return None
        return self.execute_transaction(transaction)

    def search_quotes_by_text(self, text, guild_id):
        logger.info("Searching quotes by text...")
        def transaction(session):
            pattern = f"%{text}%"
            quotes = session.query(Quote).filter(and_(Quote.message.like(pattern), Quote.guild_id == guild_id)).all()
            return [{
                "id": quote.id,
                "user_id": quote.user_id,
                "guild_id": quote.guild_id,
                "message": quote.message,
                "date_submitted": quote.date_submitted,
                "date_last_viewed": quote.date_last_viewed
            } for quote in quotes]
        return self.execute_transaction(transaction)

    def delete_quote(self, quote_id, guild_id):
        logger.info("Deleting a quote from the database...")
        def transaction(session):
            quote = session.query(Quote).filter_by(id=quote_id, guild_id=guild_id).first()
            if quote:
                session.delete(quote)
                logger.info("Quote deleted successfully.")
                return True
            else:
                logger.warning(f"Quote with ID {quote_id} in guild {guild_id} not found.")
                return False
        return self.execute_transaction(transaction)

