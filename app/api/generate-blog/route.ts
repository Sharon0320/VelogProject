import { NextResponse } from "next/server"

// Flask 백엔드 URL
const FLASK_API_URL = "http://localhost:5000/post"

export async function POST(req: Request) {
  try {
    const { content, velogCookie } = await req.json()

    if (!content) {
      return NextResponse.json({ error: "Content is required" }, { status: 400 })
    }

    // Flask 백엔드로 POST 요청 (velog_cookie 포함)
    const response = await fetch(FLASK_API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        body: content,
        velog_cookie: velogCookie,
      }),
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Flask API 오류: ${response.status} ${errorText}`)
    }

    const result = await response.json()

    // Flask 응답을 프론트엔드 형식에 맞게 변환
    return NextResponse.json({
      success: true,
      velogResponse: result,
      message: "Velog에 성공적으로 포스팅되었습니다!",
    })
  } catch (error) {
    console.error("Error posting to Velog:", error)
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "알 수 없는 오류가 발생했습니다.",
      },
      { status: 500 },
    )
  }
}
