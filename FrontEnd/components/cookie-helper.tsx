"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { ChevronDown, ChevronUp, HelpCircle } from "lucide-react"

export function CookieHelper() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <Card className="border-yellow-200 bg-yellow-50">
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <CollapsibleTrigger asChild>
          <CardHeader className="cursor-pointer hover:bg-yellow-100 transition-colors">
            <CardTitle className="flex items-center justify-between text-yellow-800">
              <div className="flex items-center gap-2">
                <HelpCircle className="w-5 h-5" />
                쿠키 복사 도움말
              </div>
              {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </CardTitle>
            <CardDescription className="text-yellow-700">
              Velog 쿠키를 복사하는 자세한 방법을 확인하세요
            </CardDescription>
          </CardHeader>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <CardContent className="text-yellow-800">
            <div className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2">🔧 Chrome/Edge에서 쿠키 복사하기:</h4>
                <ol className="list-decimal list-inside space-y-2 text-sm">
                  <li>
                    Velog에 로그인한 상태에서 <kbd className="bg-yellow-200 px-1 rounded">F12</kbd> 키를 눌러 개발자
                    도구를 엽니다
                  </li>
                  <li>
                    <strong>Application</strong> 탭을 클릭합니다
                  </li>
                  <li>
                    왼쪽 사이드바에서 <strong>Storage → Cookies → https://velog.io</strong>를 클릭합니다
                  </li>
                  <li>
                    오른쪽에 표시되는 쿠키 목록에서 <kbd className="bg-yellow-200 px-1 rounded">Ctrl+A</kbd>로 모두 선택
                  </li>
                  <li>
                    <kbd className="bg-yellow-200 px-1 rounded">Ctrl+C</kbd>로 복사한 후 위의 입력창에 붙여넣기
                  </li>
                </ol>
              </div>

              <div>
                <h4 className="font-semibold mb-2">🦊 Firefox에서 쿠키 복사하기:</h4>
                <ol className="list-decimal list-inside space-y-2 text-sm">
                  <li>
                    <kbd className="bg-yellow-200 px-1 rounded">F12</kbd> → <strong>Storage</strong> 탭 클릭
                  </li>
                  <li>
                    <strong>Cookies → https://velog.io</strong> 선택
                  </li>
                  <li>쿠키 목록을 모두 선택하여 복사</li>
                </ol>
              </div>

              <div className="bg-yellow-100 p-3 rounded-lg">
                <p className="text-sm">
                  <strong>💡 팁:</strong> 쿠키는 로그인 상태를 유지하기 위한 정보입니다. 개인정보이므로 다른 사람과
                  공유하지 마세요!
                </p>
              </div>
            </div>
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  )
}
