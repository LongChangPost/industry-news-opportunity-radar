---
name: industry-news-opportunity-radar
description: Build reusable industry opportunity radars for news, policy, projects, tenders, investment promotion, competitor movement, park development, and customer market briefs. Use when an AI agent needs to onboard a client, create radar_config.json, define sources, dedupe leads, score opportunities, and produce daily, weekly, monthly, or flash briefs with concrete consulting judgement across any industry or region.
---

# Industry News Opportunity Radar

## Workflow

Use this skill to create a client-specific opportunity radar. Do not search first. Start by asking one compact onboarding question set, then convert the answers into a reusable config and run the radar.

1. Ask the client first. Use `references/onboarding.md` and collect client type, region, industry, goals, risk limits, frequency, channel, brief length, and dedupe preference.
2. Generate `radar_config.json`. Use `scripts/configure_project.py` when answers are available as JSON.
3. Set search sources and query sets. Follow `references/source-policy.md`; use `scripts/build_search_queries.py` to expand the config into source-specific search queries.
4. Collect and normalize items. Keep title, source, source_type, url, published_at, region, industry, summary, entities, and lifecycle fields when possible.
5. Dedupe. Prefer URL; otherwise use title plus source hash. Merge tender plan, tender notice, and award result for the same project into one lifecycle lead.
6. Score. Run `scripts/score_items.py` or apply `references/analysis-rubric.md`.
7. Output the brief. Run `scripts/render_brief.py` and use `references/report-templates.md`.
8. Write history only after delivery succeeds. Use `--mark-sent` only after the brief was actually sent; dry runs and tests must not update `sent_history.json`.

## Output Standard

Every item must include a concrete consulting judgement. Do not use generic trend language. The judgement must mention at least one specific entity, project type, payer, executor, regulator, or next observable event from the item.

Respect explicit user output limits. If the user says "每天一条", "top 1", or "only one", set `top_n` to 1 and output exactly one lead unless there are no qualified new leads. If the channel is chat or Telegram, paste the rendered brief body in the chat; do not only report validation status or a file path.

Required analysis fields for each lead:

- What this shows
- Who may pay
- Who to observe next
- How to validate within 30 days
- What not to do yet
- Consulting judgement

## Small-Model-Safe Use

Keep model tasks short and structured so the workflow works across stronger and weaker models. Analyze one item, or only a few items, at a time. Ask for JSON. Do not ask the model to write long essays. Require it to quote concrete entities from the title/source when making judgement.

For model-based analysis, load `references/analysis-rubric.md` and use the structured item-analysis prompt exactly or with only field substitutions.

## Customer-Finding Mode

When the objective is `customers`, do not drift into investor, subsidy-only, or large government procurement framing unless the user asked for it. Translate broad industries into buyer scenarios:

- Local SMEs needing AI-enabled marketing, sales, customer service, internal documentation, training, design, video, image, workflow automation, or lightweight data整理.
- Signals include hiring, new store/opening, expo participation, brand campaign, recruitment posts, park tenant lists, association events, public training, digitalization notices, and businesses publishing frequent content.
- Consulting judgement should name the likely SME buyer or channel and a 30-day validation action, such as calling 10 businesses, reviewing recent content output, offering a low-cost PoC, or testing one workshop.

## Scripts

```bash
python3 scripts/configure_project.py answers.json --output radar_config.json
python3 scripts/build_search_queries.py radar_config.json --output search_queries.json
python3 scripts/score_items.py items.json --config radar_config.json --output scored_items.json
python3 scripts/render_brief.py scored_items.json --config radar_config.json --top 5 --output brief.md
```

Use `--mark-sent --history sent_history.json` only after the target channel confirms delivery.

## References

- `references/onboarding.md`: first conversation, client follow-ups, config schema.
- `references/source-policy.md`: source priority, dedupe, lifecycle merge, sent history rule.
- `references/analysis-rubric.md`: scoring and small-model-safe JSON analysis prompt.
- `references/report-templates.md`: daily, weekly, monthly, and flash brief formats.
