import re
import uuid
import requests
from typing import Dict, Any


class VelogAPI:
    """Velog API와의 상호작용을 담당하는 클래스"""
    
    def __init__(self, velog_api_url: str):
        self.velog_api_url = velog_api_url
    
    def post_to_velog(self, title: str, body: str, tags: list, summary: str, velog_cookie: str) -> Dict[str, Any]:
        """
        생성된 콘텐츠를 Velog에 포스팅하는 메서드
        """
        headers = {"Content-Type": "application/json", "Cookie": velog_cookie}
        url_slug = re.sub(r'[^\w\s-]', '', title).strip().lower().replace(" ", "-")
        if not url_slug:
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

        response = requests.post(self.velog_api_url, headers=headers, json=payload)
        print("Velog status:", response.status_code)
        print("Velog response text:", response.text)

        if response.status_code != 200:
            raise Exception(f"Velog API 오류: {response.status_code} {response.text}")
        return response.json()
