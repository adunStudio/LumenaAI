from nltk.corpus import stopwords
import nltk
from konlpy.tag import Okt
from collections import Counter
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from summa import keywords
from rake_nltk import Rake

class WordCloudService:
    FONT_PATH = 'asset/NanumGothic-Regular.ttf'

    def __init__(self):
        self._english_stop_words = set(stopwords.words('english'))  # 영어 불용어
        self._korean_stop_words  = self._load_korean_stopwords()  # 한국어 불용어

    def _load_korean_stopwords(self):
        okt = Okt()
        stop_words = set([
            '을', '를', '에', '가', '은', '는', '의', '도', '으로', '과', '와', '한', '하다', '있다', '없다',
            '저', '그', '수', '다', '로', '로서', '에서', '한테', '때문', '것', '들', '가장', '위해', '이', '있음',
            '수', '또한'
        ])
        return stop_words

    def generate_frequency_wordcloud(self, text):
        """ 빈도수 기반으로 워드 클라우드를 생성하는 함수 """
        # 텍스트를 소문자로 변환하고, 공백을 기준으로 단어를 나눔
        words = text.lower().split()

        # 불용어 제거 (영어와 한국어 불용어 적용)
        filtered_words = [word for word in words if word not in self._english_stop_words and word not in self._korean_stop_words]

        # 단어 빈도수 계산
        word_freq = Counter(filtered_words)

        # 워드 클라우드 생성
        return WordCloud(width=800, height=400, font_path=WordCloudService.FONT_PATH, background_color='white').generate_from_frequencies(word_freq)

    def generate_tfidf_wordcloud(self, text):
        """ TF-IDF 방식으로 워드 클라우드를 생성하는 함수 """
        # 불용어 처리
        stop_words_combined = list(self._english_stop_words.union(self._korean_stop_words))
        tfidf_vectorizer = TfidfVectorizer(stop_words=stop_words_combined)
        X = tfidf_vectorizer.fit_transform([text])

        # 단어와 그에 대한 TF-IDF 값을 가져오기
        tfidf_scores = np.array(X.sum(axis=0)).flatten()
        words = tfidf_vectorizer.get_feature_names_out()

        # 단어와 TF-IDF 점수를 딕셔너리로 저장
        word_scores = {words[i]: tfidf_scores[i] for i in range(len(words))}

        # 워드 클라우드 생성
        return WordCloud(width=800, height=400, font_path=WordCloudService.FONT_PATH, background_color='white').generate_from_frequencies(word_scores)

    def _filter_stopwords(self, text):
        """ 텍스트에서 불용어를 제거하는 함수 """
        words = text.split()
        return ' '.join(
            [word for word in words if word not in self._english_stop_words and word not in self._korean_stop_words])

    def generate_textrank_wordcloud(self, text):
        """ TextRank 방식으로 워드 클라우드를 생성하는 함수 """
        # 불용어 제거
        filtered_text = self._filter_stopwords(text)

        # TextRank 알고리즘으로 키워드 추출
        ranked_keywords = keywords.keywords(filtered_text, words=10, split=True)

        # 단어와 중요도를 워드 클라우드에 전달할 형식으로 변환
        word_scores = {word: 1 for word in ranked_keywords}

        # 워드 클라우드 생성
        return WordCloud(width=800, height=400, font_path=WordCloudService.FONT_PATH, background_color='white').generate_from_frequencies(word_scores)

    def generate_rake_wordcloud(self, text):
        """ RAKE 방식으로 워드 클라우드를 생성하는 함수 """
        # 불용어 제거
        filtered_text = self._filter_stopwords(text)

        # RAKE 알고리즘으로 키워드 추출
        rake = Rake()
        rake.extract_keywords_from_text(filtered_text)
        keyword_scores = rake.get_ranked_phrases_with_scores()

        # 키워드 점수와 함께 워드 클라우드에 전달할 형식으로 변환
        word_scores = {item[1]: item[0] for item in keyword_scores}

        # 워드 클라우드 생성
        return WordCloud(width=800, height=400, font_path=WordCloudService.FONT_PATH, background_color='white').generate_from_frequencies(word_scores)


