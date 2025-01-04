from sqlalchemy import String, Date, Integer, ForeignKey, DateTime, func, Boolean, Column, Table, Float
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from pydantic import EmailStr
from datetime import date
from typing import Optional
from datetime import datetime


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    hash: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    role: Mapped[str] = mapped_column(String(50), default='user', nullable=False)


photo_tag_association = Table(
    "photo_tag_association",
    Base.metadata,
    Column("photo_id", Integer, ForeignKey("photo.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True),
)


class Photo(Base):
    __tablename__ = 'photo'
    id: Mapped[int] = mapped_column(primary_key=True)
    image: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(250))
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    user: Mapped["User"] = relationship("User", backref="photo", lazy="joined")
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now(), nullable=True)
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(),
                                             onupdate=func.now(), nullable=True)
    photo_tags = relationship("Tag", secondary=photo_tag_association, back_populates="photo_photos")


class Tag(Base):
    __tablename__ = 'tag'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    photo_photos = relationship("Photo", secondary=photo_tag_association, back_populates="photo_tags")


class Comment(Base):
    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(primary_key=True)  
    text: Mapped[str] = mapped_column(String(250), nullable=False)  
    photo_id: Mapped[int] = mapped_column(ForeignKey("photo.id"), nullable=False)
    photo: Mapped["Photo"] = relationship("Photo", backref="comment", lazy="joined")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship("User", backref="comment", lazy="joined")
    created_at: Mapped[date] = mapped_column(DateTime, default=func.now(), nullable=False)  
    updated_at: Mapped[date] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)  


class Like(Base):
    __tablename__ = 'like'
    id: Mapped[int] = mapped_column(primary_key=True)
    like_value: Mapped[int] = mapped_column(Integer, nullable=False)
    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey('photo.id'), nullable=False)
    photo: Mapped["Photo"] = relationship("Photo", backref="like", lazy="joined")
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)


class PhotoTransfer(Base):
    __tablename__ = 'photo_transfer'
    id: Mapped[int] = mapped_column(primary_key=True)
    image: Mapped[str] = mapped_column(String(255), nullable=False)
    link_url: Mapped[str] = mapped_column(String(255), nullable=False)
    link_qr: Mapped[str] = mapped_column(String(255), nullable=True)
    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey('photo.id'), nullable=False)
    photo: Mapped["Photo"] = relationship("Photo", backref="transfer", lazy="joined")

class Blacklist(Base):
    __tablename__ = 'blacklist'
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, token: str):
        self.token = token