from fastapi.testclient import TestClient
from main import app
import random

client = TestClient(app)


def test_create_user():
    random_part = str(random.randint(1, 99999))
    user_name = "User " + random_part
    first_name = "First  " + random_part
    last_name = "Last  " + random_part
    middle_name = "Middle  " + random_part
    user_json = {"name": user_name, "first_name": first_name, "last_name": last_name, "middle_name": middle_name}
    response = client.post(
        "/users/",
        json=user_json
    )
    assert response.status_code == 201
    user_id = response.json()['id']
    print(user_id)


def test_create_user_and_wallet():
    random_part = str(random.randint(1, 99999))
    user_name = "User " + random_part
    first_name = "First  " + random_part
    last_name = "Last  " + random_part
    middle_name = "Middle  " + random_part
    user_json = {"name": user_name, "first_name": first_name, "last_name": last_name, "middle_name": middle_name}
    response = client.post(
        "/users/",
        json=user_json
    )
    assert response.status_code == 201
    user_id = response.json()['id']
    print("user_id=" + user_id)
    wallet_json = {"user_id": user_id, "amount": random.randint(100, 99999900)}
    response = client.post(
        "/wallets/",
        json=wallet_json
    )
    assert response.status_code == 201
    wallet_id = response.json()['id']
    print("wallet_id=" + wallet_id)


def test_create_user_and_wallet():
    random_part = str(random.randint(1, 99999))
    user_name = "User " + random_part
    first_name = "First  " + random_part
    last_name = "Last  " + random_part
    middle_name = "Middle  " + random_part
    user_json = {"name": user_name, "first_name": first_name, "last_name": last_name, "middle_name": middle_name}
    response = client.post(
        "/users/",
        json=user_json
    )
    assert response.status_code == 201
    user_id = response.json()['id']
    print("user_id=" + user_id)
    wallet_json = {"user_id": user_id, "amount": random.randint(100, 99999900)}
    response = client.post(
        "/wallets/",
        json=wallet_json
    )
    assert response.status_code == 201
    wallet_id = response.json()['id']
    print("wallet_id=" + wallet_id)


def test_get_wallets():
    response = client.get(
        "/wallets/"
    )
    assert response.status_code == 200
    body = response.json()
    if not isinstance(body, list):
        assert False


def test_make_random_transaction():
    random_amount = random.randint(100, 9999900)

    response = client.get(
        "/wallets/"
    )
    assert response.status_code == 200
    body = response.json()
    if not isinstance(body, list):
        assert False
    if len(body) < 2:
        # Создадим кошельки
        for x in range(3):
            test_create_user_and_wallet()
    # Запросим кошельки еще раз
    response = client.get(
        "/wallets/"
    )
    assert response.status_code == 200
    body = response.json()
    if not isinstance(body, list):
        assert False
    if len(body) < 2:
        assert False  # На этот раз ошибка

    # Берем первый кошелек и случайный
    wallet_debit = body[0]
    wallet_credit = body[random.randint(1, len(body) - 1)]
    wallets_reponse = client.put(
        "/wallets/make-transaction",
        params={'wallet_id_debit': wallet_debit['id'],
                'wallet_id_credit': wallet_credit['id'],
                'amount': random_amount
                }
    )

    if random_amount > wallet_debit['amount'] and wallets_reponse.status_code != 400:
        # Если на источнике мало средств, должна быть ошибка
        assert False


def test_make_transaction():
    # Создаем пользователя 1
    u1 = str(random.randint(1, 99999))
    response = client.post(
        "/users/",
        json={"name": "U " + u1, "first_name": "F " + u1, "last_name": "L " + u1, "middle_name": "M " + u1}
    )
    assert response.status_code == 201
    user_id_1 = response.json()['id']

    # Создаем пользователя 2
    u2 = str(random.randint(1, 99999))
    response = client.post(
        "/users/",
        json={"name": "U " + u2, "first_name": "F " + u2, "last_name": "L " + u2, "middle_name": "M " + u2}
    )
    assert response.status_code == 201
    user_id_2 = response.json()['id']

    # Создадим два кошелька
    wallet_json = {"user_id": user_id_1, "amount": 10000}
    response = client.post(
        "/wallets/",
        json=wallet_json
    )
    assert response.status_code == 201
    wallet_id_1 = response.json()['id']
    wallet_json = {"user_id": user_id_2, "amount": 20000}
    response = client.post(
        "/wallets/",
        json=wallet_json
    )
    assert response.status_code == 201
    wallet_id_2 = response.json()['id']
    # Проводим перевод
    wallets_reponse = client.put(
        "/wallets/make-transaction",
        params={'wallet_id_debit': wallet_id_1,
                'wallet_id_credit': wallet_id_2,
                'amount': 5000
                }
    )
    assert wallets_reponse.status_code == 200
    # запросим кошельки
    wallet_1_aft_resp = client.get(
        "/wallets/" + wallet_id_1
    )
    assert wallet_1_aft_resp.status_code == 200
    wallet_1_aft = wallet_1_aft_resp.json()
    wallet_2_aft_resp = client.get(
        "/wallets/" + wallet_id_2
    )
    assert wallet_2_aft_resp.status_code == 200
    wallet_2_aft = wallet_2_aft_resp.json()
    # С певого кошелька списывали. Должно быть 10000-5000
    assert wallet_1_aft['amount'] == 5000
    # На второй зачисляли
    assert wallet_2_aft['amount'] == 25000


def test_make_add_funds():
    # Создаем пользователя 1
    u1 = str(random.randint(1, 99999))
    response = client.post(
        "/users/",
        json={"name": "U " + u1, "first_name": "F " + u1, "last_name": "L " + u1, "middle_name": "M " + u1}
    )
    assert response.status_code == 201
    user_id_1 = response.json()['id']

    # Создаем кошелек
    wallet_json = {"user_id": user_id_1, "amount": 10000}
    response = client.post(
        "/wallets/",
        json=wallet_json
    )
    assert response.status_code == 201
    wallet_id_1 = response.json()['id']

    # Добавлем средства
    wallets_reponse = client.put(
        "/wallets/{}/credit".format(wallet_id_1),
        params={'amount': 5000}
    )
    assert wallets_reponse.status_code == 200
    # запросим кошелек
    wallet_1_aft_resp = client.get(
        "/wallets/" + wallet_id_1
    )
    assert wallet_1_aft_resp.status_code == 200
    wallet_1_aft = wallet_1_aft_resp.json()
    assert wallet_1_aft['amount'] == 15000


def test_make_add_funds_neg1():
    # Создаем пользователя 1
    u1 = str(random.randint(1, 99999))
    response = client.post(
        "/users/",
        json={"name": "U " + u1, "first_name": "F " + u1, "last_name": "L " + u1, "middle_name": "M " + u1}
    )
    assert response.status_code == 201
    user_id_1 = response.json()['id']

    # Создаем кошелек
    wallet_json = {"user_id": user_id_1, "amount": 10000}
    response = client.post(
        "/wallets/",
        json=wallet_json
    )
    assert response.status_code == 201
    wallet_id_1 = response.json()['id']

    # Добавлем средства
    wallets_reponse = client.put(
        "/wallets/{}/credit".format(wallet_id_1),
        params={'amount': -5000}
    )
    # Должна быть ошибка
    assert wallets_reponse.status_code == 400


def test_make_take_funds():
    # Создаем пользователя 1
    u1 = str(random.randint(1, 99999))
    response = client.post(
        "/users/",
        json={"name": "U " + u1, "first_name": "F " + u1, "last_name": "L " + u1, "middle_name": "M " + u1}
    )
    assert response.status_code == 201
    user_id_1 = response.json()['id']

    # Создаем кошелек
    wallet_json = {"user_id": user_id_1, "amount": 10000}
    response = client.post(
        "/wallets/",
        json=wallet_json
    )
    assert response.status_code == 201
    wallet_id_1 = response.json()['id']

    # Списываем средства
    wallets_reponse = client.put(
        "/wallets/{}/debit".format(wallet_id_1),
        params={'amount': 5000}
    )
    # запросим кошелек
    wallet_1_aft_resp = client.get(
        "/wallets/" + wallet_id_1
    )
    assert wallet_1_aft_resp.status_code == 200
    wallet_1_aft = wallet_1_aft_resp.json()
    assert wallet_1_aft['amount'] == 5000


def test_make_take_funds_neg1():
    # Создаем пользователя 1
    u1 = str(random.randint(1, 99999))
    response = client.post(
        "/users/",
        json={"name": "U " + u1, "first_name": "F " + u1, "last_name": "L " + u1, "middle_name": "M " + u1}
    )
    assert response.status_code == 201
    user_id_1 = response.json()['id']

    # Создаем кошелек
    wallet_json = {"user_id": user_id_1, "amount": 10000}
    response = client.post(
        "/wallets/",
        json=wallet_json
    )
    assert response.status_code == 201
    wallet_id_1 = response.json()['id']

    # Списываем средства
    wallets_reponse = client.put(
        "/wallets/{}/debit".format(wallet_id_1),
        params={'amount': -5000}
    )
    # Должна быть ошибка
    assert wallets_reponse.status_code == 400


def test_make_take_funds_neg2():
    # Создаем пользователя 1
    u1 = str(random.randint(1, 99999))
    response = client.post(
        "/users/",
        json={"name": "U " + u1, "first_name": "F " + u1, "last_name": "L " + u1, "middle_name": "M " + u1}
    )
    assert response.status_code == 201
    user_id_1 = response.json()['id']

    # Создаем кошелек
    wallet_json = {"user_id": user_id_1, "amount": 10000}
    response = client.post(
        "/wallets/",
        json=wallet_json
    )
    assert response.status_code == 201
    wallet_id_1 = response.json()['id']

    # Списываем средства
    wallets_reponse = client.put(
        "/wallets/{}/debit".format(wallet_id_1),
        params={'amount': 50000}
    )
    # Должна быть ошибка так как списываем больше чем есть
    assert wallets_reponse.status_code == 400



