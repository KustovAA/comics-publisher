# Публикация комиксов

Проект позволяет публиковать комиксы с сайта https://xkcd.com в сообщество вконтакте
## Окружение

### Зависимости
* Django
* environs
* requests

### Как установить
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Переменные окружения:
```
VK_APP_ID - id приложения vk
VK_ACCESS_TOKEN - token полученный с помощью Implicit Flow
VK_GROUP_ID - id сообщества vk
```

### Запуск
 ```
 python main.py
 ```
