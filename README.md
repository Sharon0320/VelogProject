# ✨ Velog AI 블로그 생성기

대화 내용을 PDF로 업로드하면 백엔드가 텍스트를 추출하고, LLM이 기술 블로그 글(제목/요약/본문/태그)을 생성해 Velog에 자동 포스팅하는 도구입니다.

## 🚀 주요 기능

- **PDF 업로드**: 대화 내용 PDF 파일 업로드
- **AI 분석**: Upstage Document Parse로 텍스트 추출, Solar Pro 2로 콘텐츠 생성
- **자동 블로그 생성**: 제목, 요약, 본문, 태그 자동 생성
- **Velog 연동**: 생성된 블로그를 Velog에 자동 포스팅

## 🏗️ 아키텍처

```
Frontend (Next.js) ←→ Backend (Flask) ←→ External APIs
     ↓                      ↓
  PDF Upload         PDF Processing
  UI Components      Image Extraction
  Progress Display   OCR Analysis
                     AI Blog Generation
                     Velog Posting
```

## 🛠️ 기술 스택

### Frontend
- **Next.js 15** + **React 18** + **TypeScript**
- **Tailwind CSS** + **shadcn/ui** 컴포넌트
- **Radix UI** (접근성 고려)

### Backend
- **Flask 3** (Python)
- **Upstage Document AI (document-parse)** for 텍스트 추출
- **Upstage Solar Pro 2** for LLM 생성

### AI
- **Upstage Solar Pro 2** (블로그 생성)
- **Upstage Document Parse** (텍스트 추출)

### Infrastructure
- **Docker** + **Docker Compose**
- **Nginx** (프론트엔드 서빙)

## 📦 설치 및 실행

### 1. 저장소 클론
```bash
git clone <repository-url>
cd VelogProject
```

### 2. 환경변수 설정
```bash
# BackEnd/.env 생성 후 아래 값 설정
UPSTAGE_API_KEY=your_upstage_api_key
VELO_API_URL=https://v2.velog.io/graphql
```

### 3. Docker로 실행
```bash
docker-compose up --build
```

### 4. 브라우저에서 접속
- Frontend: http://localhost:3000
- Backend: http://localhost:5000

## 🔧 개발 환경 설정

### Backend 개발
```bash
cd BackEnd
pip install -r requirements.txt
# 두 방법 중 하나로 실행
python Velog.py          # 진입점 (내부에서 VelogApp 실행)
# 또는
python velog_app.py      # 직접 VelogApp 실행
```

### Frontend 개발
```bash
cd FrontEnd
npm install
npm run dev
```

## 📋 사용 방법

### 1. Velog 쿠키 설정
- Velog에 로그인
- F12 → Application → Cookies → 복사
- 쿠키 입력란에 붙여넣기

### 2. PDF 업로드
- OpenAI/Perplexity 대화 내용을 PDF로 추출
- PDF 파일 업로드 (최대 10MB)

### 3. AI 분석 및 생성
- PDF 텍스트 추출 (Upstage Document Parse)
- AI 블로그 생성 (Upstage Solar Pro 2)
- Velog 자동 포스팅

## 🔍 API 엔드포인트

### Backend
- `POST /post`: PDF 업로드 및 블로그 생성/포스팅

### Frontend
- `POST /api/generate-blog`: PDF 처리 요청

## 📁 프로젝트 구조

```
VelogProject/
├── FrontEnd/                 # Next.js 프론트엔드
│   ├── app/                 # App Router
│   ├── components/          # UI 컴포넌트
│   ├── hooks/              # 커스텀 훅
│   └── public/             # 정적 파일
├── BackEnd/                 # Flask 백엔드
│   ├── Velog.py            # 진입점 (VelogApp 실행)
│   ├── velog_app.py        # 메인 애플리케이션 클래스(Flask 라우팅)
│   ├── pdf_processor.py    # PDF 텍스트 추출 (Upstage Document Parse)
│   ├── blog_content_generator.py # LLM 콘텐츠 생성 (Solar Pro 2)
│   ├── velog_api.py        # Velog 포스팅 모듈
│   ├── requirements.txt    # Python 의존성
│   ├── Dockerfile          # Docker 설정
│   └── uploads/            # 임시 파일 저장소
├── docker-compose.yml       # Docker Compose 설정
└── README.md               # 이 파일
```

## 🚨 주의사항

- **파일 크기**: PDF 최대 10MB
- **파일 형식**: PDF만 지원
- **보안**: 업로드된 파일은 처리 후 자동 삭제
- **API 키**: Upstage API 키 필요
- **Velog 인증**: 유효한 쿠키 필요

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요.

---

**Made with ❤️ for developers who love blogging**



