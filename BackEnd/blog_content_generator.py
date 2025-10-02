import re
from typing import Tuple, List, Optional
from openai import OpenAI


class BlogContentGenerator:
    """블로그 콘텐츠 생성을 담당하는 클래스"""
    
    def __init__(self, upstage_api_key: str):
        self.upstage_client = OpenAI(
            api_key=upstage_api_key,
            base_url="https://api.upstage.ai/v1/"
        )
    
    def remove_references(self, text: str) -> str:
        """[숫자] 형태의 참조(reference) 제거"""
        return re.sub(r'\[\d+\]', '', text)
    
    def get_summary_title_body_tags(self, processed_text: str, personalization_context: Optional[str] = None) -> Tuple[str, str, str, List[str]]:
        """
        Upstage Solar API를 사용해 블로그 콘텐츠를 생성하는 메서드
        (안정적인 파싱 로직 적용)
        """
        personalization_block = ""
        if personalization_context:
            personalization_block = f"""
[사용자 개인화 컨텍스트]
아래 내용은 사용자의 평소 말투/작성 스타일과 대표 포스트의 일부입니다. 글을 생성할 때 톤과 구성, 시그니처 표현을 적절히 반영하세요. 그대로 복붙하지 말고, 과적합 없이 자연스럽게 녹여주세요.
---
{personalization_context[:2000]}
---
"""

        prompt = f"""
아래의 원본 텍스트를 분석하여, 독자들이 이해하기 쉬운 전문가 수준의 기술 블로그 포스트를 마크다운 형식으로 가독성 좋게 작성해주세요. 
아래 각 항목의 지시에 따라 정확하게 결과물을 생성해주세요. 각 항목은 반드시 한 줄로 시작해야 합니다.

제목:,요약:,본문:,태그: 앞에는 마크다운 ### 붙이지 말아줘.
그리고 제목 요약 본문 태그를 시작할 때는 꼭 제목: 요약: 본문: 태그: 처럼 :를 꼭 붙여줘.
"1.문제 정의 2. 어떤 상황인지 정리 3. 원인 분석 4. 해결 과정과 적용 5. 결과 검증 및 교훈"으로 작성해줘. 본문 첫줄에는 목차를 작성해줘. 그리고 마크다운 구분선을 추가해서 본문과 목차를 구분해줘.

제목: SEO를 고려하여 사람들의 흥미를 끌 만한 기술 블로그 제목을 추천해줘.
요약: 전체 내용을 대표할 수 있는 핵심 내용 3문장으로 요약해줘.
본문: 원본 텍스트 바탕으로, 기술 블로그 본문을 작성해줘. 다음과 같은 조건이 있어. 간결하고 이해하기 쉽게 한 문단 하나의 메시지. LLM 대답처럼 딱딱하지 않게 독자에게 스토리텔링하는 식으로 전달. 이모티콘 활용해도 돼.
태그: 이 글의 핵심 키워드를 쉼표(,)로 구분된 태그로 만들어줘. 문장 말고 쓰인 기술과 해결방법 위주로 최대 10개까지.

[개인화 지시]
가능하면 사용자의 평소 어투, 제목 패턴, 소제목 구성, 마무리 문구 스타일을 반영해줘. 아래 개인화 컨텍스트가 있으면 우선 참고하고, 없으면 일반적인 기술 블로그 톤으로 작성해줘.

{personalization_block}

[원본 텍스트]
{processed_text}
"""
        try:
            response = self.upstage_client.chat.completions.create(
                model="solar-pro2",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
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

        full_body = self.remove_references(body)
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
