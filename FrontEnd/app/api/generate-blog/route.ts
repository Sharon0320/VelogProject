import { NextResponse } from "next/server"

// Flask 백엔드 URL
const FLASK_API_URL = "http://localhost:5000/post"

export async function POST(req: Request) {
  try {
    const formData = await req.formData()
    const pdfFile = formData.get("pdf_file") as File
    const velogCookie = formData.get("velog_cookie") as string

    if (!pdfFile) {
      return NextResponse.json({ error: "PDF 파일이 필요합니다." }, { status: 400 })
    }

    if (!velogCookie) {
      return NextResponse.json({ error: "Velog 쿠키가 필요합니다." }, { status: 400 })
    }

    // 파일 형식 검증
    if (pdfFile.type !== "application/pdf") {
      return NextResponse.json({ error: "PDF 파일만 업로드 가능합니다." }, { status: 400 })
    }

    // 파일 크기 검증 (10MB)
    if (pdfFile.size > 10 * 1024 * 1024) {
      return NextResponse.json({ error: "파일 크기는 10MB 이하여야 합니다." }, { status: 400 })
    }

    // Flask 백엔드로 FormData 전송
    const backendFormData = new FormData()
    backendFormData.append("pdf_file", pdfFile)
    backendFormData.append("velog_cookie", velogCookie)

    const response = await fetch(FLASK_API_URL, {
      method: "POST",
      body: backendFormData,
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Flask API 오류: ${response.status} ${errorText}`)
    }

    const result = await response.json()

    // Flask 응답을 프론트엔드 형식에 맞게 변환
    return NextResponse.json({
      success: true,
      velogResponse: result.velogResponse,
      message: result.message || "PDF 분석 및 Velog 포스팅이 완료되었습니다!",
      title: result.title,
      summary: result.summary,
      body: result.body,
      tags: result.tags,
    })
  } catch (error) {
    console.error("Error processing PDF:", error)
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "알 수 없는 오류가 발생했습니다.",
      },
      { status: 500 },
    )
  }
}
