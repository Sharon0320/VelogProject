"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Sparkles, FileText, Loader2, Key } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { CookieHelper } from "@/components/cookie-helper"

interface VelogResponse {
  success: boolean
  velogResponse?: any
  message?: string
  error?: string
}

export default function VelogHelper() {
  const [input, setInput] = useState("")
  const [blogPost, setBlogPost] = useState<VelogResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const { toast } = useToast()
  // 상태 추가
  const [velogCookie, setVelogCookie] = useState("")

  const generateBlogPost = async () => {
    if (!input.trim()) {
      toast({
        title: "입력 필요",
        description: "블로그 글 내용을 입력해주세요.",
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
    try {
      const response = await fetch("/api/generate-blog", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          content: input,
          velogCookie: velogCookie,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || "Failed to post to Velog")
      }

      if (data.success) {
        toast({
          title: "🎉 성공!",
          description: data.message || "Velog에 성공적으로 포스팅되었습니다!",
        })

        // 성공 시 결과 표시
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center py-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">✨ Velog 자동 글 작성 도우미</h1>
          <p className="text-lg text-gray-600">간단한 글을 입력하면 예쁜 블로그 글과 태그를 자동으로 만들어드려요!</p>
        </div>

        {/* Input Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />글 내용 입력
            </CardTitle>
            <CardDescription>
              작성하고 싶은 블로그 글의 내용을 자유롭게 입력해주세요. 간단한 메모나 아이디어도 괜찮아요!
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              placeholder="예: 오늘 React Hook을 공부했다. useState와 useEffect를 배웠는데 정말 유용한 것 같다. 특히 상태 관리가 쉬워졌다..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="min-h-[150px] resize-none"
            />
            <Button onClick={generateBlogPost} disabled={isLoading} className="w-full" size="lg">
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  AI가 글을 작성 중...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  블로그 글 생성하기
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
            <Textarea
              placeholder="예: _ga=GA1.1.2098360699.1712070339; access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
              value={velogCookie}
              onChange={(e) => setVelogCookie(e.target.value)}
              className="min-h-[100px] resize-none font-mono text-sm"
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
                  <li>다른 글도 작성하고 싶다면 위에서 새로운 내용을 입력하세요</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
