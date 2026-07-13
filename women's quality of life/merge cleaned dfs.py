import pandas as pd
import matplotlib as plt
import re

# удаляем "запрещённые знаки" из текстов заседаний
def remove_illegal_characters(value):
    if isinstance(value, str):
        # This regex matches characters in the ranges:
        # \x00 - \x08, \x0B, \x0C, and \x0E - \x1F
        return re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', value)
    return value
# выделяем подсет данных для более быстрой обработки
def prepare_data(df):    
    new_df = df[['id', 'text', 'link_meta']]
    new_df = df.drop_duplicates(subset='link_meta')
    # удаляем строки, где текст заседаний длиннее одного символа
    new_df = new_df[new_df['text'].str.len() > 1]
    print(f"Статья {article}: Из {len(df)} строк осталось {len(new_df)}, {round(len(new_df)/len(df)*100, 2)}% от оригинала")
    # приводим тексты заседаний в прописные буквы, удаляем все не-буквы
    new_df['text'] = new_df['text'].str.lower()
    new_df['text'] = new_df['text'].str.replace(r'[^а-яА-ЯёЁ\s]', ' ', regex=True)
    new_df['text'] = new_df['text'].str.replace(r'\s+', ' ', regex=True)
    
    return new_df
# создаём предварительный фильтр, чтобы отобрать дела, в которых упоминается война
rough_words = [
            r'\bакушер',
            r'\bгинеколог',
            r"\bродовспоможение\b",
            r"\bплод\b",
            r"\bкесарево\b",
            r"\bперинатальный\s+центр\b",
            r"беременн",
            r"родоразрешение",
            r"акушер-гинеколог",
            # r'\bрод[ы]',
            # r'\bроддом',
            # r"\bокситоцин\b",
            # r"\bроженица\b",
            # r"\bвыдавл[ивание]\b",
            # r"\bразрыв\s+промежности\b",
            # r"\bпрокол\s+пузыря\b",
            # r"\bвакуум[\s-]?экстракц[иы][яе]?\b",  # вакуум экстракция, вакуум-экстракция
            # r"\bвакуум[еэ]кст[ра]ктор\b",         # вакуумэкстрактор
            # r"\bвакуум[еэ]ктракц[иы][яе]?\b",      # вакуумэктракция
            # r"\bметод\s+кристеллера\b",
            # r"\bдавил[и]\s+на\s+живот\b",
            # r"\bбинт\s+вербова\b"#
]

rough_pattern = re.compile('|'.join(rough_words), re.IGNORECASE)

# функция, которая проверяет тексты приговоров по ключевым словам
def is_relevant(text):
    if text is None:  # Check if tokens is None
        return "!"
    return 'yes' if rough_pattern.search(text) else None

path = '/Users/Helen/Downloads/macOS-x64.sudrfscraper/results'
articles = ['118', '238', '293', '124', '109']

step_one = pd.DataFrame()

# pd.read_csv(f'{path}/109/109.csv', sep=';')
for article in articles:
    df = pd.read_csv(f'{path}/{article}/{article}.csv', sep=';')
    df['text'] = df['text'].astype('string')
    df['entryDate'] = pd.to_datetime(df['entryDate'], errors='coerce')
    print(f"{article}: первое дело поступило в суд {df['entryDate'].min()}")
    print(f"{article}: последнее дело поступило в суд {df['entryDate'].max()}")
    df = df.applymap(remove_illegal_characters)
    new_df = prepare_data(df)
    new_df['pre_relevant'] = new_df['text'].apply(is_relevant)
    childbirth = new_df.loc[new_df['pre_relevant'] == 'yes']
    mf = df[df.id.isin(childbirth.id)]
    step_two = pd.concat([step_one, mf], ignore_index=True)

final = step_two.drop_duplicates(subset='link_meta')
print(f"Из {len(step_two)} строк осталось {len(final)}, {round(len(final)/len(step_two)*100, 2)}% от базы из {len(articles)} статей")
print(f"Из {len(step_two)} строк осталось {len(final)}, {round(len(final)/len(step_two)*100, 2)}% от базы из {len(articles)} статей")
final.to_csv(f'../output/childbirth_all_articles.csv', sep=';', index=False)
print("Файл сохранён :)")

# a = len(new_df.loc[new_df['pre_relevant'] == 'yes', ['id']])
# b = len(df.loc[df['text'].str.len() > 1, ['id']])
# print(f"Всего нашлось {a} релевантных приговоров из {b} подходящих дел.")