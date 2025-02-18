import pandas as pd
import re
from pymystem3 import Mystem
from gensim.models import KeyedVectors
from gensim.models.phrases import Phrases, Phraser
import gensim
import pymorphy2
from collections import Counter
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import precision_recall_curve
import pymorphy2
from tqdm import tqdm
import time 

df = pd.read_csv("/path/to/SVO_108.csv", sep=";")
df['resultDate'] = pd.to_datetime(df['resultDate'], format='%d.%m.%Y')
print("Файл загружен!")

# преобразуем данные в колонке 'text' в строки (были объектами)
df['text'] = df['text'].astype('string')

# удаляем "запрещённые знаки" из текстов заседаний
def remove_illegal_characters(value):
    if isinstance(value, str):
        # This regex matches characters in the ranges:
        # \x00 - \x08, \x0B, \x0C, and \x0E - \x1F
        return re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', value)
    return value

new_df = df.applymap(remove_illegal_characters)

# выделяем подсет данных для более быстрой обработки
new_df = new_df[['id', 'text', 'link_text']]

# удаляем строки, где текст заседаний короче 10 символов
new_df = new_df[new_df['text'].str.len() > 10]

# приводим тексты заседаний в прописные буквы, удаляем все не-буквы
new_df['text'] = new_df['text'].str.lower()
new_df['text'] = new_df['text'].str.replace(r'[^а-яА-ЯёЁ\s]', ' ', regex=True)
new_df['text'] = new_df['text'].str.replace(r'\s+', ' ', regex=True)

# удаляем строки с закрытыми текстами длиннее 10 символов
new_df = new_df[~new_df['text'].str.contains('не подлежит размещению')]
new_df = new_df[~new_df['text'].str.contains('судебный акт не подлежит публикации')]
print("Начинаем фильтровать тексты")

# создаём предварительный фильтр, чтобы отобрать дела, в которых упоминается война
rough_words = [
            r'сво[\s]',
            r'зон\w+[\s]сво',
            r'специальн\w+[\s]военн\w+[\s]операц\w+'
]
rough_pattern = re.compile('|'.join(rough_words), re.IGNORECASE)

# функция, которая проверяет тексты приговоров по ключевым словам
def is_veteran(text):
    if text is None:  # Check if tokens is None
        return "!"
    return 'yes' if rough_pattern.search(text) else None
new_df['pre_veteran'] = new_df['text'].apply(is_veteran)

# проверяем и выводим, сколько приговоров осталось
a = len(new_df.loc[new_df['pre_veteran'] == 'yes', ['id']])
print(f"Всего нашлось {a} приговоров про войну")

# выделяем только нужные нам дела
filtered_df = new_df[new_df['pre_veteran'] == 'yes']

# функция для "нормализации" текста, т.е. приведения каждого слова в инфинитивную форму
morph = pymorphy2.MorphAnalyzer()

def normalize_text(text):
    if not isinstance(text, str):  # Handle non-string values
        return ""
    tokens = text.split()  # Tokenize by splitting on whitespace
    normalized_tokens = [morph.parse(word)[0].normal_form for word in tokens]  # Lemmatize each token
    return " ".join(normalized_tokens)  # Join normalized tokens back into a single string

# применение функции к базе данных
# занимает довольно много времени 
# 309 наблюдений — 8,5 минут
# 573 наблюдений — 26 минут
print("Начинаем нормализовать тексты...")

filtered_df['norm_text'] = filtered_df['text'].apply(normalize_text)

# выделяем из слов-инфинитивов устойчивые словосочетания (пр., Российская Федерация)
filtered_df["tokens"] = filtered_df["norm_text"].str.split()
# тренируем модель Phrases распознавать словосочетания из двух слов
bigram_model = Phrases(filtered_df["tokens"], min_count=2, threshold=10) 
bigram_phraser = Phraser(bigram_model)  
# превращаем отдельные слова в фразы (такого_вида)
filtered_df["phrases"] = filtered_df["tokens"].apply(lambda tokens: bigram_phraser[tokens])
# вставляем фразы обратно в текст
filtered_df["phrases_text"] = filtered_df["phrases"].apply(lambda words: " ".join(words))

# рейтинг релевантности текстов
def war_filter(row):
    text = row['phrases_text'] if pd.notna(row['phrases_text']) else ""

    # High-weight war phrases with additional bigrams
    war_keywords = {
            'специальный_военный': 5,
            'качество_доброволец': 5,
            'зона_специальный': 5,
            'зона_сво': 5,
            'спецоперация': 5,
            r'сво[\s]': 5,
            'военный_операция': 5,
            'прохождение_служба': 4.9,
            r'помиловать[\s]': 4.85,
            'участник_боевой': 4.7,
            'получать_ранение': 4.6,
            'контракт_принимать': 4.5,
            'вагнер': 4.4,
            'прохождение_военный': 4.3,
            'зона_проведение': 4.2,
            'проходить_служба': 4.1,
            r'режим[\s]': 4,
            'зона_боевой': 3.9,
            'выполнение_боевой': 3.8,
            'награда_медаль': 3.7,
            'ведомственный_награда': 3.6,
            'награда_чвк': 3.5,
            'территория_лнр': 3.4,
            'наградить_государственный': 3.3,
            'период_мобилизация': 3.2,
            'указ_президент': 3.1,
            'месячный_контракт': 3,
            'медаль_за': 2.9,
            'территория_украина': 2.8,
            'украина': 2.7,
            'принимать_участие': 2.6,
            'боевой_действие': 2.5,
            'днр': 2.4,
            'горячий_точка': 2.3,
            'чвк_вагнер': 2.2,
            'министерство_оборона': 2.1,
            r'лнр[\s]': 2,
            'республика_украина': 1.9,
            'территория_днр': 1.8,
            'являться_ветеран': 1.7,
            'вооруженный_сила': 1.6,
            'смягчать_наказание': 1.5,
            'обстоятельство_смягчать': 1.4,
            'заключать_договор': 1.3,
            'государственный_награда': 1.2,
            'мобилизация': 1.1,
            'повестка': 1,
            'подписать_контракт': 0.9,
            'заключать_контракт': 0.8,
            'являться_военнослужащий': 0.7,
            'наличие_смягчать': 0.6,
            'обстоятельство_смягчающий': 0.55,
            'ветеран_боевой': 0.5
    }

    # Initialize score
    score = 0.0

    # Check for phrases
    for pattern, weight in war_keywords.items():
        if re.search(pattern, text):
            score += weight

    # Return classification based on adjusted threshold
    return score

filtered_df['war_related'] = filtered_df.apply(war_filter, axis=1)

# сохраняем нужные данные для выгрузки в файл
save_df = filtered_df[['id', 'text', 'link_text', 'norm_text', 'war_related']]
save_df = save_df.loc[save_df['war_related'] > 0]
# save_df.to_excel('./SVO_rated.xlsx')

print("Переходим к TF-IDF анализу...")

# save_df = save_df.drop('Unnamed: 0', axis=1)

# тот же словарь, но в удобном формате для TF-IDF анализа
veteran_keywords = [
        'специальный военный',
        'военный операция',
        'зона сво',
        'зона проведение',
        'спецоперация',
        'зона специальный',
        'зона боевой',
        'сво',
        'государственный награда',
        'ведомственный награда',
        'награда медаль',
        'награда чвк',
        'наградить государственный',
        'чвк вагнер',
        'днр',
        'лнр',
        'украина',
        'вагнер',
        'территория днр',
        'территория лнр',
        'территория украина',
        'республика украина',
        'прохождение служба',
        'проходить служба',
        'прохождение военный',
        'мобилизация',
        'указ президент',
        'качество доброволец',
        'боевой действие',
        'выполнение боевой',
        'являться ветеран',
        'участник боевой',
        'принимать участие',
        'помиловать',
        'повестка',
        'министерство оборона',
        'режим',
        'заключать контракт',
        'подписать контракт',
        'контракт принимать',
        'месячный контракт',
        'являться военнослужащий',
        'ветеран боевой',
        'смягчать наказание',
        'наличие смягчать',
        'обстоятельство смягчать',
        'обстоятельство смягчающий',
        'медаль за',
        'горячий точка',
        'заключать договор',
        'получать ранение'
]

# TF-IDF анализ каждого текста на релевантность слов из словаря
russian_stopwords = stopwords.words("russian")
texts = save_df.norm_text.to_list()

vectorizer = TfidfVectorizer(stop_words=russian_stopwords, vocabulary=veteran_keywords, use_idf=True, ngram_range=(1,3), token_pattern=r'\S+')
X = vectorizer.fit_transform(save_df['norm_text'])
df_tfidf = pd.DataFrame(X.toarray(), 
                        columns=vectorizer.get_feature_names_out(), 
                        index=save_df.index)

# соединяем посчитанные векторы нужных нам слов и изначальную базу
combined_df = pd.concat([save_df[['id', 'war_related']], df_tfidf], axis=1)
# считаем общее количество "очков" для каждого текста (насколько близок текст к словарю)
combined_df['score'] = combined_df[veteran_keywords].sum(axis=1)

# добавляем столбец score к датасету
save_df = pd.merge(save_df, combined_df[['id', 'score']], how='left', on='id')

df = df[df.id.isin(save_df.id)]
save_df = pd.merge(df, save_df[['id', 'war_related', 'score']], how='left', on='id')
save_df.to_excel("./SVO_rated.xlsx")
print("Файл сохранен в той же папке, что и этот код, называется SVO_rated.xlsx. В конце файла добавлены два столбца: war_related и score — это рейтинги релевантности текстов от меня и от машины :)")