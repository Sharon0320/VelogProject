# Velog AI 블로그 생성기 - Backend

## 개요
PDF 파일을 분석하여 AI가 기술블로그를 자동으로 생성하고 Velog에 포스팅하는 백엔드 서비스입니다.

## 주요 기능
- PDF 텍스트 추출 및 대화 형식 파싱
- 이미지 추출 및 위치 정보 수집
- Upstage OCR을 통한 이미지 분석
- Perplexity Solar Pro 2를 통한 블로그 생성
- Velog 자동 포스팅

## 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정
`.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# Perplexity API 설정
PPLX_API_KEY=your_perplexity_api_key_here
PPLX_API_URL=https://api.perplexity.ai/chat/completions

# Velog API 설정
VELO_API_URL=https://v2.velog.io/graphql

# Upstage OCR API 설정
UPSTAGE_OCR_API_KEY=your_upstage_ocr_api_key_here
UPSTAGE_OCR_API_URL=https://api.upstage.ai/v1/vision/ocr
```

### 3. 시스템 의존성
PDF 처리 및 이미지 처리를 위해 다음 패키지가 필요합니다:
- poppler-utils
- tesseract-ocr
- OpenCV 관련 라이브러리

## 실행 방법

### 개발 환경
```bash
python Velog.py
```

### Docker
```bash
docker build -t velog-backend .
docker run -p 5000:5000 velog-backend
```

## API 엔드포인트

### POST /post
PDF 파일을 업로드하여 블로그를 생성하고 Velog에 포스팅합니다.

**요청 형식:**
- `pdf_file`: PDF 파일 (multipart/form-data)
- `velog_cookie`: Velog 인증 쿠키

**응답 형식:**
```json
{
  "success": true,
  "title": "생성된 제목",
  "summary": "생성된 요약",
  "body": "생성된 본문",
  "tags": ["태그1", "태그2"],
  "velogResponse": {...},
  "message": "성공 메시지"
}
```

### GET /health
서비스 상태 확인

## 파일 구조
```
BackEnd/
├── Velog.py          # 메인 애플리케이션
├── requirements.txt  # Python 의존성
├── Dockerfile       # Docker 설정
├── uploads/         # 임시 파일 저장소
└── README.md        # 이 파일
```

## 주의사항
- 업로드된 파일은 처리 후 자동으로 삭제됩니다
- PDF 파일 크기는 최대 10MB로 제한됩니다
- 이미지 처리를 위해 충분한 메모리가 필요합니다


