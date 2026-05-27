# Onboarding

Start with one compact conversation. Do not search before these answers are captured.

## One-Conversation Questionnaire

Ask in this order and accept short answers:

1. Client: enterprise, individual, government/park, investor, consultant, or sales team?
2. Region: country, province, city, park, or overseas market?
3. Industry: main industry, upstream/downstream, paused industries, excluded industries?
4. Goal: customers, projects, policies, technical cooperation, investment opportunities, tenders, competitors?
5. Risk limits: external outreach allowed or internal observation only? no advance payment? no license/compliance-heavy areas?
6. Frequency: daily, weekly, monthly, or flash?
7. Channel: local file, Telegram, Notion, email, or copy-ready text?
8. Brief length: top 3, 5, 6, or all?
9. Dedupe: default yes; only push new items unless the client says otherwise.
10. Freshness window: default 7 days for daily/weekly radar, 30 days for monthly radar.

Use this single message:

```text
先不搜索，我先把雷达配置问清楚。请按 1-9 简短回答：
1. 客户是谁：
2. 关注区域：
3. 关注行业：
4. 目标：
5. 风险边界：
6. 输出频率：
7. 输出渠道：
8. 每期条数：
9. 是否查重：
10. 信息时间窗口：
```

## Follow-Ups By Client Type

- Enterprise: ask target customer segment, existing products/services, sales cycle, forbidden deal types.
- Government or park: ask招商方向, preferred project size, local carrier platforms, land/energy/environment constraints.
- Investor: ask ticket size, stage, geography, investment exclusions, whether policy subsidy matters.
- Consultant: ask deliverable type, client decision-maker, evidence standard, and whether outbound validation is allowed.
- Sales team: ask ICP, region owner, contactable accounts, CRM handoff format, and urgency level.
- Individual: ask whether the radar is for learning, job search, side business, or investment observation.

## Final Config JSON Schema

Produce `radar_config.json` with this shape:

```json
{
  "client": {
    "name": "string",
    "type": "enterprise|individual|government_park|investor|consultant|sales_team|other",
    "profile": "string"
  },
  "regions": {
    "primary": ["string"],
    "secondary": ["string"],
    "excluded": ["string"],
    "overseas": false
  },
  "industries": {
    "primary": ["string"],
    "upstream_downstream": ["string"],
    "paused": ["string"],
    "excluded": ["string"]
  },
  "objectives": ["customers", "projects", "policies", "technical_cooperation", "investment", "tenders", "competitors"],
  "risk_limits": {
    "outreach_allowed": false,
    "internal_observation_only": true,
    "no_advance_payment": true,
    "avoid_license_or_compliance_heavy": true,
    "notes": ["string"]
  },
  "output": {
    "frequency": "daily|weekly|monthly|flash",
    "channels": ["local_file"],
    "top_n": 5,
    "language": "zh-CN"
  },
  "dedupe": {
    "enabled": true,
    "only_new": true,
    "history_path": "sent_history.json"
  },
  "collection": {
    "freshness_days": 7,
    "primary_source_required_for_a_grade": true,
    "cross_check_media_items": true,
    "query_budget_per_run": 30
  },
  "sources": [
    {
      "name": "string",
      "type": "government|enterprise|park_association|media|self_media",
      "priority": 1,
      "base_url": "string",
      "query_keywords": ["string"]
    }
  ],
  "query_sets": [
    {
      "name": "string",
      "keywords": ["string"],
      "regions": ["string"],
      "source_types": ["government"]
    }
  ]
}
```
