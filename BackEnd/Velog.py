import os
import re
import tempfile
import requests
import base64
from io import BytesIO
import time
from PIL import Image
import fitz
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
from flask_cors import CORS


# --- 환경 변수 및 클라이언트 초기화 ---
load_dotenv()

VELO_API_URL = os.getenv("VELO_API_URL")
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")

# Flask 앱 초기화
app = Flask(__name__)
CORS(app)

# Upstage LLM을 위한 OpenAI 클라이언트 초기화 (base_url 수정)
upstage_client = OpenAI(
    api_key=UPSTAGE_API_KEY,
    base_url="https://api.upstage.ai/v1/"
)


# --- 유틸리티 함수 ---

def remove_references(text):
    """[숫자] 형태의 참조(reference) 제거"""
    return re.sub(r'\[\d+\]', '', text)


def convert_html_to_text(html_content):
    """간단한 HTML 태그를 제거하여 텍스트만 추출"""
    text = re.sub(r'<[^>]+>', '', html_content)
    text = re.sub(r'\n+', '\n', text).strip()
    return text


def preprocess_image(image_bytes, max_size=(1024, 1024), quality=85):
    """
    이미지를 압축하고 크기를 조절하여 업로드에 최적화하는 함수
    """
    try:
        img_io = BytesIO(image_bytes)
        img = Image.open(img_io)

        # 이미지 크기 조절 (원본 비율 유지)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # JPEG 형식으로 압축 (용량 감소)
        output_io = BytesIO()
        img.save(output_io, format='JPEG', quality=quality)
        output_io.seek(0)
        return output_io.read()

    except Exception as e:
        print(f"이미지 전처리 중 오류 발생: {e}")
        return image_bytes  # 오류 발생 시 원본 이미지 반환


def upload_image_to_imgbb(image_bytes, max_retries=3, initial_delay=2):
    """
    imgbb API를 사용해 이미지를 업로드하고 URL을 반환하는 함수 (재시도 로직 추가)
    """
    url = "https://api.imgbb.com/1/upload"

    if not IMGBB_API_KEY:
        print("IMGBB_API_KEY가 .env 파일에 설정되지 않았습니다.")
        return None

    # 이미지 전처리: 크기 조절 및 압축
    preprocessed_image_bytes = preprocess_image(image_bytes)

    # 이미지를 base64로 인코딩
    encoded_image = base64.b64encode(preprocessed_image_bytes)

    payload = {
        "key": IMGBB_API_KEY,
        "image": encoded_image
    }

    retries = 0
    delay = initial_delay

    while retries < max_retries:
        try:
            response = requests.post(url, data=payload, timeout=30)

            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("success"):
                    image_url = response_data["data"]["url"]
                    print(f"imgbb upload success: {image_url}")
                    return image_url
                else:
                    print(f"imgbb 업로드 실패: {response.text}")
                    return None
            elif response.status_code == 504:
                retries += 1
                print(f"ImgBB 504 오류 발생, {retries}/{max_retries} 재시도 중... 대기 시간: {delay}초")
                time.sleep(delay)
                delay *= 2
                continue
            else:
                print(f"imgbb 업로드 실패: HTTP 상태 코드 {response.status_code}")
                print(f"응답 본문: {response.text}")
                return None
        except requests.exceptions.Timeout:
            retries += 1
            print(f"요청 타임아웃 발생, {retries}/{max_retries} 재시도 중... 대기 시간: {delay}초")
            time.sleep(delay)
            delay *= 2
            continue
        except requests.exceptions.RequestException as e:
            print(f"imgbb 요청 중 예외 발생: {e}")
            return None
        except Exception as e:
            print(f"imgbb 업로드 중 예외 발생: {e}")
            return None

    print(f"최대 재시도 횟수({max_retries}회) 초과. ImgBB 업로드 실패.")
    return None


def extract_text_from_image_upstage(image_bytes):
    """
    Upstage Document OCR API를 사용해 이미지에서 텍스트를 추출하는 함수
    """
    url = "https://api.upstage.ai/v1/document-digitization"
    headers = {'Authorization': f'Bearer {UPSTAGE_API_KEY}'}
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
    (document-parse API로 텍스트 추출, 이미지 필터링 로직 제거)
    """
    full_content = ""
    image_details = {}
    image_counter = 1
    doc = None

    print("--- 1. document-parse API로 텍스트 추출 시작 ---")
    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        url = "https://api.upstage.ai/v1/document-ai/document-parse"
        headers = {'Authorization': f'Bearer {UPSTAGE_API_KEY}'}
        files = {"document": ("document.pdf", pdf_bytes, "application/pdf")}
        data = {"base64_encoding": "['table']", "model": "document-parse"}

        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()

        result = response.json()
        html_text = result.get("content", {}).get("html", "")
        full_content = convert_html_to_text(html_text)
        print("document-parse API로 텍스트 추출 성공")
        print("--- 추출된 전체 텍스트 (일부) ---")
        print(full_content[:500] + "...")  # 추출된 텍스트의 앞부분을 로그로 출력
        print("-----------------------------------")

    except requests.exceptions.RequestException as e:
        print(f"document-parse API 요청 실패: {e}")
        full_content = "텍스트 추출 실패"

    print("\n--- 2. PDF 이미지 추출 및 처리 시작 ---")
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            image_list = page.get_images(full=True)
            print(f"페이지 {page_num + 1}에서 {len(image_list)}개의 이미지 발견.")

            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]

                print(f"  > 이미지 {img_index + 1} OCR 및 ImgBB 업로드 진행...")
                ocr_text = extract_text_from_image_upstage(image_bytes)
                image_url = upload_image_to_imgbb(image_bytes)

                if image_url:
                    placeholder = f"\n--- 이미지 {image_counter} 시작 ---\n[설명: {ocr_text}]\n--- 이미지 {image_counter} 끝 ---\n"
                    full_content += placeholder
                    alt_text = ocr_text.splitlines()[0] if ocr_text else f'Image {image_counter}'
                    image_details[f"[IMAGE_{image_counter}]"] = f"![{alt_text}]({image_url})"
                    image_counter += 1
                else:
                    print(f"  > 이미지 {img_index + 1} 처리 실패 (URL 없음).")
    except Exception as e:
        print(f"PDF 이미지 처리 중 오류 발생: {e}")
    finally:
        if doc:
            doc.close()

    print("\n--- PDF 처리 최종 결과 ---")
    print(f"최종 처리된 전체 텍스트 (일부): {full_content[:500]}...")
    print(f"이미지 상세 정보: {image_details}")
    print("----------------------------")

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
태그: 이 글의 핵심 키워드를 쉼표(,)로 구분된 태그로 만들어줘. 문장 말고 쓰인 기술과 해결방법 위주로

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

    # **수정된 파싱 로직**
    title, summary, body, tags_line = "", "", "", ""
    current_section = None

    lines = result.split('\n')
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue

        # 선행하는 마크다운 헤더(#)를 제거하여 파싱 유연성 확보
        stripped_line = re.sub(r'^#+\s*', '', stripped_line)

        # 각 섹션의 시작을 감지하고 모드를 변경
        if stripped_line.startswith('제목:'):
            current_section = 'title'
            line_content = stripped_line[len('제목:'):].strip()
        elif stripped_line.startswith('요약:'):
            current_section = 'summary'
            line_content = stripped_line[len('요약:'):].strip()
        elif stripped_line.startswith('본문:'):
            current_section = 'body'
            line_content = stripped_line[len('본문:'):].strip()
        elif stripped_line.startswith('태그:'):
            current_section = 'tags'
            line_content = stripped_line[len('태그:'):].strip()
        else:
            # 섹션 키워드가 없는 줄은 현재 섹션에 추가
            line_content = stripped_line

        # 현재 섹션에 내용 추가
        if current_section == 'title':
            title += line_content
        elif current_section == 'summary':
            if summary:
                summary += "\n" + line_content
            else:
                summary = line_content
        elif current_section == 'body':
            if body:
                body += "\n" + line_content
            else:
                body = line_content
        elif current_section == 'tags':
            if tags_line:
                tags_line += ", " + line_content
            else:
                tags_line = line_content

    full_body = remove_references(body)
    tags = [tag.strip().replace('#', '') for tag in tags_line.split(",") if tag.strip()]
    summary = summary.strip()

    if not title:
        title = "제목없음"
    if not summary:
        summary = "요약없음"
    if not full_body:
        full_body = "내용없음"

    print("\n--- LLM 응답 파싱 결과 ---")
    print(f"파싱 결과: 제목='{title}'")
    print(f"파싱 결과: 요약='{summary}'")
    print(f"파싱 결과: 태그='{tags}'")
    print(f"파싱 결과: 본문 길이={len(full_body)}")
    print("------------------------")

    return title, summary, full_body, tags


def post_to_velog(title, body, tags, summary, velog_cookie):
    """
    생성된 콘텐츠를 Velog에 포스팅하는 함수
    """
    headers = {"Content-Type": "application/json", "Cookie": velog_cookie}
    url_slug = re.sub(r'[^\w\s-]', '', title).strip().lower().replace(" ", "-")
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
        if 'pdf' not in request.files:
            return jsonify({"error": "PDF 파일이 필요합니다."}), 400

        pdf_file = request.files['pdf']
        velog_cookie = request.form.get("velog_cookie")

        if not velog_cookie:
            return jsonify({"error": "velog_cookie가 필요합니다."}), 400

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            pdf_file.save(temp_pdf.name)
            temp_pdf_path = temp_pdf.name

        print("\n=== 전체 프로세스 시작 ===")
        print(f"임시 파일 경로: {temp_pdf_path}")

        processed_text, image_details = process_pdf(temp_pdf_path)

        print("\n--- 임시 파일 삭제 ---")
        os.unlink(temp_pdf_path)
        print("임시 파일 삭제 완료.")

        print("\n=== 블로그 콘텐츠 생성 시작 (Upstage Solar) ===")
        title, summary, body_with_placeholders, tags = get_summary_title_body_tags(processed_text)
        print("블로그 콘텐츠 생성 완료.")

        final_body = body_with_placeholders
        for placeholder, markdown_img in image_details.items():
            final_body = final_body.replace(placeholder, markdown_img)

        print("\n--- 최종 본문 내용 (이미지 포함) ---")
        print(final_body[:500] + "...")  # 최종 본문 내용의 앞부분을 로그로 출력
        print("--------------------------------------")

        print("\n=== Velog 포스팅 시작 ===")
        result = post_to_velog(title, final_body, tags, summary, velog_cookie)
        print("Velog 포스팅 완료.")

        print("\n=== 전체 프로세스 성공 ===")

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
        print(f"\n=== 전체 프로세스 에러 발생 ===")
        print(f"에러 내용: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
