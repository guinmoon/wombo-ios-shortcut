Shortcut для генерации изображений с помощью [Wombo Dream](https://dream.ai/create)

Для работы скрипта необходимо установить [a-shell](https://holzschu.github.io/a-Shell_iOS/) 

[![a-shell](./dist/imgs/icon0.jpg)](https://holzschu.github.io/a-Shell_iOS/)

Если приложение не доступно в вашей стране, можно установить его через [TestFlight](https://testflight.apple.com/join/WUdKe3f4)

[![TestFlight](./dist/imgs/icon3.png)](https://testflight.apple.com/join/WUdKe3f4)

Скопируйте файлы ```wombo_create.py, styles.txt, words1.txt, words2.txt``` в директорию доступную на вашем устройстве

Установите необходимые команды и указжите расположение файлов ```wombo_create.py, styles.txt, words1.txt, words2.txt```

![TestFlight](./dist/imgs/00.jpg)

Команда генерирует случайный текст и выбирает случайный стиль:

[![icon1](./dist/imgs/icon1.png )](https://www.icloud.com/shortcuts/f328c02f8ebf4f02849edd7398d87bfe) 
 Что приснилось?

Команда позволяет ввести текст и указать стиль: 

[![icon1](./dist/imgs/icon2.png )](https://www.icloud.com/shortcuts/547142dbf33449f6859eab4386a88fd0) 
 Нарисуй сон

Команда завершит ресунок при ошибке

[![icon1](./dist/imgs/icon4.png )](https://www.icloud.com/shortcuts/619363e9eeea42afba0611ed85e37248) 
 Закончи рисунок

Для того чобы полученое изображение автоматически устанавливалось в качестве обоев необходимо в конце команды добавить действие "Установить фото в качестве обоев"

Для обновления списка стилей в ```a-shell``` выполните:
```
python $SHORTCUTS/wombo_create -u
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