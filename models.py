import uuid

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, BigInteger, ForeignKey, UniqueConstraint, CheckConstraint, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import relationship, backref

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )
    # Дата и время создания пользователя
    created_on = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Дата и время создания пользователя"
    )
    name = Column(
        String(128),
        doc="Имя пользователя клиента",
        unique=True
    )
    first_name = Column(
        String(128),
        doc="Имя клиента",
        unique=False
    )
    last_name = Column(
        String(128),
        doc="Фамилия клиента",
        unique=False
    )
    middle_name = Column(
        String(128),
        doc="Фамилия клиента",
        unique=False
    )


class Wallet(Base):
    __tablename__ = "wallets"
    __table_args__ = (
        UniqueConstraint('user_id'),
        CheckConstraint('amount >= 0')
    )
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )
    # Дата и время создания кошелька
    created_on = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Дата и время создания кошелька"
    )
    # Клиент
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        doc="Идентификатор клиента, которому принадлежит кошелек"
    )
    user = relationship(
        'User',
        backref=backref("users", lazy='dynamic'),
        doc="Идентификатор клиента, которому принадлежит кошелек"
    )
    amount = Column(
        BigInteger,
        nullable=False,
        doc="Остаток средств в кошельке, миноры"
    )


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        doc="Идентификатор транзакции"
    )
    # Дата и время создания транзакции
    created_on = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Дата и время создания записи"
    )
    wallet_credit_id = Column(
        UUID(as_uuid=True),
        ForeignKey('wallets.id'),
        doc="Кошелек, на который идет зачисление"
    )
    wallet_debit_id = Column(
        UUID(as_uuid=True),
        ForeignKey('wallets.id'),
        doc="Кошелек, с котрого идет списание"
    )
    amount = Column(
        BigInteger,
        nullable=False,
        doc="Сумма транзакции, миноры"
    )
