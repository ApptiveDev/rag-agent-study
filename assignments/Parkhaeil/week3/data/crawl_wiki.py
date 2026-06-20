"""
스타듀밸리 한국어 위키 크롤러.

대상 위키: https://ko.stardewvalleywiki.com
요청 간격 딜레이를 두어 서버 부하를 최소화합니다.

사용법:
    python crawl_wiki.py

결과: docs_sample/ 디렉토리에 .md 파일로 저장됩니다.
"""

import time
import re
from pathlib import Path
import requests
from bs4 import BeautifulSoup

try:
    import markdownify
except ImportError:
    print("markdownify 미설치. pip install markdownify 실행 후 재시도.")
    raise

WIKI_BASE = "https://ko.stardewvalleywiki.com"
OUTPUT_DIR = Path(__file__).parent / "docs_sample"
REQUEST_DELAY = 1.5  # 초

# (파일명, 위키 경로, 카테고리) 수집 대상 목록
# 한국어 위키 URL이 없으면 영문 위키로 대체하고 파일명에 명시
PAGES = [
    # 농사
    ("farming_crops_spring.md", "/봄_작물", "farming"),
    ("farming_crops_summer.md", "/여름_작물", "farming"),
    ("farming_crops_fall.md", "/가을_작물", "farming"),
    ("farming_crops_winter.md", "/겨울_작물", "farming"),
    ("farming_greenhouse.md", "/온실", "farming"),
    ("farming_artisan_goods.md", "/장인_상품", "farming"),
    ("farming_keg.md", "/양조통", "farming"),
    ("farming_preserves_jar.md", "/절임통", "farming"),
    ("farming_lightning_rod.md", "/피뢰침", "farming"),
    ("farming_ancient_seed.md", "/고대_씨앗", "farming"),
    # 낚시
    ("fishing_overview.md", "/낚시", "fishing"),
    ("fishing_tackle.md", "/미끼", "fishing"),
    ("fishing_fish_list.md", "/물고기", "fishing"),
    # 광산
    ("mining_overview.md", "/광산", "mining"),
    ("mining_dwarf_scroll.md", "/드워프_두루마리", "mining"),
    ("mining_prismatic_shard.md", "/무지개_파편", "mining"),
    # 채집/축산
    ("foraging_overview.md", "/채집", "foraging"),
    ("livestock_barn.md", "/외양간", "livestock"),
    ("livestock_coop.md", "/닭장", "livestock"),
    ("livestock_mayonnaise.md", "/마요네즈_제조기", "livestock"),
    ("livestock_auto_petter.md", "/자동채집기", "livestock"),
    # 주민
    ("villagers_gift_guide.md", "/선물", "villagers"),
    ("villagers_bouquet.md", "/꽃다발", "villagers"),
    ("villagers_marriage.md", "/결혼", "villagers"),
]


def fetch_page(path: str) -> str | None:
    url = WIKI_BASE + path
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "StardewRAGStudy/1.0"})
        if resp.status_code == 404:
            print(f"  404: {url}")
            return None
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return None


def html_to_markdown(html: str, title: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # 위키 본문 영역 추출 (MediaWiki 구조)
    content = soup.find("div", {"id": "mw-content-text"})
    if not content:
        content = soup.find("div", {"class": "mw-parser-output"})
    if not content:
        return ""

    # 불필요한 요소 제거 (편집 링크, TOC, 네비게이션 박스 등)
    for tag in content.find_all(["span", "div"], class_=[
        "mw-editsection", "toc", "navbox", "hatnote",
        "catlinks", "printfooter", "mw-jump-link"
    ]):
        tag.decompose()

    md = markdownify.markdownify(str(content), heading_style="ATX", bullets="-")

    # 연속 공백 줄 정리
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = md.strip()

    return f"# {title}\n\n{md}"


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    success = 0
    for filename, path, category in PAGES:
        out_path = OUTPUT_DIR / filename
        print(f"Fetching {path} -> {filename}")

        html = fetch_page(path)
        if not html:
            print(f"  Skipped (no content)")
            time.sleep(REQUEST_DELAY)
            continue

        title = Path(filename).stem.replace("_", " ").title()
        md = html_to_markdown(html, title)
        if not md.strip():
            print(f"  Skipped (empty markdown)")
            time.sleep(REQUEST_DELAY)
            continue

        out_path.write_text(md, encoding="utf-8")
        print(f"  Saved ({len(md)} chars, category={category})")
        success += 1
        time.sleep(REQUEST_DELAY)

    print(f"\nDone. {success}/{len(PAGES)} pages saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
