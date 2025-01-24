# LumenaAI

```
LemanaAI/
│
├── app/
│   ├── main.py                 # Streamlit 앱의 진입점 (앱 실행 파일)
│   └── pages/
│       ├── __init__.py         # 패키지 초기화 파일
│       ├── page1.py            # 첫 번째 페이지
│       ├── page2.py            # 두 번째 페이지
│       └── page3.py            # 세 번째 페이지
│
├── domain/
│   ├── __init__.py             # 패키지 초기화 파일
│   ├── entitiy/
│   │   └── __init__.py         # 엔티티 초기화 파일
│   │   
│   └─── value_object/
│       └── __init__.py         # 값 객체 초기화 파일
│
├── service/
│   ├── __init__.py             # 서비스 초기화 파일
│   ├── youtube_service.py      # YouTube 관련 비즈니스 로직
│   └── user_service.py         # User 관련 비즈니스 로직
│
├── infrastructure/
│   ├── __init__.py             # 패키지 초기화 파일
│   ├── repository/
│   │   ├── __init__.py           # 저장소 초기화 파일
│   │   ├── youtube_repository.py # YouTubeContent 저장소 구현
│   │   └── user_repository.py    # User 저장소 구현
│   └── database/
│       ├── __init__.py         # 데이터베이스 초기화 파일
│       ├── mongo_client.py     # MongoDB 클라이언트 설정
│       └── config.py           # 데이터베이스 설정 및 연결 정보
│
├── tests/                      # 테스트 파일
│
├── assets/
│   └── images/                 # 이미지 파일
│
├── .streamlit/
│   ├── config.toml             # Streamlit 설정 파일
│   └── secrets.toml            # 비공개 설정 파일 
│
├── requirements.txt            # 필요한 Python 패키지 리스트
└── README.md                   # 프로젝트 설명 파일
```