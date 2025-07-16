import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Velog 자동 글 작성 도우미',
  description: '글을 작성하면 AI로 적절한 태그를 추천해서 Velog애 게시물을 작성합니다.',
  generator: 'v0.dev',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
