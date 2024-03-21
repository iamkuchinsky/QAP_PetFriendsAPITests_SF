import os

from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Барбоскин', animal_type='двортерьер',
                                     age='4', pet_photo='images/cat1.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_successful_add_pet_simple(name='Кефир', animal_type='кот',
                                   age='3'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_add_photo_of_pet(pet_photo='images\cat1.jpg'):
    """Проверяем возможность добавления фото питомца первому животному в списке моих питомцев"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    # Получаем полный путь файла изоброжения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Проверяем, есть ли уже фотография у питомца
    if len(my_pets['pets']) == 0:
        pf.create_pet_simple(auth_key, "Феликс", "Бегемот", "2")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

        pet_id = my_pets['pets'][0]['id']
        # Добавляем фото питомца
        status, result = pf.add_photo_of_pet(auth_key, pet_id, pet_photo)
        assert status == 200
        assert 'pet_photo' in result
    else:
        print("У питомца уже есть фото")


def test_get_api_key_for_unregistered_user(email=invalid_email, password=invalid_password):
    """ Проверяем что запрос api ключа возвращает статус 403,ключ не предоставляется, т.к вводим неверный email и
     неверный пароль"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403
    assert 'key' not in result


def test_get_api_key_for_invalid_mail_valid_pass(email=invalid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 403,ключ не предоставляется, т.к введен неверный пароль"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403
    assert 'key' not in result


def test_get_api_key_for_valid_mail_invalid_pass(email=valid_email, password=invalid_password):
    """ Проверяем что запрос api ключа возвращает статус 403,ключ не предоставляется, т.к введена неверная почта"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403
    assert 'key' not in result


def test_successful_add_photo_of_pet_incorrect_format(pet_photo='images\haha_image.txt'):
    """БАГ! Проверяем, что при добавлении фото питомца неккоретного формата вернется код 400. Возвращается код 500"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    # Получаем полный путь файла изоброжения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    pf.create_pet_simple(auth_key, "Мурчик", "Кошак", "2")
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    pet_id = my_pets['pets'][0]['id']
    # Добавляем фото питомца
    status, result = pf.add_photo_of_pet(auth_key, pet_id, pet_photo)
    assert status == 400
    assert 'pet_photo' in result


def test_successful_add_photo_of_pet_incorrect_size(pet_photo='images\what_this.zip'):
    """БАГ! Проверяем, что при добавлении фото питомца неккоретного формата и размера вернется код 400. Возвращается
    код 500"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    # Получаем полный путь файла изоброжения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    pf.create_pet_simple(auth_key, "Арчи", "Собака", "2")
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    pet_id = my_pets['pets'][0]['id']
    # Добавляем фото питомца
    status, result = pf.add_photo_of_pet(auth_key, pet_id, pet_photo)
    assert status == 400


def test_get_all_pets_with_valid_key_332(animal_type = 'корги', age = '7'):
    """БАГ!Проверяем, что без ввода обязательного поля запрос вернется с кодом 400. Питомец создается без атрибута Name"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.create_pet_simple(auth_key, name=None, animal_type=animal_type, age=age)
    assert status == 400


def test_add_new_pet_with_invalid_image_size(name='Шарик', animal_type='дворняга',
                                             age='10', pet_photo='images/what_this.zip'):
    """БАГ! Проверяем что при добавлении некорректного размера фото вернется код 400. Получаем код 200"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400


def test_add_new_pet_with_invalid_image_format(name='Шарик', animal_type='дворняга',
                                               age='10', pet_photo='images/haha_image.txt'):
    """БАГ! Проверяем что при добавлении некорректного формата фото вернется код 400. Получаем код 200"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400
