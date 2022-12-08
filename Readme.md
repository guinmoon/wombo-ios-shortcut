Shortcut для генерации изображений с помощью [Wombo Dream](https://dream.ai/create)

Для работы скрипта необходимо установить [a-shell](https://holzschu.github.io/a-Shell_iOS/) 

[![a-shell](./dist/imgs/icon0.jpg)](https://holzschu.github.io/a-Shell_iOS/)

Если приложение не доступно в вашей стране, можно установить его через [TestFlight](https://testflight.apple.com/join/WUdKe3f4)

[![TestFlight](./dist/imgs/icon3.png)](https://testflight.apple.com/join/WUdKe3f4)

Скопируйте файлы ```wombo_create.py, styles.txt, words1.txt, words2.txt``` в директорию доступную на вашем устройстве

Установите необходимые команды и указжите расположение файлов ```wombo_create.py, styles.txt, words1.txt, words2.txt```

![TestFlight](./dist/imgs/00.jpg)

Команда генерирует случайный текст и выбирает случайный стиль:

[![icon1](./dist/imgs/icon1.png )](https://www.icloud.com/shortcuts/afc0c2ddc1f54916b2879779e91e605c) 
 Что приснилось?

Команда позволяет ввести текст и указать стиль: 

[![icon1](./dist/imgs/icon2.png )](https://www.icloud.com/shortcuts/da61b07fcc4a4904ae7c15b5839c5cde) 
 Нарисуй сон

Для того чобы полученое изображение автоматически устанавливалось в качестве обоев необходимо в конце команды добавить действие "Установить фото в качестве обоев"

Для обновления списка стилей в ```a-shell``` выполните:
```
python $SHORTCUTS/wombo_create
```


Генерация изображения без ```Shortcut```:
```
python3 wombo_create.py [OPTIONS]
OPTIONS:
    -k KEY, identify_key если не указан используется то что в коде
    -u, обновить файл со стилями
    -i, продолжить загрузку после получения ID
    -o, продолжить загрузку после получения ID (1 итерация)
    -c, обрезать изображение 
    -d, загрузить изображение
    -s STYLE, стиль если указано r программа выберет сама
    -p PROMPT,  текст если указано r программа выберет сама
```
```
python3 wombo_create.py && \
 python3 wombo_create.py -i && \
  python3 wombo_create.py -d && \
   python3 wombo_create.py -c
```