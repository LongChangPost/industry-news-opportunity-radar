# Source Policy

## Source Priority

1. Government official sites: development and reform, industry and information technology, commerce, natural resources, ecology/environment, public resource trading, procurement.
2. Enterprise official sites and listed-company disclosures.
3. Park, investment promotion, and industry association sites.
4. Mainstream media.
5. Self-media: low-weight reference only; do not treat as confirmation.

## Source Rules

- Prefer primary source links over syndicated copies.
- Keep source name, source_type, published_at, url, and retrieval date when available.
- If a media item cites an official document, search for the official document before scoring.
- Low-weight sources can suggest search keywords but should not drive A-grade judgement alone.
- A-grade leads require a primary source, a named payer/executor, and a visible next event such as申报截止、招标节点、名单公示、项目业主公告、上市公司公告.
- Media and self-media items must be marked `confirmation_required` until matched to official or enterprise sources.
- Do not fabricate links or source metadata. If URL, source, date, budget, or subsidy amount is unknown, write `待核验` instead of guessing.
- Any exact budget, subsidy amount, deadline, or named buyer must be traceable to an original source URL or explicitly marked unverified.

## Search Query Rules

- Build query sets by source type, not one giant web search.
- Government queries combine region + industry + action words such as 政策, 申报, 补贴, 招标, 中标, 项目, 开工, 公示.
- Enterprise queries combine company/industry + 公告, 投资者关系, 战略合作, 采购, 产能, 中标, 合同.
- Park and association queries combine region + 园区, 招商, 投促, 协会, 供需对接, 场景征集.
- Media queries are discovery only; if useful, backtrack to the primary source before final judgement.
- Self-media queries are keyword discovery only and default to low confidence.

## Evidence Levels

- `primary_official`: government, public resource trading, procurement, exchange filing, enterprise official announcement.
- `primary_industry`: park, investment promotion, or association page with named organizer or project owner.
- `secondary_media`: mainstream media report with source attribution.
- `low_confidence`: self-media, repost, rumor, or item without payer/executor/source URL.

## Dedupe Rules

- URL is the first dedupe key.
- If URL is missing, use normalized title plus source hash.
- If the same project appears as tender plan, tender notice, candidate award, and final award, merge it into one lifecycle lead.
- Keep the most advanced lifecycle stage and preserve earlier stage notes in `lifecycle_events`.
- If two items share project owner, project name, region, and procurement number, treat them as the same lifecycle lead even with different URLs.

## Sent History

- Write `sent_history.json` only after the delivery channel confirms success.
- Dry runs, preview renders, and tests must run with no sent marking.
- `scripts/render_brief.py` defaults to no sent marking and supports explicit `--no-mark-sent`.
- Use `--mark-sent --history sent_history.json` only after a successful local save or channel send.
