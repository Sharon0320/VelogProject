import re
from typing import List


class TextUtils:
    """텍스트 처리 유틸리티 클래스"""
    
    @staticmethod
    def remove_references(text: str) -> str:
        """[숫자] 형태의 참조(reference) 제거"""
        return re.sub(r'\[\d+\]', '', text)
    
    @staticmethod
    def convert_html_to_text(html_content: str) -> str:
        """간단한 HTML 태그를 제거하여 텍스트만 추출"""
        text = re.sub(r'<[^>]+>', '', html_content)
        text = re.sub(r'\n+', '\n', text).strip()
        return text
    
    @staticmethod
    def clean_text(text: str) -> str:
        """텍스트를 정리하는 메서드 (참조 제거 + HTML 태그 제거)"""
        cleaned = TextUtils.remove_references(text)
        cleaned = TextUtils.convert_html_to_text(cleaned)
        return cleaned
    
    @staticmethod
    def extract_tags_from_string(tags_string: str) -> List[str]:
        """태그 문자열에서 태그 리스트를 추출하는 메서드"""
        return [tag.strip().replace('#', '') for tag in tags_string.split(",") if tag.strip()]
