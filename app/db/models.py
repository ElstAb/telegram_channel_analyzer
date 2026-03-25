from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    telegram_id = Column(Integer, unique=True)

    username = Column(String, unique=True)


class Channel(Base):

    __tablename__ = "channels"

    id = Column(Integer, primary_key=True)

    channel_name = Column(String, unique=True)


class UserChannel(Base):

    __tablename__ = "user_channels"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    channel_id = Column(Integer, ForeignKey("channels.id"))