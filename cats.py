import requests
from tqdm import tqdm
import json

# Создание класса с общей сессией
class BaseAPI:
    def __init__(self):
        self.session = requests.Session()

class CataasAPI(BaseAPI):
    def get_cat(self, text):
        url = f'https://cataas.com/cat/says/{text}'
        response = self.session.get(url)
        # Страховка и остановка программы при ошибке
        response.raise_for_status()
        return response.content

class YandexDiskAPI(BaseAPI):
    base_url = 'https://cloud-api.yandex.net'

    def __init__(self, token):
        super().__init__()
        self.session.headers.update({'Authorization': f'OAuth {token}'})

    def create_folder(self, folder):
        params = {'path': folder}
        response = self.session.put(url=f'{self.base_url}/v1/disk/resources',
                                params=params)
        # Функция вернет результат, если папка создана или уже существует
        return response.status_code == 201 or response.status_code == 409

    def delete_folder(self, folder):
        params = {'path': folder}
        response = self.session.delete(url=f'{self.base_url}/v1/disk/resources',
                                   params=params)
        return response.status_code == 204

    def upload_file(self, path, file):
        # Разрешаем перезаписывать файл, если он уже существует
        params = {'path': path, 'overwrite': 'true'}
        response_upload = self.session.get(url=f'{self.base_url}/v1/disk/resources/upload',
                                           params=params)
        response_upload.raise_for_status()

        # Извлечение ссылки
        upload_link = response_upload.json()['href']
        # Отправка файла по ссылке
        response = requests.put(upload_link, data=file)
        response.raise_for_status()
        return response.status_code

# Данные от пользователя
user_text = input('Введите текст для картинки: ')
user_token = input('Введите токен с Полигона Яндекс.Диска: ')

cat_1 = CataasAPI()
ya_1 = YandexDiskAPI(user_token)
group_name = 'PY-142'

# Настройка прогресс-бара
pbar = tqdm(total=3, desc='Выполнение', unit='этап')

pbar.set_description('Скачивание котика')
image_cat = cat_1.get_cat(user_text)
pbar.update(1)

pbar.set_description('Телепортация котика в папку')
ya_1.create_folder(group_name)
file_path = f'{group_name}/{user_text}.jpg'
ya_1.upload_file(file_path, image_cat)
pbar.update(1)

pbar.set_description('Сохранение информации в JSON')
data = [
    {
        'file_name': f'{user_text}.jpg',
        'size': len(image_cat)
    }
]

with open('result.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)
pbar.update(1)
pbar.close()

# Проверка файла json
print('Чтение JSON: ')
with open('result.json', 'r', encoding='utf-8') as f:
    print(json.dumps(json.load(f), indent=4, ensure_ascii=False))






