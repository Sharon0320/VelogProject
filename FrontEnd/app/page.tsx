"use client"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Sparkles, FileText, Loader2, Key, Upload, X, FileImage } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { CookieHelper } from "@/components/cookie-helper"

interface VelogResponse {
  success: boolean
  velogResponse?: any
  message?: string
  error?: string
}

interface PDFFile {
  file: File
  name: string
  size: number
  preview?: string
}

export default function VelogHelper() {
  const [pdfFile, setPdfFile] = useState<PDFFile | null>(null)
  const [blogPost, setBlogPost] = useState<VelogResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
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
    if (file.size > 10 * 1024 * 1024) {
      toast({
        title: "파일 크기 초과",
        description: "파일 크기는 10MB 이하여야 합니다.",
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

    setIsLoading(true)
    setIsProcessing(true)
    
    try {
      // FormData를 사용하여 파일 업로드
      const formData = new FormData()
      formData.append("pdf_file", pdfFile.file)
      formData.append("velog_cookie", velogCookie)

      const response = await fetch("/api/generate-blog", {
        method: "POST",
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || "Failed to post to Velog")
      }

      if (data.success) {
        toast({
          title: "🎉 성공!",
          description: data.message || "PDF를 분석하여 Velog에 성공적으로 포스팅되었습니다!",
        })

        setBlogPost({
          success: true,
          velogResponse: data.velogResponse,
          message: data.message,
        })
      } else {
        throw new Error(data.error || "포스팅에 실패했습니다.")
      }
    } catch (error) {
      console.error("Error:", error)
      toast({
        title: "오류 발생",
        description: error instanceof Error ? error.message : "알 수 없는 오류가 발생했습니다.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
      setIsProcessing(false)
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

    return `# ${blogPost.title}

${blogPost.content}

---

## 📝 요약
${blogPost.summary}

**태그:** ${blogPost.tags.map((tag) => `#${tag}`).join(" ")}`
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
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
                    <FileImage className="w-8 h-8 text-red-500" />
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
                  {isProcessing ? "PDF 분석 중..." : "AI가 글을 작성 중..."}
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  PDF 분석하여 블로그 생성하기
                </>
              )}
            </Button>
          </CardContent>
        </Card>

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
                  포스팅 완료!
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