from typing import List

import uvicorn
import os
from fastapi import FastAPI, status, HTTPException
from fastapi_sqlalchemy import DBSessionMiddleware
from fastapi_sqlalchemy import db
from sqlalchemy import create_engine
from sqlalchemy.exc import DatabaseError

from models import User as ModelUser, Wallet as ModelWallet, Transaction as ModelTransaction
from schema import User as SchemaUser, Wallet as SchemaWallet, WalletTransactionOut
from dotenv import load_dotenv
import models


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

engine = create_engine(
    os.environ["DATABASE_URL"]
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])


@app.post("/users/",
          response_model=SchemaUser,
          status_code=status.HTTP_201_CREATED,
          description="Создание клиента")
def create_user(user: SchemaUser):
    db_user = ModelUser(
        name=user.name,
        first_name=user.first_name,
        last_name=user.last_name,
        middle_name=user.middle_name
    )
    try:
        db.session.add(db_user)
        db.session.commit()
    except DatabaseError:
        db.session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Невозможно создать клиента")
    return db_user


@app.get("/users/",
         response_model=List[SchemaUser],
         status_code=status.HTTP_200_OK,
         description="Список клиентов"
         )
def get_users():
    db_users = db.session.query(ModelUser).all()
    return db_users


@app.post("/wallets/",
          response_model=SchemaWallet,
          status_code=status.HTTP_201_CREATED,
          description="Создание кошелька клиента с суммой"
          )
def create_wallet(wallet: SchemaWallet):
    db_wallet = ModelWallet(
        user_id=wallet.user_id,
        amount=wallet.amount
    )
    try:
        db.session.add(db_wallet)
        db.session.commit()
    except DatabaseError:
        db.session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Невозможно создать кошелек")
    return db_wallet


@app.get("/wallets/",
         response_model=List[SchemaWallet],
         status_code=status.HTTP_200_OK,
         description="Список кошельков"
         )
def get_wallets():
    db_wallets = db.session.query(ModelWallet).all()
    return db_wallets


@app.get("/wallets/{wallet_id}",
         response_model=SchemaWallet,
         status_code=status.HTTP_200_OK,
         description="Кошельек"
         )
def get_wallets(wallet_id: str):
    db_wallet = db.session.query(ModelWallet).filter_by(id=wallet_id).first()
    if not db_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Кошелек не найден")
    return db_wallet


@app.put("/wallets/{wallet_id}/credit",
         response_model=SchemaWallet,
         status_code=status.HTTP_200_OK,
         description="Зачислить сумму на кошелек (из-вне)"
         )
def update_wallet_credit(wallet_id: str, amount: int):
    if amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Сумма должна быть больше нуля")
    db_wallet = db.session.query(ModelWallet).filter_by(id=wallet_id).first()
    if not db_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Кошелек не найден")
    db_wallet.amount += amount
    try:
        db_transaction = ModelTransaction(
            wallet_credit_id=db_wallet.id,
            wallet_debit_id=None,
            amount=amount
        )
        db.session.add(db_transaction)
        db.session.add(db_wallet)
        db.session.commit()
    except DatabaseError:
        db.session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Кошелек не может быть обновлен")
    return db_wallet


@app.put("/wallets/{wallet_id}/debit",
         response_model=SchemaWallet,
         status_code=status.HTTP_200_OK,
         description="Списать сумму с кошелька (вывод)"
         )
def update_wallet_debit(wallet_id: str, amount: int):
    if amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Сумма должна быть больше нуля")
    db_wallet = db.session.query(ModelWallet).filter_by(id=wallet_id).first()
    if not db_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Кошелек не найден")

    if db_wallet.amount < amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="На кошельке источника недостаточно средств")

    db_wallet.amount -= amount
    try:
        db_transaction = ModelTransaction(
            wallet_credit_id=None,
            wallet_debit_id=db_wallet.id,
            amount=amount
        )
        db.session.add(db_transaction)
        db.session.add(db_wallet)
        db.session.commit()
    except DatabaseError:
        db.session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Кошелек не может быть обновлен")
    return db_wallet


@app.put("/wallets/make-transaction",
         response_model=WalletTransactionOut,
         status_code=status.HTTP_200_OK,
         description="Перевод денежных средств"
         )
def update_wallet_transaction(wallet_id_debit: str, wallet_id_credit: str, amount: int):
    if amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Сумма должна быть больше нуля")
    db_wallet_debit = db.session.query(ModelWallet).filter_by(id=wallet_id_debit).first()
    if not db_wallet_debit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Кошелек источника не найден")
    db_wallet_credit = db.session.query(ModelWallet).filter_by(id=wallet_id_credit).first()
    if not db_wallet_debit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Кошелек назначения не найден")
    if db_wallet_debit.id == db_wallet_credit.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Пеервод на себя невозможен")
    if db_wallet_debit.amount < amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="На кошельке источника недостаточно средств")

    try:
        db_wallet_debit.amount -= amount
        db_wallet_credit.amount += amount
        wallets_out = WalletTransactionOut(
            wallet_credit=db_wallet_credit,
            wallet_debit=db_wallet_debit
        )
        db_transaction = ModelTransaction(
            wallet_credit_id=db_wallet_credit.id,
            wallet_debit_id=db_wallet_debit.id,
            amount=amount
        )

        db.session.add(db_wallet_debit)
        db.session.add(db_wallet_credit)
        db.session.add(db_transaction)
        db.session.commit()
    except DatabaseError:
        db.session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Транзакция не может быть проведена")
    return wallets_out


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
