#это будет наш интерфейс взаимодействия с приложением
import requests
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder

class PetFriends:
    def __init__(self):
        self.base_url = "https://petfriends.skillfactory.ru/"

    def get_api_key(self, email: str, password: str):

        headers = {
            'email': email,
            'password': password
        }
        res = requests.get(self.base_url+'api/key', headers=headers)
        status = res.status_code
        result = ''
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    def get_list_of_pets(self, auth_key: json, filter: str):
        headers = {'auth_key': auth_key['key']}
        filter = {'filter': filter}

        res = requests.get(self.base_url+'api/pets', headers=headers, params=filter)
        status = res.status_code
        result = ''
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    def add_new_pet(self, auth_key: json, name: str, animal_type: str, age: str, pet_photo):
        data = MultipartEncoder(
            fields={
                'name': name,
                'animal_type': animal_type,
                'age': age,
                'pet_photo': (pet_photo, open(pet_photo, 'rb'), 'images/jpg')
            })
        headers = {'auth_key': auth_key['key'], 'Content-Type': data.content_type}
        res = requests.post(self.base_url+'api/pets', headers=headers, data=data)
        status = res.status_code
        result = ''
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    def delete_pet(self, auth_key: json, pet_id: str):
        headers = {'auth_key': auth_key['key']}

        res = requests.delete(self.base_url + f'api/pets/{pet_id}', headers=headers)
        status = res.status_code
        result = ''
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    def update_pet_info(self, auth_key: json, pet_id: str, name: str, animal_type: str, age: int):
        headers = {'auth_key': auth_key['key']}
        data = {
                'name': name,
                'animal_type': animal_type,
                'age': age
        }
        res = requests.put(self.base_url + f'api/pets/{pet_id}', headers=headers, data=data)
        status = res.status_code
        result = ''
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    def add_new_pet_simple(self, auth_key: json, name: str, animal_type: str, age: str):
        data = {
                'name': name,
                'animal_type': animal_type,
                'age': age
            }
        headers = {'auth_key': auth_key['key']}
        res = requests.post(self.base_url+'api/create_pet_simple', headers=headers, data=data)
        status = res.status_code
        result = ''
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    def add_pet_photo(self, auth_key: json, pet_id: str, pet_photo):
        data = MultipartEncoder(
            fields={
                'pet_photo': (pet_photo, open(pet_photo, 'rb'), 'images/jpeg')
            })
        headers = {'auth_key': auth_key['key'], 'Content-Type': data.content_type}
        res = requests.post(self.base_url+f'/api/pets/set_photo/{pet_id}', headers=headers, data=data)
        status = res.status_code
        result = ''
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result
# ----------------------- 10 ДОПОЛНИТЕЛЬНЫХ ТЕСТОВ -----------------------
# 1) негативный тест 1-го эндпоинта POST /api/create_pet_simple. Если вернётся 200, то питомец создан без выполнения
# скрипта на xss-уязвимость. За основу беру ф-ю def add_new_pet_simple, не дублирую ее здесь

# 2) тест 1-го эндпоинта POST /api/create_pet_simple: посмотрим, добавит ли он питомца с именем в 5000 знаков. Имя находится в settings под
# переменной long_name и не обрежет ли имя при добавлении

# 3) негативный тест 2-го эндпоинта GET /api/key. Попытка получить авторизационный ключ с неверными данными
    # За основу беру ф-ю def get_api_key, не дублирую ее здесь

# 4) негативный тест 3-го эндпоинта GET /api/pets. Попытка получить список всех питомцев с неверным авторизационным ключом
    def get_list_of_pets_negative(self, auth_key: json, filter: str):
        headers = {'auth_key': auth_key}
        filter = {'filter': filter}

        res = requests.get(self.base_url+'api/pets', headers=headers, params=filter)
        status = res.status_code
        result = ''
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

# 5) тест 4-го эндпоинта POST /api/pets: загрузка картинки разрешением 11233 x 6900 пикселей и весом 50 Мб. За основу
    # беру ф-ю def add_new_pet, не дублирую ее здесь

# 6) негативный тест 5-го эндпоинта POST /api/pets/set_photo/{pet_id}. Попытка добавить фото питомца в формате tiff
    def add_pet_photo_with_tiff(self, auth_key: json, pet_id: str, pet_photo):
        data = MultipartEncoder(
            fields={
                'pet_photo': (pet_photo, open(pet_photo, 'rb'), 'images/tiff')
            })
        headers = {'auth_key': auth_key['key'], 'Content-Type': data.content_type}
        res = requests.post(self.base_url+f'/api/pets/set_photo/{pet_id}', headers=headers, data=data)
        status = res.status_code
        result = ''
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

# 7) негативный тест 6-го эндпоинта DELETE /api/pets/{pet_id}. Попытка удалить чужого питомца с проверкой,
# что он не является моим. За основу беру ф-ю def delete_pet, не дублирую ее здесь

# 8) негативный тест 5-го эндпоинта POST /api/pets/set_photo/{pet_id}. Попытка обновить фото чужого питомца с проверкой
# того, что питомец не является моим. За основу беру ф-ю def add_pet_photo, не дублирую ее здесь

# 9) негативный тест 7-го эндпоинта PUT /api/pets/{pet_id}. Попытка обновить информацию той же информацией,
# что уже указана на сайте, и при этом ничего не ломается. За основу беру ф-ю def update_pet_info, не дублирую ее здесь

# 10) негативный тест 7-го эндпоинта PUT /api/pets/{pet_id}. Попытка обновить информацию у удалённого питомца. За
# основу беру ф-ю def update_pet_info, не дублирую ее здесь