@echo off
echo 영업본부 주간보고 스킬 설치 중...

:: .claude/commands 폴더가 없으면 생성
if not exist "%USERPROFILE%\.claude\commands" (
    mkdir "%USERPROFILE%\.claude\commands"
)

:: 스킬 파일 복사
copy /Y ".claude\commands\영업주간보고.md" "%USERPROFILE%\.claude\commands\영업주간보고.md"

echo.
echo 설치 완료!
echo Claude Code에서 /영업주간보고 를 입력하면 바로 사용 가능합니다.
echo.
echo 단, Notion MCP 연결이 필요합니다.
echo Claude Code 채팅창에서 /mcp 입력 후 claude.ai Notion 인증하세요.
pause
