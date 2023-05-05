"""
Специальная библиотека для обработки входных данных для определения уровня знаний английского яыка для просмотра фильма по субтитру
"""

import re
import pysrt
from nltk.tokenize import word_tokenize
import string

HTML = r'<.*?>' # html тэги меняем на пробел
TAG = r'{.*?}' # тэги меняем на пробел
COMMENTS = r'[\(\[][A-Za-z ]+[\)\]]' # комменты в скобках меняем на пробел
UPPER = r'[[A-Za-z ]+[\:\]]' # указания на того кто говорит (BOBBY:)
LETTERS = r'[^a-zA-Z\'.,!? ]' # все что не буквы меняем на пробел 
SPACES = r'([ ])\1+' # повторяющиеся пробелы меняем на один пробел
DOTS = r'[\.]+' # многоточие меняем на точку
SYMB = r"[^\w\d'\s]" # знаки препинания кроме апострофа

def clean_subs(subs):
    """
    Очистка субтитров

    Параметры:
    ----------
    subs: SubRipFile - объект с информацией о субтитрах

    Результат:
    ----------
    Отформатированная строка
    """
    subs = subs[1:] # удаляем первый рекламный субтитр
    txt = re.sub(HTML, ' ', subs.text) # html тэги меняем на пробел
    txt = re.sub(COMMENTS, ' ', txt) # комменты в скобках меняем на пробел
    txt = re.sub(UPPER, ' ', txt) # указания на того кто говорит (BOBBY:)
    txt = re.sub(LETTERS, ' ', txt) # все что не буквы меняем на пробел
    txt = re.sub(DOTS, r'.', txt) # многоточие меняем на точку
    txt = re.sub(SPACES, r'\1', txt) # повторяющиеся пробелы меняем на один пробел
    txt = re.sub(SYMB, '', txt) # знаки препинания кроме апострофа на пустую строку
    txt = re.sub('www', '', txt) # кое-где остаётся www, то же меняем на пустую строку
    txt = txt.lstrip() # обрезка пробелов слева
    txt = txt.encode('ascii', 'ignore').decode() # удаляем все что не ascii символы   
    txt = txt.lower() # текст в нижний регистр
    return txt

def read_subs(movie, str):
    """
    Чтение информации по субтитрам

    Параметры:
    ----------
    movie: string - название фильма
    str: string - информация из файла с субтитрами (строки из файла)

    Результат:
    ----------
    subtitles: array - общая информация по фильму
    subtitles_info: array - статистичекая информация по фильму
    """
    subtitles = []
    subtitles_info = []

    path = None
    subs = None
    
    subs = pysrt.from_string(str)
    
    try:
        subtitles.append([movie, clean_subs(subs)])
        
        for i in range(len(subs)):
            if i == 0:
                # пропускаем первый рекламный субтитр
                continue
            len_ms = subs[i].end - subs[i].start
            if len_ms.seconds > 0:
                len_ms = (len_ms.seconds * 1000) + len_ms.milliseconds
            else:
                len_ms = len_ms.milliseconds
                
            subtitles_info.append([movie, subs[i].start, subs[i].end, subs[i].end - subs[i].start, len_ms])
        
    except Exception as e:
        print(f'Ошибка чтения файла {path}: {e}')
    
    return subtitles, subtitles_info

def time2seconds(time):
    """
    Преобразование объекта datetime.time в секунды

    Параметры:
    ----------
    time: datetime.time - время

    Результат:
    ----------
    integer - количество секунд
    """
    return (time.to_time().hour * 60 * 60) + (time.to_time().minute * 60) + (time.to_time().second)

def tokenizer_porter(text, all_stopwords, porter):
    """
    Преобразование строки: токенизация, стреминг

    Параметры:
    ----------
    text: string - входная строка
    all_stopwords: [string] - стоп-слова
    porter: PorterStemmer - алгоритм

    Результат:
    ----------
    string - преобразованная строка
    """
    if text == text:
        text = text.translate(str.maketrans('', '', string.punctuation))
        # чистим от стоп-слов
        words = word_tokenize(text)
        words = [word for word in words if word.casefold() not in all_stopwords]

        return " ".join([porter.stem(word) for word in words])
    else:
        return None
    
def set_category_count(row, df_words, dict_words):
    """
    Вычисление количества слов в определённой категории

    Параметры:
    ----------
    row: Serias - данные
    df_words: DataFrame - слова из категорий
    dict_words: dict - вспомагательный словарь

    Результат:
    ----------
    Serias - преобразованные данные
    """
    words = word_tokenize(row['text'])

    for level in df_words['level'].unique():
        row[level] = len([word for word in words if word.lower() in dict_words[level]]) / len(words)
    return row