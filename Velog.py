from flask import Flask, request, jsonify
import requests
import re


app = Flask(__name__)


# Perplexity API 정보
from dotenv import load_dotenv
import os


load_dotenv()  # .env 파일에서 환경변수 불러오기

PPLX_API_KEY = os.getenv("PPLX_API_KEY")
PPLX_API_URL = os.getenv("PPLX_API_URL")
VELO_API_URL = os.getenv("VELO_API_URL")

def remove_references(text):
    """[숫자] 형태의 reference 제거"""
    return re.sub(r'\[\d+\]', '', text)


def get_summary_title_body_tags(text):
    prompt = f"""
아래 글을 읽고, 각 항목을 반드시 한 줄씩 아래처럼 써줘, : 뒤에는 조건들이니 참고해서 써줘줘:
제목: 이 글로 쓸 기술블로그의 제목을 추천해줘
요약: 내용을 3문장으로 요약해줘.
본문: 지금까지의 내용을 바탕으로 기술블로그를 쓸건데, 본문 내용을 해치지 않고, 쓸 내용을 교수님께 칭찬받을 수 있게 자세하게 정리해줘 (트러블슈팅 형식이면 더 좋음 내용 보고 잘 판단해)
태그: 이 글의 주요 키워드들을 태그로, 쉼표로 구분해서 한 줄로만 출력해줘.
글: {text}
"""
    headers = {
        "Authorization": f"Bearer {PPLX_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "sonar-pro",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(PPLX_API_URL, headers=headers, json=data)
    print("Perplexity status:", response.status_code)
    if response.status_code != 200:
        print("Perplexity response text:", response.text)
        raise Exception(f"Perplexity API 오류: {response.status_code} {response.text}")
    try:
        result = response.json()["choices"][0]["message"]["content"]
        print("Perplexity 응답 원문:\n", result)
    except Exception as e:
        print("Perplexity 응답 파싱 오류:", response.text)
        raise Exception("Perplexity API 응답 파싱 오류")


    # 멀티라인 본문 파싱
    title, summary, full_body, tags_line = "제목없음", "요약없음", "", ""
    lines = [line.rstrip() for line in result.split('\n')]
    in_body = False
    for line in lines:
        if line.startswith("제목:") or line.lower().startswith("title:"):
            title = line.split(":", 1)[1].strip()
            in_body = False
        elif line.startswith("요약:") or line.lower().startswith("summary:"):
            summary = line.split(":", 1)[1].strip()
            in_body = False
        elif line.startswith("본문:") or line.lower().startswith("content:") or line.lower().startswith("body:"):
            in_body = True
            full_body = line.split(":", 1)[1].strip()
        elif line.startswith("태그:") or line.lower().startswith("tags:"):
            tags_line = line.split(":", 1)[1].strip()
            in_body = False
        elif in_body:
            full_body += "\n" + line.strip()
    # reference 제거
    full_body = remove_references(full_body)
    tags = [tag.strip() for tag in tags_line.split(",") if tag.strip()]
    return title, summary, full_body, tags


def post_to_velog(title, body, tags, summary, velog_cookie):
    headers = {
        "Content-Type": "application/json",
        "Cookie": velog_cookie
    }
    variables = {
        "title": title,
        "body": body,
        "tags": tags,
        "is_markdown": True,
        "is_temp": False,
        "is_private": False,
        "url_slug": title.replace(" ", "-"),
        "thumbnail": None,
        "meta": {"short_description": summary},
        "series_id": None,
        "token": None
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


@app.route("/post", methods=["POST"])
def post():
    try:
        data = request.json
        body = data.get("body")
        velog_cookie = data.get("velog_cookie")
        if not body:
            return jsonify({"error": "본문이 필요합니다."}), 400
        if not velog_cookie:
            return jsonify({"error": "velog_cookie가 필요합니다."}), 400


        # 1. 요약, 제목, 본문, 태그 추천
        title, summary, full_body, tags = get_summary_title_body_tags(body)


        # 2. 벨로그에 포스팅 (본문은 full_body 사용)
        result = post_to_velog(title, full_body, tags, summary, velog_cookie)
        return jsonify(result)
    except Exception as e:
        print("에러:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)