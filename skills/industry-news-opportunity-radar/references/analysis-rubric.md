# Analysis Rubric

Design for weaker reasoning models: one item at a time, short fields, JSON output, no long free-form text.

## Required Fields Per Lead

Each lead must answer:

- This shows what: identify the concrete signal in the item.
- Who may pay: name the likely payer, buyer, sponsor, owner, regulator, or executor.
- Who to observe next: list two concrete entities or events.
- 30-day validation: one small action that can prove whether this is actionable.
- Do not do yet: one action to avoid before evidence improves.
- Consulting judgement: one specific commercial judgement tied to the item.

## Fixed Scoring

Score each dimension 0-5:

- Policy fit: region/industry/objective match and official policy alignment.
- Budget trace: procurement, tender, award, subsidy, funding, project investment, or named budget.
- Customer clarity: named owner, buyer, department, enterprise, park, platform company, or executor.
- 30-day loop possibility: can validate with a call, document, public list, tender follow-up, PoC, or small meeting within 30 days.
- Risk/noise deduction: subtract for rumor, vague planning, compliance-heavy work, financing uncertainty, litigation, unsafe outreach, or low-weight source.

Total score:

```text
total = policy_fit + budget_trace + customer_clarity + thirty_day_loop - risk_noise_deduction
```

Grade:

- A: 14 or above
- B: 10-13
- C: 6-9
- D: 5 or below

## Signal Interpretation

- Tender/procurement: look for buyer, budget, procurement number, project owner, candidate award, final award, and acceptance requirements.
- Policy/subsidy: look for主管部门、申报条件、截止日期、附件、企业名单、示范场景、财政资金.
- Investment promotion/park: look for carrier platform, land/energy/environment constraints, signed project, and follow-up implementation body.
- Competitor movement: look for pricing page changes, hiring spikes, new office, channel partner, product release, filing, award, or customer case.
- Funding/investment: look for investor identity, round/stage, use of funds, government fund participation, and industrial chain fit.
- Technical cooperation: look for scenario owner, PoC scope, compliance materials, data/interface access, and whether equipment investment is required.

Do not over-score an item just because it is recent. Recency only matters after source quality, payer clarity, and next validation event are present.

## MiniMax Prompt

Use this prompt for one item at a time. Require JSON only.

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

输出 JSON schema：
{
  "commercial_meaning": "这条说明什么，必须结合标题中的实体或项目类型",
  "likely_payer": "最可能付款/发起/采购的一方",
  "observe_next": ["接下来观察的实体或事件 1", "接下来观察的实体或事件 2"],
  "thirty_day_validation": "30 天内一个可执行验证动作",
  "do_not_do": "证据不足前暂时不要做的事",
  "consulting_judgement": "针对本条的具体咨询判断，必须出现实体、项目类型、付款方或执行方之一"
}
```

## Examples

Tender or construction:

```json
{
  "commercial_meaning": "某市公共资源交易中心发布的污水处理厂扩建招标说明建设资金和招采流程已启动。",
  "likely_payer": "项目业主或其政府平台公司",
  "observe_next": ["中标候选人公示", "总包和设备分包名单"],
  "thirty_day_validation": "查招标文件联系人和业主单位，确认是否需要验收资料、施工留痕或合规台账服务。",
  "do_not_do": "不要直接承诺接工程或垫资进场。",
  "consulting_judgement": "这类施工线索不适合直接接工程，适合倒推项目业主、总包和安装队，验证施工留痕、验收资料和台账外包需求。"
}
```

Policy:

```json
{
  "commercial_meaning": "工信部门发布试点申报通知，说明主管部门正在筛选企业名单和示范场景。",
  "likely_payer": "申报企业或承接申报服务的园区/平台公司",
  "observe_next": ["申报指南附件", "入围企业名单"],
  "thirty_day_validation": "核对申报条件和截止日期，找出本地 10 家可能符合条件的企业。",
  "do_not_do": "不要把政策通知当作立即成交信号。",
  "consulting_judgement": "这类政策线索不是马上成交信号，应该跟后续申报指南、主管部门答疑和企业名单，判断是否能做材料辅导或项目包装。"
}
```
