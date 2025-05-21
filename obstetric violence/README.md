# Анализ данных для текста "ТКТКТК" — от 10/2016 до 10/2024 (English version below)

Этот репозиторий содержит данные, код и результаты, которые подтверждают части текста [TKTKTKTK](https://support.semnasem.org/), опубликованного ДД/ММ/ГГГГ. Пожалуйста, прочитайте сам текст, содержащий важный контекст и подробности, прежде чем продолжить.

## Данные

В данном анализе используются данные группы ВК "Насилие в родах" и тексты судебных приговоров по акушерскому насилию.

Данные получены из следующих источников:

- Агрегатор судебных дел ГАС РФ [Правосудие] (https://sudrf.ru/):
  - тексты приговоров скачены с помощью [парсера] Если быть Точным (https://github.com/tochno-st/sudrfscraper) по статьям УК РФ 109, 118, 124, 238, 293 
  - данные охватывают период от 05/09/2019 до 20/06/2024
- посты группы Вконтакте ["Насилие в родах"] (https://vk.com/humanize_birth):
  - посты скачены с помощью [VK API] (https://dev.vk.com/ru/api/access-token/getting-started#%D0%9A%D0%BB%D1%8E%D1%87%20%D0%B4%D0%BE%D1%81%D1%82%D1%83%D0%BF%D0%B0%20%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8F) 
  - данные охватывают период от 21/10/2016 до 02/10/2024


Итоговые файлы содержат, помимо прочего, следующие столбцы, имеющие отношение к анализу:

- `detailed_data_VK.csv` - посты из группы ВК "Насилие в родах"
  - `text` - оригинальный текст поста
  - `hashtags` - хэштеги, упомянутые в постах или вручную добавленные при проверке данных
  - `violence_type` - тип акушерского насилия (определяется по хэштегам)
  - `clean_text` - очищенный текст поста
  - `lemmas` - леммы, полученные из очищенного текста поста
  - `emotion_shares` - эмоции и доли эмоций от всех значимых слов в посте
  - `total_emotion_shares` - общая доля эмоций в посте
- `childbirth_all_articles.csv` - тексты приговоров по пяти вышеупомянутым статьям УК РФ
  - `no. of suspects` - количество подсудимых
  - `yearDate` - год вынесения приговора
  - `resultDate` - полная дата вынесения приговора
  - `decision` - решение суда
  - `cui` - уникальный индекс дела, чтобы вычислить дубли
  - `link_text` - ссылка на текст приговора
  - `relevant` - описывает ли дело насилие при родах (yes/no/-)
  - `mother killed` - умерла ли роженица
  - `child killed` - умер ли новорожденный
  - `sentence years` - количество лет ограничения свободы
  - `drop reason` - причина отмены наказания или прекращения дела
  - `commentary` - комментарий при ручной проверке данных


## Методология

Рабочая тетрадь [`sentiment analysis.ipynb`](notebook/tktktk.ipynb) производит следующий анализ:

##### Часть 1: Скачивание постов с помощью VK API

##### Часть 2: Составление словаря эмоций и подсчёт эмоций в постах

## Данные на выходе

Рабочая тетрадь выводит датасет, содержащий анализ эмоций в постах "Насилие в родах": [`detailed_data_VK.csv`](output/tktktk.csv).

## Репликация анализа

Вы можете повторить анализ самостоятельно. Для этого на вашем компьютере должно быть установлено следующее:

- Python 3
- Библиотеки Python, указанные в [`sentiment analysis.ipynb`](notebook/tktktk.ipynb)

## Лицензия

Весь код в этом репозитории доступен под лицензией [MIT License](https://opensource.org/licenses/MIT). Файл данных в папке output/ доступен по лицензии [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) (CC BY 4.0). Все файлы в папке data/ являются общественным достоянием.

## Отзывы / Вопросы?

Напишите Янине Сорокиной по адресу yanina.sorokina@protonmail.com

# Analysis of Obstetric violence data set — 10/2016 to 10/2024

This repository contains data, analytic code, and findings that support portions of the article, “[TKTKTKTK](https://support.semnasem.org/),” published Month Date, Year. Please read that article, which contains important context and details, before proceeding.

## Data

This analysis uses TKTKTK spreadsheets.

The spreadsheets come from the following sources:

- Court case aggregator GAS RF [“Justice”] (https://sudrf.ru/):
  - texts of sentences downloaded with the help of [parser To be Accurate] (https://github.com/tochno-st/sudrfscraper) for articles of the Criminal Code of the Russian Federation 109, 118, 124, 238, 293
  - data covers the period from 05/09/2019 to 20/06/2024
- posts of the Vkontakte group [“Violence in childbirth”] (https://vk.com/humanize_birth):
  - posts were parsed using [VK API] (https://dev.vk.com/ru/api/access-token/getting-started#%D0%9A%D0%BB%D1%8E%D1%87%20%D0%B4%D0%BE%D1%81%D1%82%D1%83%D0%BF%D0%B0%20%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8F)
  - data covers the period from 21/10/2016 to 02/10/2024

Each of the spreadsheets contains, among others, the following columns relevant to the analysis:

- `detailed_data_VK.csv` - posts from the VK group “Violence in childbirth”
  - `text` - original text of the post
  - `hashtags` - hashtags mentioned in the posts or manually added when checking the data
  - `violence_type` - type of obstetric violence (determined by hashtags)
  - `clean_text` - cleaned text of the post
  - `lemmas` - lemmas derived from the cleaned text of the post
  - `emotion_shares` - emotions and emotion shares from all relevant words in the post
  - `total_emotion_shares` - total share of emotions in the post
- `childbirth_all_articles.csv` - texts of sentences under the five above-mentioned articles of the Criminal Code of the Russian Federation
  - `no. of suspects` - number of defendants
  - `yearDate` - year of sentencing
  - `resultDate` - full date of sentencing
  - `decision` - court decision
  - `cui` - unique case index to calculate duplicates
  - `link_text` - link to the text of the sentence
  - `relevant` - whether the case describes violence in childbirth (yes/no/-)
  - `mother killed` - whether the woman in labor died.
  - `child killed` - whether the newborn baby died
  - `sentence years` - number of years of confinement
  - `drop reason` - reason for dropping a sentence or dropping a case
  - `commentary` - commentary during manual data check

## Methodology

The notebook [`sentiment analysis.ipynb`](notebook/tktktk.ipynb) performs the following analyses:

##### Part 1: Parsing posts using the VK API

##### Part 2: Creating an Emotion Dictionary and Counting Emotions in Posts


## Outputs

The notebooks output this spreadsheet which contains analysis of emotions in the post “Violence in childbirth”: [`detailed_data_VK.csv`](output/tktktktk.csv).

## Running the analysis yourself

You can run the analysis yourself. To do so, you'll need the following installed on your computer:

- Python 3
- The Python libraries specified in [`sentiment analysis.ipynb`](notebook/tktktk.ipynb)

## Licensing

All code in this repository is available under the [MIT License](https://opensource.org/licenses/MIT). The data file in the output/ directory is available under the [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) (CC BY 4.0) license. All files in the data/ directory are released into the public domain.

## Feedback / Questions?

Contact Yanina Sorokina at yanina.sorokina@protonmail.com
