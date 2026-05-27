---
name: industry-news-opportunity-radar
description: Hermes/MiniMax skill for building client-specific industry opportunity radars from news, policy, projects, tenders, investment promotion, competitor movement, parks, and customer market signals. Always onboard first, then generate structured config, source-specific search queries, scored leads, and daily/weekly/monthly/flash briefs with concrete consulting judgement.
---

# Industry News Opportunity Radar for Hermes + MiniMax

## Trigger

Use this skill when Leo asks Coco to build, run, test, or improve an industry opportunity radar, policy radar, tender radar, competitor radar, city/park/project opportunity scan, or client daily/weekly/monthly brief.

## Hard Rules

1. Do not search first. Ask the onboarding question set first unless the user already gave every required field.
2. Keep tasks short. MiniMax should analyze one item or a small batch at a time.
3. Prefer JSON fields over free-form prose.
4. Do not produce generic judgement. Every lead must mention a concrete entity, project type, payer, executor, regulator, or next observable event from the item.
5. If source is media or self-media, mark `confirmation_required: true` and name the official/enterprise source to verify.
6. Write `sent_history` only after the user or sender confirms delivery success. Test runs must use `no_mark_sent: true`.
7. If a fact was not searched or verified, say it is unverified. Do not invent URLs, budgets, or policies.
8. Separate report frequency from item count. “每天一份报告/每天一个报告” means daily cadence. “top10/每天10条/10条线索” means 10 leads inside each report.

## Step 1: Onboard First

Ask exactly this, in one message:

```text
先不搜索，我先把雷达配置问清楚。请按 1-10 简短回答：
1. 客户是谁：企业/个人/政府园区/投资人/咨询顾问/销售团队？
2. 关注区域：国家/省/市/园区/海外市场？
3. 关注行业：主行业、上下游、暂缓行业、排除行业？
4. 目标：找客户/项目/政策/技术合作/投资机会/招投标/竞品？
5. 风险边界：是否允许外联、是否只做内部观察、是否不能垫资、是否避开牌照/合规重业务？
6. 输出频率：日报/周报/月报/临时快报？
7. 输出渠道：本地文件/Telegram/Notion/邮件/复制文本？
8. 每期条数：3/5/6/10/全量？这是每份报告里的线索数，不是每天几份报告。
9. 是否查重：默认是，只推新增。
10. 信息时间窗口：默认日报 7 天、周报 14 天、月报 30 天。
```

## Step 2: Generate Config

After answers are available, output `radar_config` JSON:

```json
{
  "client": {"name": "", "type": "enterprise|individual|government_park|investor|consultant|sales_team|other", "profile": ""},
  "regions": {"primary": [], "secondary": [], "excluded": [], "overseas": false},
  "industries": {"primary": [], "upstream_downstream": [], "paused": [], "excluded": []},
  "objectives": ["projects", "policies", "tenders", "technical_cooperation"],
  "risk_limits": {"outreach_allowed": false, "internal_observation_only": true, "no_advance_payment": true, "avoid_license_or_compliance_heavy": true, "notes": []},
  "output": {"frequency": "daily", "channels": ["local_file"], "top_n": 5, "language": "zh-CN"},
  "dedupe": {"enabled": true, "only_new": true, "history_path": "sent_history.json"},
  "collection": {"freshness_days": 7, "primary_source_required_for_a_grade": true, "cross_check_media_items": true, "query_budget_per_run": 30}
}
```

## Step 3: Build Search Queries

Output `search_queries` JSON. Keep each query source-specific:

```json
{
  "queries": [
    {"source_type": "government", "query": "{region} {industry} 政策 申报 site:gov.cn", "freshness_days": 7, "primary_source_required": true},
    {"source_type": "government", "query": "{region} {industry} 招标 中标 公共资源交易", "freshness_days": 7, "primary_source_required": true},
    {"source_type": "enterprise", "query": "{industry} 公告 投资者关系 战略合作 采购", "freshness_days": 7, "primary_source_required": true},
    {"source_type": "park_association", "query": "{region} {industry} 园区 招商 场景征集 供需对接", "freshness_days": 7, "primary_source_required": true},
    {"source_type": "media", "query": "{region} {industry} 项目 签约 开工 新闻", "freshness_days": 7, "primary_source_required": false},
    {"source_type": "self_media", "query": "{region} {industry} 动向 低权重参考", "freshness_days": 7, "primary_source_required": false}
  ]
}
```

Source priority:

1. Government, development reform, industry/IT, commerce, natural resources, public resource trading, procurement.
2. Enterprise official sites and listed-company announcements.
3. Park, investment promotion, and industry associations.
4. Mainstream media.
5. Self-media as low-weight keyword discovery only.

## Step 4: Normalize Items

Each item should use this shape:

```json
{
  "title": "",
  "source": "",
  "source_type": "government|enterprise|park_association|media|self_media",
  "url": "",
  "published_at": "YYYY-MM-DD",
  "region": "",
  "industry": "",
  "topic": "",
  "summary": "",
  "entities": [],
  "buyer": "",
  "payer": "",
  "project_name": "",
  "lifecycle_project_id": ""
}
```

Dedupe:

- URL first.
- Without URL, hash normalized title + source.
- Tender plan, tender notice, candidate award, and final award for the same project become one lifecycle lead.

## Step 5: Score

Score 0-5 per dimension:

```json
{
  "policy_fit": 0,
  "budget_trace": 0,
  "customer_clarity": 0,
  "thirty_day_loop": 0,
  "risk_noise_deduction": 0,
  "source_type": "government",
  "evidence_level": "primary_official|primary_industry|secondary_media|low_confidence",
  "confirmation_required": false,
  "total": 0,
  "grade": "A|B|C|D"
}
```

Formula: `total = policy_fit + budget_trace + customer_clarity + thirty_day_loop - risk_noise_deduction`.

Grade: A >= 14, B 10-13, C 6-9, D <= 5. A-grade requires primary source, named payer/executor, and visible next event.

## Step 6: MiniMax Item Analysis Prompt

Use this for one item at a time:

```text
你是行业机会雷达分析员。只分析 1 条线索。不要写长文。不要输出操作说明。

输入：
radar_config = {{radar_config}}
item = {{item}}
scoring_result = {{scoring_result}}

任务：
1. 必须引用 item 标题或来源里的具体实体、项目类型、付款方或执行方。
2. 不允许写“值得关注”“持续跟踪”“有机会”等空洞套话，除非后面接具体对象和验证动作。
3. 如果看不出付款方，就写最可能付款/发起的一方，并说明依据。
4. 如果来源是媒体或自媒体，必须说明需要回查哪个官方/企业来源。
5. 输出 JSON，字段必须完整，不要 Markdown。

输出 JSON：
{
  "commercial_meaning": "这条说明什么，必须结合标题中的实体或项目类型",
  "likely_payer": "最可能付款/发起/采购的一方",
  "observe_next": ["接下来观察的实体或事件 1", "接下来观察的实体或事件 2"],
  "thirty_day_validation": "30 天内一个可执行验证动作",
  "do_not_do": "证据不足前暂时不要做的事",
  "consulting_judgement": "针对本条的具体咨询判断，必须出现实体、项目类型、付款方或执行方之一"
}
```

## Step 7: Brief Template

Daily brief starts directly from this heading:

```markdown
## 今日内部关注

### 1. 标题
- 产业/主题：
- 级别/分数/风险：
- 切入：
- 内部观察：
- 咨询判断：
- 链接：
```

Do not include usage instructions in the brief.

## Concrete Judgement Examples

Tender/construction:

```text
这类施工线索不适合直接接工程，适合倒推项目业主、总包和安装队，验证施工留痕、验收资料和台账外包需求。
```

Policy:

```text
这类政策线索不是马上成交信号，应该跟后续申报指南、主管部门答疑和企业名单，判断是否能做材料辅导或项目包装。
```

Technical cooperation:

```text
这类技术合作线索说明需求已外溢，但先不要碰设备投资，先做合规资料、台账和 PoC 场景。
```

## Self-Test Rule

When Leo asks for a test, output:

- `PASS` only if onboarding-first, config, queries, scoring, brief fields, concrete consulting judgement, and sent_history rule all appear.
- `FAIL: reason` if any requirement is missing.
