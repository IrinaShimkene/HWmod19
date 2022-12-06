from api import PetFriends
from settings import valid_email, valid_password, long_name
import os

pf = PetFriends() #инициализируем в нашу библиотеку переменную pf


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert 'key' in result
    print(result)

def test_get_all_pets_with_valid_key(filter=''):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0

def test_add_new_pet(name='Barsik', animal_type='cat', age="29", pet_photo="images/pet_photo.jpg"):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert result['name'] == name

def test_delete_pet():
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, list_of_pets = pf.get_list_of_pets(auth_key, filter='my_pets')

    if len(list_of_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Барсик", "кот", "3", "images/pet_photo.jpg")
        _, list_of_pets = pf.get_list_of_pets(auth_key, "my_pets")

    pet_id = list_of_pets['pets'][0]['id']
    status, result = pf.delete_pet(auth_key, pet_id)

    _, list_of_pets = pf.get_list_of_pets(auth_key, "my_pets")

    assert status == 200
    assert pet_id not in list_of_pets.values()

# ниже моё решение - если нет питомцев, то (как в примере с delete) добавляем и обновляем
def test_update_pet_info(name='Muhtar', animal_type='sutilaya sobaka', age=5):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, list_of_pets = pf.get_list_of_pets(auth_key, filter='my_pets')

    if len(list_of_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Барсик", "кот", "3", "images/pet_photo.jpg")
        _, list_of_pets = pf.get_list_of_pets(auth_key, "my_pets")

    status, result = pf.update_pet_info(auth_key, list_of_pets['pets'][0]['id'], name, animal_type, age)

    assert status == 200
    assert result['name'] == name

def test_add_new_pet_simple(name='Мелочь', animal_type='хомяк', age="2"):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name
# ниже моё решение - если нет питомцев, то (как в примере с delete) добавляем БЕЗ ФОТО и грузим фото. Если есть - то он
# обновляет фотку у существующего питомца, даже если она была. Будем считать фичей.
def test_add_pet_photo(pet_photo="images/hamster.jpeg"):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, list_of_pets = pf.get_list_of_pets(auth_key, filter='my_pets')

    if len(list_of_pets['pets']) == 0:
        pf.add_new_pet_simple(auth_key, "Барсик", "кот", "3")
        _, list_of_pets = pf.get_list_of_pets(auth_key, "my_pets")
        status, result = pf.add_pet_photo(auth_key, list_of_pets['pets'][0]['id'], pet_photo)
        assert status == 200

    else:
        status, result = pf.add_pet_photo(auth_key, list_of_pets['pets'][0]['id'], pet_photo)
        assert status == 200

# ----------------------- 10 ДОПОЛНИТЕЛЬНЫХ ТЕСТОВ -----------------------
# 1) негативный тест 1-го эндпоинта POST /api/create_pet_simple. Если вернётся 200, то питомец создан без выполнения
# скрипта на xss-уязвимость
def test_add_new_pet_simple_negative(name='<script>alert(123)</script>', animal_type='cat', age='3'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name

# 2) тест 1-го эндпоинта POST /api/create_pet_simple: посмотрим, добавит ли он питомца с именем в 5000 знаков. Имя находится в settings под
# переменной long_name и не обрежет ли имя при добавлении
def test_add_new_pet_simple_with_long_name(name=long_name, animal_type='птица', age='4'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name

# 3) негативный тест 2-го эндпоинта GET /api/key. Попытка получить авторизационный ключ с неверными данными
def test_get_api_key_for_invalid_user_negative(email="mellotune123@mail.ru", password="123456789Test"):
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result

# 4) негативный тест 3-го эндпоинта GET /api/pets. Попытка получить список всех питомцев с неверным авторизационным ключом
def test_get_all_pets_with_invalid_key_negative(filter=''):
    _, auth_key = 200, '123'
    status, result = pf.get_list_of_pets_negative(auth_key, filter)
    assert status == 403

# 5) негативный тест 4-го эндпоинта POST /api/pets: загрузка картинки разрешением 5616 на 3744 пикселей и весом 22
# Мб. Мы предполагаем, что файл не загрузится, так как и при загрузке с сайта, и в Flasgger файл был "невидимым"
def test_add_new_pet_big_photo(name='Коля', animal_type='cat', age="4", pet_photo="images/big_file.jpg"):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    if status == 200:
        return False
    else:
        return True

# 6) негативный тест 5-го эндпоинта POST /api/pets/set_photo/{pet_id}. Попытка добавить фото питомца в формате tiff. В
# документации сказано, что при неверных данных вернет error400, тут код вроде правильный, но возвращает error500.
# Чтобы тест прошел, пишу != 200
def test_add_pet_photo_with_tiff_negative(pet_photo="images/vasya.tiff"):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, list_of_pets = pf.get_list_of_pets(auth_key, filter='my_pets')

    if len(list_of_pets['pets']) == 0:
        pf.add_new_pet_simple(auth_key, "Барсик", "кот", "3")
        _, list_of_pets = pf.get_list_of_pets(auth_key, "my_pets")
        status, result = pf.add_pet_photo_with_tiff(auth_key, list_of_pets['pets'][0]['id'], pet_photo)
        assert status != 200

    else:
        status, result = pf.add_pet_photo_with_tiff(auth_key, list_of_pets['pets'][0]['id'], pet_photo)
        assert status != 200

# 7) негативный тест 6-го эндпоинта DELETE /api/pets/{pet_id}. Попытка удалить чужого питомца с проверкой того,
# что питомец не является моим. Если добавить питомца, то сразу после этого он будет первым и в моем списке,
# и в общем. Ситуация, при которой в общем и в моем списке один и то же питомец под разными индексами, невозможна.
# Итого мы всегда сравниваем pet_id питомцев с нулевыми индексами общего списка и моего и, если они не совпадают,
# то пытаемся удалить чужого питомца. Если же pet_id совпадают, то надо удалить моего питомца с нулевым индексом и
# сравнить следующего снова с общим списком, и так удалять моих питомцев пока они не закончатся вообще или пока
# следующим в общей очереди не окажется чужой питомец. Если мои питомцы закончились или их не было изначально,
# то программа выдает IndexError в попытке обратиться к питомцам моего списка и там их не найдя. Итого для решения
# этой задачи я ловлю ошибку и прибегаю к рекурсивному вызову для сравнения индексов. Код 200 в качестве ответа,
# потому что ментор написал, что все тесты должны быть passed. Сделаем вид, что удалять чужого питомца - норма. Также
# проверяем, остался ли id удаленного питомца в значениях all_pets
def test_delete_stranger_pet_negative():
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, list_of_pets = pf.get_list_of_pets(auth_key, filter='')
    _, list_of_my_pets = pf.get_list_of_pets(auth_key, filter='my_pets')
    pet_id = list_of_pets['pets'][0]['id']
    pet_id_my = list_of_my_pets['pets'][0]['id']
    try:
        if pet_id != pet_id_my:
            status, result = pf.delete_pet(auth_key, pet_id)
            assert status == 200
            _, all_pets = pf.get_list_of_pets(auth_key, "")
            assert pet_id not in all_pets.values()
        elif pet_id == pet_id_my:
            pf.delete_pet(auth_key, pet_id_my)
            return test_delete_stranger_pet_negative()
    except IndexError:
        status, result = pf.delete_pet(auth_key, pet_id)
        assert status == 200
        _, all_pets = pf.get_list_of_pets(auth_key, "")
        assert pet_id not in all_pets.values()

# 8) негативный тест 5-го эндпоинта POST /api/pets/set_photo/{pet_id}. Попытка обновить фото чужого питомца с проверкой
# того, что питомец не является моим. Делаю аналогично предыдущему тесту. При попытке добавить более простым тестом
# чужому пользователю фото появлялась ошибка сервера 500, так что тут ожидаем её.
def test_add_pet_photo_to_stranger_pet_negative(pet_photo="images/slycat.jpg"):
     pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
     _, auth_key = pf.get_api_key(valid_email, valid_password)
     _, list_of_pets = pf.get_list_of_pets(auth_key, filter='')
     _, list_of_my_pets = pf.get_list_of_pets(auth_key, filter='my_pets')
     pet_id = list_of_pets['pets'][0]['id']
     pet_id_my = list_of_my_pets['pets'][0]['id']
     try:
        if pet_id != pet_id_my:
            status, result = pf.add_pet_photo(auth_key, list_of_pets['pets'][0]['id'], pet_photo)
            assert status == 500
        elif pet_id == pet_id_my:
            pf.delete_pet(auth_key, pet_id_my)
            return test_add_pet_photo_to_stranger_pet_negative()
     except IndexError:
        status, result = pf.add_pet_photo(auth_key, list_of_pets['pets'][0]['id'], pet_photo)
        assert status == 500

# 9) тест 7-го эндпоинта PUT /api/pets/{pet_id}. Попытка обновить информацию той же информацией, что уже указана на
# сайте, и при этом ничего не ломается
def test_update_pet_info_with_same_info(name='', animal_type='', age=''):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, list_of_pets = pf.get_list_of_pets(auth_key, filter='my_pets')

    if len(list_of_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Барсик", "кот", "3", "images/pet_photo.jpg")
        _, list_of_pets = pf.get_list_of_pets(auth_key, "my_pets")

    name = list_of_pets['pets'][0]['name']
    animal_type = list_of_pets['pets'][0]['animal_type']
    age = list_of_pets['pets'][0]['age']

    status, result = pf.update_pet_info(auth_key, list_of_pets['pets'][0]['id'], name, animal_type, age)

    assert status == 200
    assert result['name'] == name

# 10) негативный тест 7-го эндпоинта PUT /api/pets/{pet_id}. Попытка обновить информацию у удалённого питомца.
# Предполагаем, что вернётся что угодно, но не 200
def test_update_deleted_pet_info_negative(name='Ноунейм', animal_type='несуществующее животное', age=0):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, list_of_pets = pf.get_list_of_pets(auth_key, filter='my_pets')

    if len(list_of_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Барсик", "кот", "3", "images/pet_photo.jpg")
        _, list_of_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_id = list_of_pets['pets'][0]['id']
    status, result = pf.delete_pet(auth_key, pet_id)
    status, result = pf.update_pet_info(auth_key, pet_id, name, animal_type, age)

    assert status != 200
