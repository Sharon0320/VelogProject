# ✨ Velog AI 블로그 생성기

OpenAI나 Perplexity에서 대화한 내용을 PDF로 추출하여 AI가 분석하고, 이미지와 함께 기술블로그를 자동으로 생성하여 Velog에 포스팅하는 도구입니다.

## 🚀 주요 기능

- **PDF 업로드**: OpenAI/Perplexity 대화 내용 PDF 파일 업로드
- **AI 분석**: Perplexity Solar Pro 2를 통한 대화 내용 분석
- **이미지 처리**: PDF에서 이미지 추출 및 Upstage OCR 분석
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
- **Flask 3.0.3** (Python)
- **PyPDF2** + **pdfplumber** (PDF 처리)
- **OpenCV** + **Pillow** (이미지 처리)
- **pdf2image** (PDF → 이미지 변환)

### AI & OCR
- **Perplexity Solar Pro 2** (블로그 생성)
- **Upstage OCR** (이미지 텍스트 분석)

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
# BackEnd/.env 파일 생성
cp BackEnd/.env.example BackEnd/.env

# 필요한 API 키 설정
PPLX_API_KEY=your_perplexity_api_key
UPSTAGE_OCR_API_KEY=your_upstage_ocr_api_key
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
python Velog.py
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
- PDF 텍스트 추출
- 이미지 분석 및 OCR
- AI 블로그 생성
- Velog 자동 포스팅

## 🔍 API 엔드포인트

### Backend
- `POST /post`: PDF 업로드 및 블로그 생성
- `GET /health`: 서비스 상태 확인

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
│   ├── Velog.py            # 메인 애플리케이션
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
- **API 키**: Perplexity, Upstage OCR API 키 필요
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



