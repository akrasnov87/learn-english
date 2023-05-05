import streamlit as st

import pandas as pd
from joblib import load
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import util
import os.path

st.title('Уровень знания английского')

st.subheader('Определение требуемого уровня знания английского языка по субтитрам фильма')

fname = 'learning/data/words.xlsx'

if os.path.isfile(fname):
    uploaded_file = st.file_uploader('Выбрать файл в формате *.srt', type='srt', help='Файлы SRT – это формат субтитров, который поддерживается большинством программных видеопроигрывателей, а также программным обеспечением для их создания и редактирования.')
    
    if uploaded_file is not None:
        #nltk.download('stopwords') python -m nltk.downloader stopwords  
        #nltk.download('punkt')  python -m nltk.downloader punkt  
        all_stopwords = stopwords.words('english')
        porter = PorterStemmer()

        txt = st.text("Процесс обработки может занять некоторое время. Подождите...")

        encodings = ['utf-8', 'ansi', 'utf-16-le']
        
        for encoding in encodings:
            try:
                subtitles, subtitles_info = util.read_subs(uploaded_file.name, uploaded_file.getvalue().decode(encoding))
                if len(subtitles_info) > 0:
                    break
            except:
                pass

        # ниже предобработка данных
        df_subtitles = pd.DataFrame(subtitles, columns=['movie', 'text'])
        df_subtitles.set_index('movie', inplace=True)    

        df_subtitles_info = pd.DataFrame(subtitles_info, columns=['movie', 'start', 'end', 'length', 'milliseconds'])
        df_subtitles_info = df_subtitles_info.groupby(['movie']).aggregate({'start': 'min', 'end': 'max', 'milliseconds': 'mean'})

        df_subtitles_info['len_sec'] = df_subtitles_info['end'].apply(util.time2seconds)
        df_subtitles = df_subtitles.merge(df_subtitles_info, how='left', left_index=True, right_index=True)
        df_subtitles.drop(columns=['start', 'end'], inplace=True)

        if os.path.isfile(fname):
            df_words = pd.read_excel(fname)
            df_words = df_words.groupby(['level', 'word'])['file'].count().reset_index()

            dict_words = {}

            for level in df_words['level'].unique():
                df_subtitles[level] = 0
                dict_words[level] = df_words.loc[df_words['level'] == level, 'word'].values
                
            df_subtitles = df_subtitles.apply(lambda x: util.set_category_count(x, df_words, dict_words), axis=1)
            df_subtitles['porter_text'] = df_subtitles['text'].apply(lambda x: util.tokenizer_porter(x, all_stopwords, porter))    

            # загружаем вспомогательные данные и модели
            cls = load('learning/models/subtitle.model')
            scaler = load('learning/models/subtitle.scaler')
            transformer = load('learning/models/subtitle.transformer')
            numeric = ['A1', 'A2', 'B1', 'B2', 'C1']

            features = df_subtitles[['porter_text', 'A1', 'A2', 'B1', 'B2', 'C1']]
            features_ohe = features.copy()
            features_ohe[numeric] = scaler.transform(features_ohe[numeric])
            features_ohe = transformer.transform(features_ohe)

            pred = cls.predict(features_ohe)
            st.markdown(f'Требуемый уровень знаний английского языка для просмотра фильма: <b>{pred[0]}</b>', unsafe_allow_html=True)

            txt.text('')
else:
    st.markdown("<span style='color: red'>Словарь английских слов не найден</span>", unsafe_allow_html=True)


        