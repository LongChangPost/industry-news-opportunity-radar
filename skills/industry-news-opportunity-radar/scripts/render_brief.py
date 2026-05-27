#!/usr/bin/env python3
"""Render Markdown radar briefs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from score_items import as_items, load_json, score_items  # noqa: E402


PHASE_PRIORITY = {
    "中标结果": 5,
    "中标": 5,
    "候选": 4,
    "招标公告": 3,
    "采购公告": 3,
    "招标计划": 2,
    "采购意向": 2,
}


def save_text(path: str | Path, text: str) -> None:
    Path(path).write_text(text, encoding="utf-8")


def normalize_title(title: str) -> str:
    text = re.sub(r"\s+", "", title.lower())
    for word in ["招标计划", "招标公告", "采购公告", "采购意向", "中标候选人公示", "中标结果公告", "中标公告"]:
        text = text.replace(word, "")
    return text


def item_key(item: dict[str, Any]) -> str:
    url = str(item.get("url", "")).strip()
    if url:
        return "url:" + url
    raw = normalize_title(str(item.get("title", ""))) + "|" + str(item.get("source", ""))
    return "hash:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def lifecycle_key(item: dict[str, Any]) -> str:
    explicit = str(item.get("lifecycle_project_id", "")).strip()
    if explicit:
        return "life:" + explicit
    project_name = str(item.get("project_name", "")).strip()
    if project_name:
        return "life:" + normalize_title(project_name)
    return item_key(item)


def phase_score(item: dict[str, Any]) -> int:
    text = str(item.get("lifecycle_stage", "")) + " " + str(item.get("title", ""))
    return max((score for phase, score in PHASE_PRIORITY.items() if phase in text), default=1)


def load_history(path: str | Path) -> set[str]:
    p = Path(path)
    if not p.exists():
        return set()
    data = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return set(data.get("sent_keys", []))
    if isinstance(data, list):
        return set(str(item) for item in data)
    return set()


def write_history(path: str | Path, existing: set[str], new_keys: list[str]) -> None:
    merged = sorted(existing.union(new_keys))
    Path(path).write_text(json.dumps({"sent_keys": merged}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def dedupe_items(items: list[dict[str, Any]], history: set[str]) -> list[dict[str, Any]]:
    by_lifecycle: dict[str, dict[str, Any]] = {}
    for item in items:
        key = lifecycle_key(item)
        if item_key(item) in history or key in history:
            continue
        previous = by_lifecycle.get(key)
        if previous is None or phase_score(item) >= phase_score(previous):
            merged = dict(item)
            events = []
            if previous:
                events.extend(previous.get("lifecycle_events", []))
                events.append({"title": previous.get("title", ""), "url": previous.get("url", "")})
            events.extend(item.get("lifecycle_events", []))
            if events:
                merged["lifecycle_events"] = events
            by_lifecycle[key] = merged
    return list(by_lifecycle.values())


def ensure_scored(items: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    if all("scoring_result" in item and "analysis" in item for item in items):
        return items
    return score_items(items, config)


def score_sort_key(item: dict[str, Any]) -> tuple[int, int]:
    score = item.get("scoring_result", {})
    return (int(score.get("total", 0)), int(score.get("source_weight", 0)))


def risk_label(score: dict[str, Any]) -> str:
    deduction = int(score.get("risk_noise_deduction", 0))
    if deduction >= 4:
        return "高"
    if deduction >= 2:
        return "中"
    return "低"


def item_topic(item: dict[str, Any]) -> str:
    industry = str(item.get("industry", "")).strip()
    topic = str(item.get("topic", "")).strip()
    if industry and topic:
        return f"{industry}/{topic}"
    return industry or topic or "未分类"


def render_item(index: int, item: dict[str, Any]) -> str:
    score = item.get("scoring_result", {})
    analysis = item.get("analysis", {})
    title = str(item.get("title", "未命名线索"))
    grade = score.get("grade", "C")
    total = score.get("total", 0)
    risk = risk_label(score)
    cut_in = analysis.get("thirty_day_validation") or item.get("cut_in") or "30 天内验证付款方、预算和执行方。"
    internal = analysis.get("commercial_meaning") or item.get("summary") or "需补充来源信息。"
    judgement = analysis.get("consulting_judgement") or "本条缺少咨询判断，需补齐实体、付款方和30天验证动作。"
    url = item.get("url") or "无链接"
    return "\n".join(
        [
            f"### {index}. {title}",
            f"- 产业/主题：{item_topic(item)}",
            f"- 级别/分数/风险：{grade} / {total}/20 / {risk}",
            f"- 切入：{cut_in}",
            f"- 内部观察：{internal}",
            f"- 咨询判断：{judgement}",
            f"- 链接：{url}",
        ]
    )


def render_brief(items: list[dict[str, Any]], config: dict[str, Any], top_n: int | None) -> tuple[str, list[str]]:
    default_top = int(config.get("output", {}).get("top_n", 5) or 5)
    limit = top_n if top_n is not None else default_top
    ordered = sorted(items, key=score_sort_key, reverse=True)
    selected = ordered if limit <= 0 else ordered[:limit]
    lines = ["## 今日内部关注", ""]
    if not selected:
        lines.append("今日无新增高价值线索。")
    else:
        for idx, item in enumerate(selected, start=1):
            lines.append(render_item(idx, item))
            lines.append("")
    keys = [item_key(item) for item in selected] + [lifecycle_key(item) for item in selected]
    return "\n".join(lines).rstrip() + "\n", keys


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Markdown radar brief.")
    parser.add_argument("items", help="Path to items.json or scored_items.json")
    parser.add_argument("--config", required=True, help="Path to radar_config.json")
    parser.add_argument("--top", type=int, default=None, help="Keep top N items; 0 means all")
    parser.add_argument("--no-dedupe", action="store_true", help="Do not filter sent history or merge lifecycle leads")
    parser.add_argument("--mark-sent", action="store_true", help="Write sent history after render success")
    parser.add_argument("--no-mark-sent", action="store_true", help="Explicit dry run; do not write sent history")
    parser.add_argument("--history", default=None, help="Path to sent_history.json")
    parser.add_argument("--output", "-o", default="-", help="Output Markdown path or '-' for stdout")
    args = parser.parse_args()

    config = load_json(args.config)
    raw_items = as_items(load_json(args.items))
    items = ensure_scored(raw_items, config)
    history_path = args.history or config.get("dedupe", {}).get("history_path", "sent_history.json")
    history = set() if args.no_dedupe else load_history(history_path)
    filtered = items if args.no_dedupe else dedupe_items(items, history)
    markdown, keys = render_brief(filtered, config, args.top)

    if args.output == "-":
        print(markdown, end="")
    else:
        save_text(args.output, markdown)

    if args.mark_sent and not args.no_mark_sent:
        write_history(history_path, history, keys)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
