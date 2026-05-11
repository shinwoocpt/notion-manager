"""
주간보고 자동 취합기
- 노션 팀원 주간보고 DB에서 이번 주 보고서 수집
- Claude로 핵심 요약 + 이슈/리스크 추출
- 관리자용 요약 페이지를 노션에 자동 생성
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from notion_client import Client
import anthropic

load_dotenv()

notion = Client(auth=os.environ["NOTION_API_KEY"])
claude = anthropic.Anthropic(api_key=os.environ["CLAUDE_API_KEY"])

REPORT_DB_ID = os.environ["REPORT_DB_ID"]
SUMMARY_DB_ID = os.environ["SUMMARY_DB_ID"]


def get_week_range():
    today = datetime.now()
    start = today - timedelta(days=today.weekday())  # 이번 주 월요일
    end = start + timedelta(days=6)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def fetch_weekly_reports():
    """노션 DB에서 이번 주 팀원 보고서 수집"""
    week_start, week_end = get_week_range()

    results = notion.databases.query(
        database_id=REPORT_DB_ID,
        filter={
            "and": [
                {
                    "property": "날짜",
                    "date": {
                        "on_or_after": week_start,
                        "on_or_before": week_end,
                    },
                }
            ]
        },
    )

    reports = []
    for page in results["results"]:
        props = page["properties"]

        # 노션 페이지 제목 추출
        title = ""
        if "이름" in props and props["이름"]["title"]:
            title = props["이름"]["title"][0]["plain_text"]

        # 작성자 추출 (사람 속성)
        author = ""
        if "담당자" in props and props["담당자"]["people"]:
            author = props["담당자"]["people"][0]["name"]

        # 페이지 본문 내용 가져오기
        content = fetch_page_content(page["id"])

        reports.append({"author": author, "title": title, "content": content})

    return reports


def fetch_page_content(page_id):
    """노션 페이지 블록 내용을 텍스트로 추출"""
    blocks = notion.blocks.children.list(block_id=page_id)
    text_parts = []

    for block in blocks["results"]:
        block_type = block["type"]
        block_data = block.get(block_type, {})

        # 텍스트가 있는 블록 유형들 처리
        rich_text = block_data.get("rich_text", [])
        for rt in rich_text:
            text_parts.append(rt.get("plain_text", ""))

    return "\n".join(text_parts)


def summarize_with_claude(reports):
    """Claude로 전체 보고서 취합 요약 생성"""
    if not reports:
        return "이번 주 제출된 주간보고가 없습니다."

    # 개인별 보고서 텍스트 조합
    combined = ""
    for r in reports:
        combined += f"\n\n[{r['author']} - {r['title']}]\n{r['content']}"

    week_start, week_end = get_week_range()

    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"""다음은 {week_start} ~ {week_end} 주간 팀원들의 주간보고입니다.
관리자가 한눈에 파악할 수 있도록 아래 형식으로 정리해주세요:

## 이번 주 핵심 성과
(전체 팀 기준 3~5줄 요점)

## 팀원별 진행 현황
(각 팀원의 핵심 내용 1~2줄씩)

## 이슈 / 리스크
(문제가 될 수 있는 항목, 없으면 "없음")

## 다음 주 주요 일정
(언급된 예정 사항 정리)

---
{combined}""",
            }
        ],
    )

    return response.content[0].text


def create_summary_page(summary_text, reports):
    """관리자용 요약 페이지를 노션에 생성"""
    week_start, week_end = get_week_range()
    title = f"주간보고 요약 ({week_start} ~ {week_end})"

    # 요약 텍스트를 노션 블록으로 변환
    blocks = []
    for line in summary_text.split("\n"):
        if line.startswith("## "):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": line[3:]}}]
                },
            })
        elif line.strip():
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": line}}]
                },
            })

    # 제출자 목록 추가
    submitters = ", ".join([r["author"] for r in reports if r["author"]])
    blocks.insert(0, {
        "object": "block",
        "type": "callout",
        "callout": {
            "icon": {"type": "emoji", "emoji": "📋"},
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": f"제출자 ({len(reports)}명): {submitters}"},
                }
            ],
        },
    })

    # 노션 페이지 생성
    new_page = notion.pages.create(
        parent={"database_id": SUMMARY_DB_ID},
        properties={
            "이름": {"title": [{"text": {"content": title}}]},
            "날짜": {"date": {"start": week_start, "end": week_end}},
        },
        children=blocks,
    )

    return new_page["url"]


def main():
    print("주간보고 수집 중...")
    reports = fetch_weekly_reports()
    print(f"→ {len(reports)}개 보고서 수집 완료")

    if not reports:
        print("이번 주 보고서가 없습니다.")
        return

    print("Claude로 요약 분석 중...")
    summary = summarize_with_claude(reports)

    print("노션에 요약 페이지 생성 중...")
    page_url = create_summary_page(summary, reports)

    print(f"\n완료! 요약 페이지: {page_url}")
    print("\n" + "=" * 50)
    print(summary)


if __name__ == "__main__":
    main()
