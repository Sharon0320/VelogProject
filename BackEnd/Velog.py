import os
import re
import tempfile
import requests
import base64
from io import BytesIO

# Import for image size check
from PIL import Image
import fitz
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

# --- 환경 변수 및 클라이언트 초기화 ---
load_dotenv()

VELO_API_URL = os.getenv("VELO_API_URL")
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")

# Flask 앱 초기화
app = Flask(__name__)

# Upstage LLM을 위한 OpenAI 클라이언트 초기화 (base_url 수정)
upstage_client = OpenAI(
    api_key=UPSTAGE_API_KEY,
    base_url="https://api.upstage.ai/v1/"  # base_url에 슬래시 추가
)


# --- 유틸리티 함수 ---

def remove_references(text):
    """[숫자] 형태의 참조(reference) 제거"""
    return re.sub(r'\[\d+\]', '', text)


def upload_image_to_imgbb(image_bytes):
    """imgbb API를 사용해 이미지를 업로드하고 URL을 반환하는 함수"""
    url = "https://api.imgbb.com/1/upload"

    if not IMGBB_API_KEY:
        print("IMGBB_API_KEY가 .env 파일에 설정되지 않았습니다.")
        return None

    # 이미지를 base64로 인코딩
    encoded_image = base64.b64encode(image_bytes)

    payload = {
        "key": IMGBB_API_KEY,
        "image": encoded_image
    }

    try:
        response = requests.post(url, data=payload)
        response_data = response.json()

        if response.status_code == 200 and response_data.get("success"):
            image_url = response_data["data"]["url"]
            print(f"imgbb upload success: {image_url}")
            return image_url
        else:
            print(f"imgbb 업로드 실패: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"imgbb 업로드 중 예외 발생: {e}")
        return None


def extract_text_from_image_upstage(image_bytes):
    """
    Upstage Document OCR API를 사용해 이미지에서 텍스트를 추출하는 함수
    """
    url = "https://api.upstage.ai/v1/document-digitization"
    headers = {'Authorization': f'Bearer {UPSTAGE_API_KEY}'}
    # 파일을 multipart/form-data 형식으로 전송
    files = {"document": ("image.jpg", image_bytes, "image/jpeg")}
    data = {"model": "ocr"}
    response = requests.post(url, headers=headers, files=files, data=data)

    if response.status_code == 200:
        text = response.json().get("text", "")
        print("OCR 성공")
        return text.strip()
    else:
        print(f"OCR 실패: {response.status_code} - {response.text}")
        return f"OCR 실패: {response.status_code}"


def process_pdf(pdf_path):
    """
    PDF 파일에서 텍스트와 이미지를 추출하고, 이미지는 OCR 및 업로드를 수행하는 함수
    (작은 이미지 필터링 기능 추가)
    """
    doc = fitz.open(pdf_path)
    full_content = ""
    image_details = {}
    image_counter = 1

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        full_content += page.get_text("text") + "\n\n"

        # 페이지의 너비와 높이 가져오기
        page_width = page.rect.width
        page_height = page.rect.height

        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            # 이미지 크기 필터링: 가로/세로 100px 미만 또는 페이지 너비의 10% 미만 이미지는 무시
            try:
                from PIL import Image
                from io import BytesIO
                img_io = BytesIO(image_bytes)
                image_obj = Image.open(img_io)
                width, height = image_obj.size

                # 페이지 너비의 10%를 기준으로 필터링
                min_size_threshold = max(100, page_width * 0.1)

                if width < min_size_threshold or height < min_size_threshold:
                    print(f"이미지 {page_num + 1}-{img_index + 1}는 크기가 작아 (W:{width}, H:{height}) 건너뜁니다.")
                    continue
            except Exception as e:
                print(f"이미지 크기 확인 중 오류 발생: {e}")
                # 오류 발생 시 일단 통과시켜 OCR/업로드 진행

            ocr_text = extract_text_from_image_upstage(image_bytes)
            image_url = upload_image_to_imgbb(image_bytes)

            if image_url:
                placeholder = f"\n--- 이미지 {image_counter} 시작 ---\n[설명: {ocr_text}]\n--- 이미지 {image_counter} 끝 ---\n"
                full_content += placeholder
                alt_text = ocr_text.splitlines()[0] if ocr_text else f'Image {image_counter}'
                image_details[f"[IMAGE_{image_counter}]"] = f"![{alt_text}]({image_url})"
                image_counter += 1

    return full_content, image_details


# --- 핵심 로직: 블로그 생성 및 포스팅 ---

def get_summary_title_body_tags(processed_text):
    """
    Upstage Solar API를 사용해 블로그 콘텐츠를 생성하는 함수
    (안정적인 파싱 로직 적용)
    """
    prompt = f"""
당신은 PDF 문서 분석 능력이 뛰어난 기술 블로그 전문가입니다. 아래의 원본 텍스트를 분석하여, 독자들이 이해하기 쉬운 전문가 수준의 기술 블로그 포스트를 작성해주세요. 원본 텍스트에는 이미지의 OCR 결과가 '--- 이미지 N 시작/끝 ---' 형태로 포함되어 있습니다.
아래 각 항목의 지시에 따라 정확하게 결과물을 생성해주세요. 각 항목은 반드시 한 줄로 시작해야 합니다.

제목:,요약:,본문:,태그: 앞에는 마크다운 ### 붙이지 말아줘.
그리고 제목 요약 본문 태그를 시작할 때는 꼭 제목: 요약: 본문: 태그: 처럼 :를 꼭 붙여줘.
본문 첫줄에는 어떤 내용들을 있는지 목차를 작성해줘.

제목: SEO를 고려하여 사람들의 흥미를 끌 만한 기술 블로그 제목을 추천해줘.
요약: 전체 내용을 대표할 수 있는 핵심 내용 3문장으로 요약해줘.
본문: 원본 텍스트와 이미지 OCR 결과를 바탕으로, 교수님께 칭찬받을 만한 상세하고 깊이 있는 기술 블로그 본문을 작성해줘. 문제 해결 과정을 다루는 트러블슈팅 형식이라면 더욱 좋아. 특히, 내용의 흐름에 맞게 이미지가 들어갈 가장 적절한 위치에 '[IMAGE_1]', '[IMAGE_2]'와 같은 플레이스홀더를 반드시 삽입해줘.
태그: 이 글의 핵심 키워드를 쉼표(,)로 구분된 태그로 만들어줘.

[원본 텍스트]
{processed_text}
"""
    try:
        response = upstage_client.chat.completions.create(
            model="solar-pro2",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=4096
        )
        result = response.choices[0].message.content
        print("Upstage Solar 응답 원문:\n", result)

    except Exception as e:
        print(f"Upstage Solar API 오류: {e}")
        raise Exception(f"Upstage Solar API 오류: {e}")

    # 멀티라인 본문 파싱 (안정적인 로직)
    title, summary, full_body, tags_line = "제목없음", "요약없음", "", ""
    lines = result.split('\n')
    in_body = False

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue

        # '제목:' 키워드를 포함하는 줄을 찾음
        title_match = re.search(r'제목:', stripped_line)
        if title_match:
            title = stripped_line[title_match.end():].strip()
            in_body = False
            continue

        # '요약:' 키워드를 포함하는 줄을 찾음
        summary_match = re.search(r'요약:', stripped_line)
        if summary_match:
            summary = stripped_line[summary_match.end():].strip()
            in_body = False
            continue

        # '본문:' 키워드를 포함하는 줄을 찾음
        body_match = re.search(r'본문:', stripped_line)
        if body_match:
            in_body = True
            full_body = stripped_line[body_match.end():].strip()
            continue

        # '태그:' 키워드를 포함하는 줄을 찾음
        tags_match = re.search(r'태그:', stripped_line)
        if tags_match:
            tags_line = stripped_line[tags_match.end():].strip()
            in_body = False
            continue

        # '본문' 섹션 내부에 있는 줄들을 추가
        if in_body:
            full_body += "\n" + stripped_line

    # reference 제거
    full_body = remove_references(full_body)
    tags = [tag.strip() for tag in tags_line.split(",") if tag.strip()]

    # 결과가 비어있는 경우 기본값 설정
    if not title:
        title = "제목없음"
    if not summary:
        summary = "요약없음"
    if not full_body:
        full_body = "내용없음"

    # 디버깅을 위한 파싱 결과 출력
    print(f"파싱 결과: 제목='{title}', 요약='{summary}', 태그='{tags}', 본문 첫 100자='{full_body[:100]}...'")

    return title, summary, full_body, tags


def post_to_velog(title, body, tags, summary, velog_cookie):
    """
    생성된 콘텐츠를 Velog에 포스팅하는 함수
    """
    headers = {"Content-Type": "application/json", "Cookie": velog_cookie}
    # 제목에서 유효한 URL slug 생성
    url_slug = re.sub(r'[^\w\s-]', '', title).strip().lower().replace(" ", "-")
    # 제목이 비어있을 경우 대체 slug 생성
    if not url_slug:
        import uuid
        url_slug = f"untitled-post-{uuid.uuid4().hex[:8]}"

    variables = {
        "title": title, "body": body, "tags": tags, "is_markdown": True,
        "is_temp": False, "is_private": False, "url_slug": url_slug,
        "thumbnail": None, "meta": {"short_description": summary},
        "series_id": None, "token": None
    }
    payload = {
        "operationName": "WritePost",
        "query": """
        mutation WritePost($title: String, $body: String, $tags: [String], $is_markdown: Boolean, $is_temp: Boolean, $is_private: Boolean, $url_slug: String, $thumbnail: String, $meta: JSON, $series_id: ID, $token: String) {
          writePost(title: $title, body: $body, tags: $tags, is_markdown: $is_markdown, is_temp: $is_temp, is_private: $is_private, url_slug: $url_slug, thumbnail: $thumbnail, meta: $meta, series_id: $series_id, token: $token) {
            id user { id username } url_slug
          }
        }
        """,
        "variables": variables
    }

    response = requests.post(VELO_API_URL, headers=headers, json=payload)
    print("Velog status:", response.status_code)
    print("Velog response text:", response.text)

    if response.status_code != 200:
        raise Exception(f"Velog API 오류: {response.status_code} {response.text}")
    return response.json()


# --- Flask 라우트 ---

@app.route("/post", methods=["POST"])
def post_from_pdf():
    try:
        # 파일이 multipart/form-data로 전송되었는지 확인
        if 'pdf' not in request.files:
            return jsonify({"error": "PDF 파일이 필요합니다."}), 400

        pdf_file = request.files['pdf']
        velog_cookie = request.form.get("velog_cookie")

        if not velog_cookie:
            return jsonify({"error": "velog_cookie가 필요합니다."}), 400

        # ... (이하 코드는 변경 없음)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            pdf_file.save(temp_pdf.name)
            temp_pdf_path = temp_pdf.name

        print("PDF 처리 시작...")
        processed_text, image_details = process_pdf(temp_pdf_path)
        print("PDF 처리 완료.")

        os.unlink(temp_pdf_path)

        print("블로그 콘텐츠 생성 시작 (Upstage Solar)...")
        title, summary, body_with_placeholders, tags = get_summary_title_body_tags(processed_text)
        print("블로그 콘텐츠 생성 완료.")

        final_body = body_with_placeholders
        for placeholder, markdown_img in image_details.items():
            final_body = final_body.replace(placeholder, markdown_img)

        print("Velog 포스팅 시작...")
        result = post_to_velog(title, final_body, tags, summary, velog_cookie)
        print("Velog 포스팅 완료.")

        # 포스팅 성공 시, 프론트엔드로 제목, 요약, 본문, 태그를 함께 반환
        return jsonify({
            "success": True,
            "message": "PDF를 분석하여 Velog에 성공적으로 포스팅되었습니다!",
            "velogResponse": result,
            "title": title,
            "summary": summary,
            "body": final_body,
            "tags": tags
        }), 200

    except Exception as e:
        print(f"전체 프로세스 에러: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
