# Описание

## Создание модели
Для генерации модели используется инструмент Jupyter Notebook, который использует каталог `learning` для чтения и сохранения данных.

Для создания модели выполнить тетрадку `english-learn.ipynb`.

Процесс создания может занять некоторое время, так для обработки 237 фильмов на компьютере без видиокарты требуется порядка 6 минут.

После завершения создания модели данные будут сохранены в каталоге `learning/models`:
* subtitle.model - обученная модель
* subtitle.scaler - объект для преобразования числовых данных
* subtitle.transformer - объект для преобразования текстовых данных в вектор

### Структура каталога learning
* data
    * movies_label.xlsx - файл с указанием категории знания английского языка
    * words.xlsx - словарь слов, который нужно знать в каждой категории
* models - каталог для хранения моделей
* subtitles - каталог для хранения субтитров (собственные данные можно сохранить в дополнительном каталоге)

## Запуск приложения
<pre>
python -m streamlit run app.py
</pre>

### Дополнительное ПО
<pre>
pip install -r requirements.txt
</pre>
Выполнение данный команды позволит загрузить дополнительные модули, без которых не не работает данное приложение

### Запуск контейнера
Если есть возможность и знания работы с docker, то можно воспользоваться заранее собранным контейнером
<pre>
docker pull akrasnov87/learn-english:latest
docker run -d --rm -p 8501:8501 -h learn akrasnov87/learn-english:latest
</pre>

Публичная страница: https://hub.docker.com/r/akrasnov87/learn-english

<b>Примечание</b>: для корректной работы требуется в контейнер устанавливать ту версию `scikit-learn`, которая установлено локально при сборки модели.

### Сборка
<pre>
docker build -t learn-english:latest .
docker run -d --rm -p 8501:8501 -h learn learn-english:latest
</pre>
<b>Примечание</b>: для отладки можно использовать можно использовать команд `-it` вместо `-d`