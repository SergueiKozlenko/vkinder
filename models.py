from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=True)
    max_number = Column(Integer)
    sex = Column(Integer)
    sex_title = Column(String(100))
    age_from = Column(Integer)
    age_to = Column(Integer)
    city_id = Column(Integer)
    city_title = Column(String(100))
    country_id = Column(Integer)
    status_id = Column(Integer)
    status_title = Column(String(100))

    users_search = relationship("UsersSearch", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")
    black_list = relationship("BlackList", back_populates="user")


class UsersSearch(Base):
    __tablename__ = 'users_search'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

    user = relationship("User", back_populates="users_search")


class Favorite(Base):
    __tablename__ = 'favorites'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

    user = relationship("User", back_populates="favorites")


class BlackList(Base):
    __tablename__ = 'black_list'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

    user = relationship("User", back_populates="black_list")
