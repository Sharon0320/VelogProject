import os
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from pdf_processor import PDFProcessor
from blog_content_generator import BlogContentGenerator
from velog_api import VelogAPI
from vector_store import VectorStore, derive_user_id_from_cookie
from embedding_service import EmbeddingService


class VelogApp:
    """메인 Velog 애플리케이션 클래스"""
    
    def __init__(self):
        # 환경 변수 로드
        load_dotenv()
        
        # 환경 변수 설정
        self.velog_api_url = os.getenv("VELO_API_URL")
        self.upstage_api_key = os.getenv("UPSTAGE_API_KEY")
        
        # Flask 앱 초기화
        self.app = Flask(__name__)
        CORS(self.app)
        
        # 서비스 클래스들 초기화
        self.pdf_processor = PDFProcessor(self.upstage_api_key)
        self.blog_generator = BlogContentGenerator(self.upstage_api_key)
        self.velog_api = VelogAPI(self.velog_api_url)
        self.vector_store = VectorStore()
        self.embedder = EmbeddingService()
        
        # 라우트 설정
        self._setup_routes()
    
    def _setup_routes(self):
        """Flask 라우트를 설정하는 메서드"""
        
        @self.app.route("/post", methods=["POST"])
        def post_from_pdf():
            return self._handle_pdf_posting()

        @self.app.route("/sync-embeddings", methods=["POST"])
        def sync_embeddings():
            try:
                if not self.vector_store.available():
                    return jsonify({"error": "Vector DB unavailable"}), 503

                payload = request.get_json(silent=True) or {}
                velog_cookie = payload.get("velog_cookie", "")
                user_id = derive_user_id_from_cookie(velog_cookie)
                documents = payload.get("documents", [])  # [{post_id, content}]
                contents = []
                for doc in documents:
                    post_id = str(doc.get("post_id", ""))
                    content = str(doc.get("content", "")).strip()
                    if content:
                        contents.append((post_id, content))

                # embed and upsert
                if contents:
                    embeddings = self.embedder.embed_texts([c[1] for c in contents])
                    upserts = []
                    for (post_id, content), emb in zip(contents, embeddings):
                        upserts.append((post_id, content, emb))
                    self.vector_store.upsert_documents(user_id, upserts)

                return jsonify({
                    "success": True,
                    "message": "벡터 DB 동기화가 완료되었습니다.",
                    "count": len(contents)
                }), 200
            except Exception as e:
                print("임베딩 동기화 오류:", e)
                return jsonify({"error": str(e)}), 500
    
    def _handle_pdf_posting(self):
        """PDF 포스팅 요청을 처리하는 메서드"""
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

            # PDF 처리
            processed_text, image_details = self.pdf_processor.process_pdf(temp_pdf_path)

            print("\n--- 임시 파일 삭제 ---")
            os.unlink(temp_pdf_path)
            print("임시 파일 삭제 완료.")

            # 블로그 개인화 컨텍스트 생성 (유사도 검색)
            personalization_context = None
            try:
                if self.vector_store.available():
                    query_emb = self.embedder.embed_single(processed_text)
                    user_id = derive_user_id_from_cookie(velog_cookie)
                    neighbors = self.vector_store.similarity_search(user_id, query_emb, k=5)
                    # 상위 문서 일부를 이어붙여 컨텍스트 구성
                    if neighbors:
                        joined = "\n\n".join([c[:600] for c, _ in neighbors])
                        personalization_context = joined[:4000]
            except Exception as _:
                personalization_context = None

            # 블로그 콘텐츠 생성 (개인화 컨텍스트 포함)
            print("\n=== 블로그 콘텐츠 생성 시작 (Upstage Solar) ===")
            title, summary, body_with_placeholders, tags = self.blog_generator.get_summary_title_body_tags(
                processed_text,
                personalization_context=personalization_context,
            )
            print("블로그 콘텐츠 생성 완료.")

            final_body = body_with_placeholders
            # 이미지 플레이스홀더 처리 (이미지 기능 비활성화됨)
            # for placeholder, markdown_img in image_details.items():
            #     final_body = final_body.replace(placeholder, markdown_img)

            print("\n--- 최종 본문 내용 ---")
            print(final_body[:500] + "...")  # 최종 본문 내용의 앞부분을 로그로 출력
            print("--------------------------------------")

            # Velog 포스팅
            print("\n=== Velog 포스팅 시작 ===")
            result = self.velog_api.post_to_velog(title, final_body, tags, summary, velog_cookie)
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
    
    def run(self, host="0.0.0.0", port=5000, debug=True):
        """애플리케이션을 실행하는 메서드"""
        self.app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    app = VelogApp()
    app.run()
