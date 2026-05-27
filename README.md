# Industry News Opportunity Radar

Universal Agent Skill for building client-specific news, policy, project, tender, park, competitor, and industry opportunity radars.

The canonical skill is:

```text
skills/industry-news-opportunity-radar/
```

It is agent-neutral: any agent can use the core `SKILL.md`, references, scripts, and examples. Platform-specific folders are adapters, not the source of truth.

## Install Options

### Any Agent Skills-Compatible Runtime

Copy this folder into the agent's skills directory:

```text
skills/industry-news-opportunity-radar/
```

### Paste-Only Agents

Use the flattened prompt:

```text
dist/industry-news-opportunity-radar.universal.md
```

### Codex

```text
$skill-installer install from GitHub repo LongChangPost/industry-news-opportunity-radar path skills/industry-news-opportunity-radar
```

After installation, restart Codex.

### Hermes / MiniMax

Use the adapter if the profile supports local skills:

```text
hermes/profiles/coco/skills/industry-news-opportunity-radar/SKILL.md
```

Or copy the canonical skill folder into the target Hermes profile's `skills/` directory.

## Test Prompt

```text
Use industry-news-opportunity-radar. First onboard this client, then generate radar_config, search queries, scored items, and a daily brief from the bundled examples. Client: enterprise sales team serving parks with digital project documentation services; region: Jiangsu and Zhejiang; industries: low-altitude economy and smart manufacturing; goals: policies, tenders, projects, technical cooperation; risk: internal observation only, no advance payment, avoid license-heavy work; output: daily local file, top 3, dedupe on.
```
