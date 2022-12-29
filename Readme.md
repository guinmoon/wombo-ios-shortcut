Shortcut для генерации изображений с помощью [Wombo Dream](https://dream.ai/create)

Присуствует возможность генерации случайной фразы, а так же ее трансформации в [Yandex Balaboba](https://yandex.ru/lab/yalm)

Для работы скрипта необходимо установить [a-shell-mini](https://apps.apple.com/us/app/a-shell-mini/id1543537943) 

[![a-shell-mini](./dist/imgs/icon0.jpg)](https://apps.apple.com/us/app/a-shell-mini/id1543537943)

Если приложение не доступно в вашей стране, можно установить его через [TestFlight](https://testflight.apple.com/join/REdHww5C)

[![TestFlight](./dist/imgs/icon3.png)](https://testflight.apple.com/join/WUdKe3f4)

Скопируйте файлы ```wombo_create.py, styles.txt, words1.txt, words2.txt``` в директорию доступную на вашем устройстве

Установите необходимые команды и указжите расположение файлов ```wombo_create.py, styles.txt, words1.txt, words2.txt```

![TestFlight](./dist/imgs/00.jpg)

Команда генерирует случайный текст и выбирает случайный стиль:

[![icon1](./dist/imgs/icon1.png )](https://www.icloud.com/shortcuts/803621a053c24dd6a01cd560a474dad5) 
 Что приснилось?

Команда позволяет ввести текст и указать стиль: 

[![icon1](./dist/imgs/icon2.png )](https://www.icloud.com/shortcuts/adf73ca29b6e487eadfa9093b35b4d41) 
 Нарисуй сон

Команда завершит ресунок при ошибке

[![icon1](./dist/imgs/icon4.png )](https://www.icloud.com/shortcuts/d710141096fd4265b655afc45e2dd804) 
 Закончи рисунок

Для того чобы полученое изображение автоматически устанавливалось в качестве обоев необходимо в конце команды добавить действие "Установить фото в качестве обоев"

|![icon1](./dist/imgs/wp.gif)|![icon1](./dist/imgs/auto_gen.gif)|

Для обновления списка стилей в ```a-shell-mini``` выполните:
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
    -r, поместить изображение в директорию out после crop    
    -d, загрузить изображение    
    -s STYLE, стиль если указано r программа выберет сама
    -b, не использовать стили из черного списка styles_blist
    -p PROMPT,  текст если указано r программа выберет сама, если указано -b используется yandex balaboba
```
```
python3 wombo_create.py -p b -b && \
python3 wombo_create.py -i && \
python3 wombo_create.py -d && \
python3 wombo_create.py -c
```