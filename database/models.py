from sqlalchemy import func, DateTime, String, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship


class Base(DeclarativeBase):
    created = mapped_column(DateTime, default=func.now())


class User(Base):
    """Таблица пользователя."""

    __tablename__ = 'user'

    # id = mapped_column(Integer, primary_key=True, autoincrement=True)
    id = mapped_column(Integer, primary_key=True)
    first_name = mapped_column(String(50))
    last_name = mapped_column(String(50))
    points = relationship('Point', back_populates='users')


class Point(Base):
    """Таблица баллов ЕГЭ."""

    __tablename__ = 'point'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject = mapped_column(String)
    point = mapped_column(Integer)
    user_id = mapped_column(Integer, ForeignKey('user.id'))
    users = relationship("User", back_populates="points")
