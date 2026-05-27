#!/usr/bin/env python3
"""Expand radar_config.json into source-specific search queries."""

from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path
from typing import Any


ACTION_WORDS = {
    "government": {
        "projects": ["项目", "开工", "签约", "建设"],
        "policies": ["政策", "申报", "补贴", "试点", "公示"],
        "technical_cooperation": ["揭榜挂帅", "场景征集", "技术合作"],
        "investment": ["基金", "投资", "融资", "招商"],
        "tenders": ["招标", "采购", "中标", "采购意向"],
        "competitors": ["公告", "名单", "示范"],
        "customers": ["企业名单", "供需对接", "场景清单"],
    },
    "enterprise": {
        "projects": ["项目合作", "合同", "中标"],
        "policies": ["入选", "试点", "补贴"],
        "technical_cooperation": ["战略合作", "联合实验室", "PoC"],
        "investment": ["融资", "投资", "产能"],
        "tenders": ["采购", "供应商", "中标"],
        "competitors": ["产品发布", "客户案例", "招聘", "价格"],
        "customers": ["合作伙伴", "客户案例", "采购"],
    },
    "park_association": {
        "projects": ["招商", "签约", "项目落地"],
        "policies": ["申报", "政策", "奖励"],
        "technical_cooperation": ["场景征集", "供需对接", "技术合作"],
        "investment": ["基金", "路演", "投融资"],
        "tenders": ["采购", "招标", "中标"],
        "competitors": ["会员动态", "企业动态", "榜单"],
        "customers": ["企业名录", "供需对接", "招商项目"],
    },
    "media": {
        "projects": ["项目", "签约", "开工"],
        "policies": ["政策", "试点", "名单"],
        "technical_cooperation": ["合作", "场景"],
        "investment": ["融资", "投资"],
        "tenders": ["招标", "中标"],
        "competitors": ["发布", "扩产", "合作"],
        "customers": ["客户", "订单"],
    },
    "self_media": {
        "projects": ["项目", "动向"],
        "policies": ["政策", "名单"],
        "technical_cooperation": ["合作", "场景"],
        "investment": ["融资", "投资"],
        "tenders": ["招标", "中标"],
        "competitors": ["爆料", "动向"],
        "customers": ["客户", "订单"],
    },
}


SOURCE_HINTS = {
    "government": ["site:gov.cn", "公共资源交易", "发改", "工信", "商务"],
    "enterprise": ["官网", "公告", "投资者关系"],
    "park_association": ["园区", "投促", "协会"],
    "media": ["新闻", "报道"],
    "self_media": ["低权重参考"],
}


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_json(path: str | Path, data: Any) -> None:
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def list_values(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if value:
        return [str(value).strip()]
    return []


def build_queries(config: dict[str, Any]) -> list[dict[str, Any]]:
    regions = list_values(config.get("regions", {}).get("primary")) or ["全国"]
    industries = (
        list_values(config.get("industries", {}).get("primary"))
        + list_values(config.get("industries", {}).get("upstream_downstream"))
    ) or ["产业"]
    objectives = list_values(config.get("objectives")) or ["projects", "policies"]
    freshness_days = int(config.get("collection", {}).get("freshness_days", 7) or 7)
    query_budget = int(config.get("collection", {}).get("query_budget_per_run", 30) or 30)
    source_types = [source.get("type", "media") for source in config.get("sources", [])]
    source_types = list(dict.fromkeys(source_types)) or ["government", "enterprise", "park_association", "media"]

    rows_by_type: dict[str, list[dict[str, Any]]] = {}
    for source_type in source_types:
        source_actions = ACTION_WORDS.get(source_type, ACTION_WORDS["media"])
        hints = SOURCE_HINTS.get(source_type, [])
        rows_by_type[source_type] = []
        for region, industry, objective in product(regions, industries, objectives):
            actions = source_actions.get(objective, ["项目"])
            for action in actions[:3]:
                terms = [region, industry, action]
                if source_type == "government":
                    terms.append(f"({hints[0]} OR {hints[1]})")
                elif hints:
                    terms.append(hints[0])
                query = " ".join(term for term in terms if term)
                rows_by_type[source_type].append(
                    {
                        "source_type": source_type,
                        "objective": objective,
                        "region": region,
                        "industry": industry,
                        "query": query,
                        "freshness_days": freshness_days,
                        "priority": 1 if source_type == "government" else 2 if source_type == "enterprise" else 3,
                        "primary_source_required": source_type in {"government", "enterprise", "park_association"},
                    }
                )

    priority_order = sorted(source_types, key=lambda stype: (1 if stype == "government" else 2 if stype == "enterprise" else 3, stype))
    selected: list[dict[str, Any]] = []
    index = 0
    while len(selected) < query_budget:
        added = False
        for source_type in priority_order:
            bucket = rows_by_type.get(source_type, [])
            if index < len(bucket):
                selected.append(bucket[index])
                added = True
                if len(selected) >= query_budget:
                    break
        if not added:
            break
        index += 1
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description="Build search_queries.json from radar_config.json.")
    parser.add_argument("config", help="Path to radar_config.json")
    parser.add_argument("--output", "-o", default="search_queries.json", help="Output path")
    args = parser.parse_args()

    config = load_json(args.config)
    queries = build_queries(config)
    save_json(args.output, {"queries": queries})
    print(json.dumps({"queries": queries}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
