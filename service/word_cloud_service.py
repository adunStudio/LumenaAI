from nltk.corpus import stopwords

from konlpy.tag import Okt
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

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
        wordcloud = WordCloud(width=800, height=400, font_path=WordCloudService.FONT_PATH, background_color='white').generate_from_frequencies(word_freq)

        return wordcloud
