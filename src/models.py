from datetime import date
from sqlalchemy import Integer, String, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Phone(Base):
    __tablename__ = 'phones'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[str] = mapped_column(String(50), nullable=False)
    contact_id: Mapped[int] = mapped_column(Integer, ForeignKey('contacts.id', ondelete='CASCADE'))
    contact = relationship("Contact", back_populates="phones")

    def __repr__(self):
        return self.number


class Email(Base):
    __tablename__ = 'emails'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    address: Mapped[str] = mapped_column(String(50), nullable=False)
    contact_id: Mapped[int] = mapped_column(Integer, ForeignKey('contacts.id', ondelete='CASCADE'))
    contact = relationship("Contact", back_populates="emails")

    def __repr__(self):
        return self.address


class Contact(Base):
    __tablename__ = 'contacts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True, index=True)
    emails: Mapped[Email] = relationship("Email", back_populates="contact", lazy='joined', cascade="all, delete")
    phones: Mapped[Phone] = relationship("Phone", back_populates="contact", lazy='joined', cascade="all, delete")
    birthday: Mapped[date] = mapped_column(Date, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)


if __name__ == "__main__":
    pass


