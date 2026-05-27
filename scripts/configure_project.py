#!/usr/bin/env python3
"""Create radar_config.json from onboarding answers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


CLIENT_TYPE_MAP = {
    "企业": "enterprise",
    "个人": "individual",
    "政府": "government_park",
    "园区": "government_park",
    "投资人": "investor",
    "咨询顾问": "consultant",
    "顾问": "consultant",
    "销售团队": "sales_team",
    "销售": "sales_team",
}

OBJECTIVE_MAP = {
    "找客户": "customers",
    "客户": "customers",
    "找项目": "projects",
    "项目": "projects",
    "找政策": "policies",
    "政策": "policies",
    "技术合作": "technical_cooperation",
    "合作": "technical_cooperation",
    "投资机会": "investment",
    "投资": "investment",
    "招投标": "tenders",
    "招标": "tenders",
    "投标": "tenders",
    "竞品": "competitors",
}


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, bool):
        return [str(value).lower()]
    text = str(value).replace("，", ",").replace("、", ",").replace("；", ",")
    return [part.strip() for part in text.split(",") if part.strip()]


def first_answer(data: dict[str, Any], *names: str, default: Any = "") -> Any:
    for name in names:
        if name in data and data[name] not in (None, ""):
            return data[name]
    return default


def infer_client_type(text: str) -> str:
    for key, value in CLIENT_TYPE_MAP.items():
        if key in text:
            return value
    return "other"


def infer_objectives(raw: Any) -> list[str]:
    text = " ".join(as_list(raw))
    found: list[str] = []
    for key, value in OBJECTIVE_MAP.items():
        if key in text and value not in found:
            found.append(value)
    return found or ["projects", "policies"]


def yes_no(text: str, default: bool) -> bool:
    if not text:
        return default
    lowered = text.lower()
    if any(word in lowered for word in ["yes", "true", "允许", "可以", "要", "需要"]):
        return True
    if any(word in lowered for word in ["no", "false", "不", "否", "只观察"]):
        return False
    return default


def source_keywords(regions: list[str], industries: list[str], objectives: list[str]) -> list[str]:
    base = regions + industries
    objective_words = {
        "customers": ["客户", "企业名单", "供需对接"],
        "projects": ["项目", "开工", "签约"],
        "policies": ["政策", "申报", "补贴"],
        "technical_cooperation": ["技术合作", "揭榜挂帅", "试点"],
        "investment": ["融资", "投资", "基金"],
        "tenders": ["招标", "采购", "中标"],
        "competitors": ["公告", "产能", "合作"],
    }
    words: list[str] = []
    for objective in objectives:
        words.extend(objective_words.get(objective, []))
    return list(dict.fromkeys(base + words))


def build_sources(regions: list[str], industries: list[str], objectives: list[str]) -> list[dict[str, Any]]:
    keywords = source_keywords(regions, industries, objectives)
    return [
        {
            "name": "政府官网/主管部门/公共资源交易",
            "type": "government",
            "priority": 1,
            "base_url": "",
            "query_keywords": keywords + ["发改", "工信", "商务", "自然资源", "公共资源交易"],
        },
        {
            "name": "企业官网/上市公司公告",
            "type": "enterprise",
            "priority": 2,
            "base_url": "",
            "query_keywords": keywords + ["公告", "投资者关系", "项目合作"],
        },
        {
            "name": "园区/投促/行业协会",
            "type": "park_association",
            "priority": 3,
            "base_url": "",
            "query_keywords": keywords + ["园区", "招商", "协会", "供需"],
        },
        {
            "name": "主流媒体",
            "type": "media",
            "priority": 4,
            "base_url": "",
            "query_keywords": keywords,
        },
        {
            "name": "自媒体低权重线索",
            "type": "self_media",
            "priority": 5,
            "base_url": "",
            "query_keywords": keywords,
        },
    ]


def freshness_days(frequency: str, raw_value: Any) -> int:
    try:
        return int(str(raw_value).replace("天", "").strip())
    except (TypeError, ValueError):
        pass
    if frequency == "monthly":
        return 30
    if frequency == "weekly":
        return 14
    return 7


def build_config(answers: dict[str, Any]) -> dict[str, Any]:
    client_text = str(first_answer(answers, "client", "客户是谁", "客户", default=""))
    client_type = str(first_answer(answers, "client_type", "客户类型", default="")) or infer_client_type(client_text)
    regions = as_list(first_answer(answers, "regions", "关注区域", "区域", default=[]))
    primary_industries = as_list(first_answer(answers, "primary_industries", "主行业", "关注行业", default=[]))
    upstream_downstream = as_list(first_answer(answers, "upstream_downstream", "上下游", default=[]))
    paused = as_list(first_answer(answers, "paused_industries", "暂缓行业", default=[]))
    excluded = as_list(first_answer(answers, "excluded_industries", "排除行业", default=[]))
    objectives = infer_objectives(first_answer(answers, "objectives", "目标", default=[]))
    risk_text = str(first_answer(answers, "risk_limits", "风险边界", default=""))
    frequency = str(first_answer(answers, "frequency", "输出频率", default="daily")).strip() or "daily"
    channels = as_list(first_answer(answers, "channels", "输出渠道", default=["local_file"])) or ["local_file"]
    top_n_raw = first_answer(answers, "top_n", "简报长度", "每期条数", default=5)
    try:
        top_n = int(str(top_n_raw).replace("条", "").replace("top", "").strip())
    except ValueError:
        top_n = 5
    dedupe_text = str(first_answer(answers, "dedupe", "是否查重", default="是"))
    dedupe_enabled = yes_no(dedupe_text, True)
    freshness = freshness_days(frequency, first_answer(answers, "freshness_days", "信息时间窗口", default=""))

    config = {
        "client": {
            "name": str(first_answer(answers, "client_name", "客户名称", default=client_text or "未命名客户")),
            "type": client_type,
            "profile": client_text,
        },
        "regions": {
            "primary": regions,
            "secondary": as_list(first_answer(answers, "secondary_regions", "次级区域", default=[])),
            "excluded": as_list(first_answer(answers, "excluded_regions", "排除区域", default=[])),
            "overseas": any(word in " ".join(regions) for word in ["海外", "东南亚", "欧洲", "美国", "日本"]),
        },
        "industries": {
            "primary": primary_industries,
            "upstream_downstream": upstream_downstream,
            "paused": paused,
            "excluded": excluded,
        },
        "objectives": objectives,
        "risk_limits": {
            "outreach_allowed": yes_no(risk_text, False) and "只做内部" not in risk_text,
            "internal_observation_only": "只做内部" in risk_text or "内部观察" in risk_text,
            "no_advance_payment": "垫资" in risk_text or "不垫资" in risk_text or True,
            "avoid_license_or_compliance_heavy": any(word in risk_text for word in ["牌照", "合规", "许可"]),
            "notes": as_list(risk_text),
        },
        "output": {
            "frequency": frequency,
            "channels": channels,
            "top_n": top_n,
            "language": "zh-CN",
        },
        "dedupe": {
            "enabled": dedupe_enabled,
            "only_new": dedupe_enabled,
            "history_path": "sent_history.json",
        },
        "collection": {
            "freshness_days": freshness,
            "primary_source_required_for_a_grade": True,
            "cross_check_media_items": True,
            "query_budget_per_run": 30,
        },
        "sources": build_sources(regions, primary_industries + upstream_downstream, objectives),
        "query_sets": [
            {
                "name": "核心机会",
                "keywords": source_keywords(regions, primary_industries + upstream_downstream, objectives),
                "regions": regions,
                "source_types": ["government", "enterprise", "park_association"],
            }
        ],
    }
    return config


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate radar_config.json from onboarding answers.")
    parser.add_argument("answers", nargs="?", help="Path to answers.json")
    parser.add_argument("--output", "-o", default="radar_config.json", help="Output config path")
    args = parser.parse_args()

    if args.answers:
        answers = json.loads(Path(args.answers).read_text(encoding="utf-8"))
    else:
        answers = {
            "client": "企业销售团队",
            "regions": ["江苏", "浙江"],
            "primary_industries": ["低空经济"],
            "objectives": ["找项目", "招投标", "政策"],
            "risk_limits": "只做内部观察，不垫资，不碰牌照重合规业务",
            "frequency": "daily",
            "channels": ["local_file"],
            "top_n": 5,
            "dedupe": "是",
        }
    config = build_config(answers)
    output_path = Path(args.output)
    output_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(config, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
