# 데이터 수집 안내

## 수집 대상
**스타듀밸리 한국어 위키** (`https://ko.stardewvalleywiki.com`)

MediaWiki 기반 공개 위키. 크리에이티브 커먼즈 저작자표시-동일조건변경허락(CC BY-SA) 라이선스.

## 수집 방법

```bash
# 의존성 설치
pip install requests beautifulsoup4 markdownify

# 크롤러 실행
python data/crawl_wiki.py
```

크롤러는 `data/docs_sample/` 에 카테고리별 `.md` 파일로 저장합니다.

## 수집 페이지 목록 (25개)

| 파일명 | 위키 경로 | 카테고리 |
|--------|-----------|----------|
| farming_crops_spring.md | /봄_작물 | 농사 |
| farming_crops_summer.md | /여름_작물 | 농사 |
| farming_crops_fall.md | /가을_작물 | 농사 |
| farming_crops_winter.md | /겨울_작물 | 농사 |
| farming_greenhouse.md | /온실 | 농사 |
| farming_artisan_goods.md | /장인_상품 | 농사 |
| farming_keg.md | /양조통 | 농사 |
| farming_preserves_jar.md | /절임통 | 농사 |
| farming_lightning_rod.md | /피뢰침 | 농사 |
| farming_ancient_seed.md | /고대_씨앗 | 농사 |
| fishing_overview.md | /낚시 | 낚시 |
| fishing_tackle.md | /미끼 | 낚시 |
| fishing_fish_list.md | /물고기 | 낚시 |
| mining_overview.md | /광산 | 광산 |
| mining_dwarf_scroll.md | /드워프_두루마리 | 광산 |
| mining_prismatic_shard.md | /무지개_파편 | 광산 |
| foraging_overview.md | /채집 | 채집 |
| livestock_barn.md | /외양간 | 축산 |
| livestock_coop.md | /닭장 | 축산 |
| livestock_mayonnaise.md | /마요네즈_제조기 | 축산 |
| livestock_auto_petter.md | /자동채집기 | 축산 |
| villagers_gift_guide.md | /선물 | 주민 |
| villagers_bouquet.md | /꽃다발 | 주민 |
| villagers_marriage.md | /결혼 | 주민 |

## 서버 부하 관리
- 요청 간 1.5초 딜레이 적용
- User-Agent 명시
- 원본 전체 데이터는 저장소에 포함하지 않음 (`.gitignore` 참고)
