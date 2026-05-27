# Coco / Hermes / MiniMax Install + Test

## Install Directive For Coco

把下面这个文件安装到 Coco 的 Hermes profile：

Source in repo:
`hermes/profiles/coco/skills/industry-news-opportunity-radar/SKILL.md`

Target path, if Coco follows the standard Hermes profile layout:
`~/.hermes/profiles/coco/skills/industry-news-opportunity-radar/SKILL.md`

If Coco's profile name is not `coco`, use its real profile directory and keep the skill folder name:
`industry-news-opportunity-radar`.

Do not install it as a Codex skill. Do not use `$skill-installer`. Coco is Hermes + MiniMax.

## Smoke Test Prompt For Coco

```text
使用 industry-news-opportunity-radar 能力。

先不要联网搜索。先用 onboarding 流程问我配置问题；然后基于以下客户信息，产出 radar_config、search_queries、scored_items 和一份日报简报：

客户：企业销售团队，做园区数字化和项目资料服务
区域：江苏、浙江
行业：低空经济、智能制造、园区数字化、工程资料管理
目标：找政策、找项目、找招投标、找技术合作
风险：只做内部观察，不垫资，不碰牌照或重合规业务
输出：日报，本地 Markdown，top 3，必须查重，只推新增

用这 3 条样例线索测试，不要编造新链接：
1. 标题：苏州市低空经济示范区无人机起降点建设项目招标公告；来源：苏州市公共资源交易中心；source_type：government；链接：https://example.gov.cn/suzhou-low-altitude-tender；摘要：项目建设内容包括起降点、配套管理系统和验收资料，采购人是示范区建设管理中心。
2. 标题：浙江省经信厅发布智能制造试点示范申报通知；来源：浙江省经济和信息化厅；source_type：government；链接：https://example.gov.cn/zhejiang-smart-manufacturing-policy；摘要：通知要求企业提交数字化改造场景、项目投资证明和验收材料。
3. 标题：某产业园发布低空物流技术合作需求征集；来源：杭州某产业园投资促进中心；source_type：park_association；链接：https://example.com/hangzhou-park-low-altitude-cooperation；摘要：园区面向企业征集低空物流试点场景，要求提供合规资料和 PoC 方案。

验收标准：
1. 必须先问客户问题，不能直接搜索。
2. 必须输出 radar_config JSON。
3. 必须输出 source-specific search_queries JSON。
4. 必须输出 scored_items，且包含 policy_fit、budget_trace、customer_clarity、thirty_day_loop、risk_noise_deduction、total、grade、evidence_level。
5. 日报必须从“## 今日内部关注”开始。
6. 每条日报必须包含：标题、产业/主题、级别/分数/风险、切入、内部观察、咨询判断、链接。
7. 咨询判断必须引用具体实体、项目类型、付款方或执行方，不能写空泛趋势话。
8. 必须说明 sent_history 只有发送成功后才写入，测试 run 不写入。
9. 最后输出 PASS 或 FAIL，以及失败原因。
```
