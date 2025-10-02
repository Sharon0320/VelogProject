"use client"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Sparkles, FileText, Loader2, Key, Upload, X, File, FileWarning } from "lucide-react" // FileImage -> File로 변경
import { useToast } from "@/hooks/use-toast"
import { CookieHelper } from "@/components/cookie-helper"

interface VelogResponse {
  success: boolean
  velogResponse?: any
  message?: string
  error?: string
  title?: string
  summary?: string
  body?: string
  tags?: string[]
}

interface PDFFile {
  file: File
  name: string
  size: number
}

export default function VelogHelper() {
  const [pdfFile, setPdfFile] = useState<PDFFile | null>(null)
  const [blogPost, setBlogPost] = useState<VelogResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false) // isProcessing 상태 제거, isLoading으로 통합
  const { toast } = useToast()
  const [velogCookie, setVelogCookie] = useState("")
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // PDF 파일 검증
    if (file.type !== "application/pdf") {
      toast({
        title: "파일 형식 오류",
        description: "PDF 파일만 업로드 가능합니다.",
        variant: "destructive",
      })
      return
    }

    // 파일 크기 검증 (10MB 제한)
    const MAX_FILE_SIZE = 10 * 1024 * 1024
    if (file.size > MAX_FILE_SIZE) {
      toast({
        title: "파일 크기 초과",
        description: `파일 크기는 ${formatFileSize(MAX_FILE_SIZE)} 이하여야 합니다.`,
        variant: "destructive",
      })
      return
    }

    setPdfFile({
      file,
      name: file.name,
      size: file.size,
    })

    toast({
      title: "파일 업로드 완료",
      description: `${file.name} 파일이 성공적으로 업로드되었습니다.`,
    })
  }

  const removeFile = () => {
    setPdfFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const generateBlogPost = async () => {
    if (!pdfFile) {
      toast({
        title: "파일 필요",
        description: "PDF 파일을 업로드해주세요.",
        variant: "destructive",
      })
      return
    }

    if (!velogCookie.trim()) {
      toast({
        title: "쿠키 필요",
        description: "Velog 쿠키를 입력해주세요.",
        variant: "destructive",
      })
      return
    }
    
    // 블로그 포스팅 상태 초기화
    setBlogPost(null);
    setIsLoading(true)

    try {
      // FormData를 사용하여 파일 업로드
      const formData = new FormData()
      formData.append("pdf", pdfFile.file) // 백엔드와 키 일치!
      formData.append("velog_cookie", velogCookie)

      console.log("FormData 생성 완료, API 요청 시작...")

      const response = await fetch("http://127.0.0.1:5000/post", { // 백엔드 라우트와 일치하도록 수정
        method: "POST",
        body: formData,
      })

      console.log("API 응답 상태:", response.status)

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || "포스팅에 실패했습니다.")
      }

      const data = await response.json()
      console.log("API 응답 데이터:", data)

      toast({
        title: "🎉 성공!",
        description: data.message || "PDF를 분석하여 Velog에 성공적으로 포스팅되었습니다!",
      })

      setBlogPost({
        success: true,
        velogResponse: data, // velog_response 객체를 직접 넘겨줍니다.
        message: "PDF를 분석하여 Velog에 성공적으로 포스팅되었습니다!", // 응답 객체에 message가 없으면 기본값 사용
        title: data.title,
        summary: data.summary,
        body: data.body,
        tags: data.tags,
      })
    } catch (error) {
      console.error("Error:", error)
      toast({
        title: "오류 발생",
        description: error instanceof Error ? error.message : "알 수 없는 오류가 발생했습니다.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast({
      title: "복사 완료!",
      description: "클립보드에 복사되었습니다. Velog에 붙여넣기 하세요.",
    })
  }

  const generateMarkdown = () => {
    if (!blogPost) return ""

    const formattedTags = blogPost.tags && blogPost.tags.length > 0 ? blogPost.tags.map((tag: string) => `#${tag}`).join(" ") : ""

    return `# ${blogPost.title || "제목 없음"}

${blogPost.body || "본문 없음"}

---

## 📝 요약
${blogPost.summary || "요약 없음"}

**태그:** ${formattedTags || "태그 없음"}`
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  const syncEmbeddings = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/sync-embeddings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          velog_cookie: velogCookie,
          documents: blogPost?.body
            ? [
                {
                  post_id: blogPost?.velogResponse?.data?.writePost?.id || "temp",
                  content: `${blogPost?.title || ""}\n\n${blogPost?.body || ""}`.slice(0, 8000),
                },
              ]
            : [],
        }),
      })

      if (!response.ok) {
        const err = await response.json().catch(() => ({}))
        throw new Error(err.error || `동기화 실패 (${response.status})`)
      }

      const data = await response.json()
      toast({ title: "동기화 완료", description: data.message || "벡터 DB 동기화 완료" })
    } catch (e) {
      toast({
        title: "동기화 오류",
        description: e instanceof Error ? e.message : "알 수 없는 오류",
        variant: "destructive",
      })
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center py-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">✨ Velog AI 블로그 생성기</h1>
          <p className="text-lg text-gray-600">PDF 파일을 업로드하면 AI가 분석하여 기술블로그를 자동으로 만들어드려요!</p>
        </div>

        {/* PDF Upload Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />PDF 파일 업로드
            </CardTitle>
            <CardDescription>
              OpenAI나 Perplexity에서 대화한 내용을 PDF로 추출한 파일을 업로드해주세요.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {!pdfFile ? (
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <Button
                  variant="outline"
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full h-32 flex flex-col items-center justify-center gap-2"
                >
                  <Upload className="w-8 h-8 text-gray-400" />
                  <span className="text-lg font-medium">PDF 파일 선택하기</span>
                  <span className="text-sm text-gray-500">또는 파일을 여기로 드래그하세요</span>
                </Button>
              </div>
            ) : (
              <div className="border rounded-lg p-4 bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <File className="w-8 h-8 text-red-500" />
                    <div>
                      <p className="font-medium text-gray-900">{pdfFile.name}</p>
                      <p className="text-sm text-gray-500">{formatFileSize(pdfFile.size)}</p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={removeFile}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            )}
            
            <Button 
              onClick={generateBlogPost} 
              disabled={isLoading || !pdfFile} 
              className="w-full" 
              size="lg"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  <span>
                    {pdfFile ? "PDF 분석 및 포스팅 중..." : "AI가 글을 작성 중..."}
                  </span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  PDF 분석하여 블로그 생성하기
                </>
              )}
            </Button>
            <Button
              onClick={syncEmbeddings}
              variant="outline"
              className="w-full"
              disabled={isLoading || !velogCookie.trim()}
            >
              벡터 DB 동기화
            </Button>
          </CardContent>
        </Card>

        {/* Processing Progress */}
        {isLoading && (
          <Card className="border-blue-200 bg-blue-50">
            <CardHeader>
              <CardTitle className="text-blue-800 flex items-center gap-2">
                <Loader2 className="w-5 h-5 animate-spin" />
                처리 중...
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                  <span className="text-sm text-blue-700">PDF 텍스트 및 이미지 추출 중...</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse animation-delay-500"></div>
                  <span className="text-sm text-blue-700">AI 블로그 콘텐츠 생성 중...</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse animation-delay-1000"></div>
                  <span className="text-sm text-blue-700">Velog에 포스팅 중...</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Velog Cookie Input Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Key className="w-5 h-5" />
              Velog 쿠키 입력
            </CardTitle>
            <CardDescription>Velog에 포스팅하기 위해 브라우저에서 복사한 쿠키를 입력해주세요.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <textarea
              placeholder="예: _ga=GA1.1.2098360699.1712070339; access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
              value={velogCookie}
              onChange={(e) => setVelogCookie(e.target.value)}
              className="min-h-[100px] resize-none font-mono text-sm w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            />
            <div className="text-sm text-gray-600">
              <p className="font-medium mb-2">쿠키 복사 방법:</p>
              <ol className="list-decimal list-inside space-y-1 text-xs">
                <li>Velog에 로그인한 상태에서 F12 (개발자 도구) 열기</li>
                <li>Application 탭 → Storage → Cookies → https://velog.io 클릭</li>
                <li>모든 쿠키를 복사해서 위에 붙여넣기</li>
              </ol>
            </div>
          </CardContent>
        </Card>

        <CookieHelper />

        {/* Results Section */}
        {blogPost && blogPost.success && (
          <div className="space-y-6">
            {/* Success Message */}
            <Card className="border-green-200 bg-green-50">
              <CardHeader>
                <CardTitle className="text-green-800 flex items-center gap-2">
                  <Sparkles className="w-5 h-5" />
                  블로그 생성 완료!
                </CardTitle>
              </CardHeader>
              <CardContent className="text-green-700">
                <p className="text-lg font-medium">{blogPost.message}</p>
                {blogPost.velogResponse?.data?.writePost && (
                  <div className="mt-4 space-y-2">
                    <p>
                      <strong>포스트 ID:</strong> {blogPost.velogResponse.data.writePost.id}
                    </p>
                    <p>
                      <strong>URL:</strong>
                      <a
                        href={`https://velog.io/@${blogPost.velogResponse.data.writePost.user.username}/${blogPost.velogResponse.data.writePost.url_slug}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="ml-2 text-blue-600 hover:text-blue-800 underline"
                      >
                        블로그 글 보러가기 →
                      </a>
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Generated Blog Content */}
            <Card>
              <CardHeader>
                <CardTitle className="text-blue-800">📝 생성된 블로그 내용</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Title */}
                <div>
                  <h3 className="font-semibold text-gray-700 mb-2">제목</h3>
                  <div className="p-3 bg-gray-50 rounded-md border">
                    <p className="text-lg font-medium">{blogPost.title || "제목 없음"}</p>
                  </div>
                </div>

                {/* Summary */}
                <div>
                  <h3 className="font-semibold text-gray-700 mb-2">요약</h3>
                  <div className="p-3 bg-gray-50 rounded-md border">
                    <p className="text-gray-800">{blogPost.summary || "요약 없음"}</p>
                  </div>
                </div>

                {/* Body */}
                <div>
                  <h3 className="font-semibold text-gray-700 mb-2">본문</h3>
                  <div className="p-3 bg-gray-50 rounded-md border max-h-96 overflow-y-auto">
                    <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">{blogPost.body || "본문 없음"}</pre>
                  </div>
                  <Button
                    onClick={() => copyToClipboard(blogPost.body || "")}
                    variant="outline"
                    size="sm"
                    className="mt-2"
                  >
                    본문 복사
                  </Button>
                </div>

                {/* Tags */}
                <div>
                  <h3 className="font-semibold text-gray-700 mb-2">태그</h3>
                  <div className="flex flex-wrap gap-2">
                    {blogPost.tags && blogPost.tags.length > 0 ? (
                      blogPost.tags.map((tag, index) => (
                        <span
                          key={index}
                          className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
                        >
                          #{tag}
                        </span>
                      ))
                    ) : (
                      <p className="text-gray-500">태그 없음</p>
                    )}
                  </div>
                </div>

                {/* Markdown Preview */}
                <div>
                  <h3 className="font-semibold text-gray-700 mb-2">마크다운 미리보기</h3>
                  <div className="p-3 bg-gray-50 rounded-md border max-h-96 overflow-y-auto">
                    <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">{generateMarkdown()}</pre>
                  </div>
                  <Button
                    onClick={() => copyToClipboard(generateMarkdown())}
                    variant="outline"
                    size="sm"
                    className="mt-2"
                  >
                    마크다운 복사
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Instructions */}
            <Card className="border-blue-200 bg-blue-50">
              <CardHeader>
                <CardTitle className="text-blue-800">🎯 다음 단계</CardTitle>
              </CardHeader>
              <CardContent className="text-blue-700">
                <ul className="list-disc list-inside space-y-2">
                  <li>위의 링크를 클릭해서 포스팅된 글을 확인하세요</li>
                  <li>필요하면 Velog에서 추가 편집을 할 수 있습니다</li>
                  <li>다른 PDF도 분석하고 싶다면 위에서 새로운 파일을 업로드하세요</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}