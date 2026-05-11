# Notion 주간보고 자동 취합기

팀원 주간보고를 자동으로 모아 Claude가 요약해서 노션 관리자 페이지로 저장합니다.

## 설치

```bash
pip install -r requirements.txt
```

## 환경 설정

1. `.env.example`을 `.env`로 복사
2. 각 항목 채우기:
   - `NOTION_API_KEY`: notion.so/my-integrations에서 발급
   - `CLAUDE_API_KEY`: console.anthropic.com에서 발급
   - `REPORT_DB_ID`: 팀원 주간보고 DB ID
   - `SUMMARY_DB_ID`: 요약본 저장할 DB ID

## 노션 DB 구조 (팀원 주간보고 DB)

| 속성명 | 유형 | 설명 |
|--------|------|------|
| 이름   | 제목 | 보고서 제목 |
| 날짜   | 날짜 | 작성 날짜 |
| 담당자 | 사람 | 작성자 |

## 실행

```bash
python weekly_report.py
```

## 자동화 (매주 금요일 오후 5시)

Windows 작업 스케줄러에 등록하거나, 아래 명령어로 실행 파일 등록:

```
python weekly_report.py
```

## 향후 추가 예정

- `kpi_report.py` — KPI/수치 현황 자동 분석
- `meeting_minutes.py` — 회의록에서 액션아이템 추출
- `client_report.py` — 거래처별 현황 정리
