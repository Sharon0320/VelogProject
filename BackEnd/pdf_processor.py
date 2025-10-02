import os
import re
import requests
from typing import Tuple, Dict


class PDFProcessor:
    """PDF 파일 처리 및 텍스트 추출을 담당하는 클래스"""
    
    def __init__(self, upstage_api_key: str):
        self.upstage_api_key = upstage_api_key
    
    def convert_html_to_text(self, html_content: str) -> str:
        """간단한 HTML 태그를 제거하여 텍스트만 추출"""
        text = re.sub(r'<[^>]+>', '', html_content)
        text = re.sub(r'\n+', '\n', text).strip()
        return text
    
    def process_pdf(self, pdf_path: str) -> Tuple[str, Dict]:
        """
        PDF 파일에서 텍스트를 추출하는 메서드
        document-parse API를 사용하여 텍스트 추출
        """
        full_content = ""
        image_details = {}
        
        print("--- 1. document-parse API로 텍스트 추출 시작 ---")
        try:
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            url = "https://api.upstage.ai/v1/document-ai/document-parse"
            headers = {'Authorization': f'Bearer {self.upstage_api_key}'}
            files = {"document": ("document.pdf", pdf_bytes, "application/pdf")}
            data = {"base64_encoding": "['table']", "model": "document-parse"}

            response = requests.post(url, headers=headers, files=files, data=data)
            response.raise_for_status()

            result = response.json()
            html_text = result.get("content", {}).get("html", "")
            full_content = self.convert_html_to_text(html_text)
            print("document-parse API로 텍스트 추출 성공")
            print("--- 추출된 전체 텍스트 (일부) ---")
            print(full_content[:500] + "...")
            print("-----------------------------------")

        except requests.exceptions.RequestException as e:
            print(f"document-parse API 요청 실패: {e}")
            full_content = "텍스트 추출 실패"

        print("\n--- PDF 처리 최종 결과 ---")
        print(f"최종 처리된 전체 텍스트 (일부): {full_content[:500]}...")
        print("----------------------------")

        return full_content, image_details
