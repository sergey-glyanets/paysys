from uuid import UUID

from pydantic import BaseModel
from pydantic.class_validators import Optional


class User(BaseModel):
    id: Optional[UUID] = None
    name: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None

    class Config:
        orm_mode = True


class Wallet(BaseModel):
    id: Optional[UUID] = None
    user_id: UUID
    amount: int = 0

    class Config:
        orm_mode = True


class WalletTransactionOut(BaseModel):
    wallet_credit: Wallet
    wallet_debit: Wallet
