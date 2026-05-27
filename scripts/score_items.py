#!/usr/bin/env python3
"""Score radar items without network or model calls."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


BUDGET_WORDS = ["招标", "采购", "中标", "预算", "资金", "补贴", "申报", "投资", "建设", "改造", "合同"]
CUSTOMER_WORDS = ["公司", "集团", "局", "委", "厅", "园区", "平台", "中心", "政府", "业主", "采购人"]
LOOP_WORDS = ["公告", "公示", "指南", "名单", "征集", "试点", "申报", "招标", "中标", "揭榜挂帅", "验收"]
RISK_WORDS = ["传闻", "网传", "处罚", "诉讼", "亏损", "投诉", "违法", "不确定", "暂定", "许可证", "牌照", "制裁"]

SOURCE_TYPE_WEIGHT = {
    "government": 5,
    "enterprise": 4,
    "park_association": 3,
    "media": 2,
    "self_media": 1,
}

PRIMARY_SOURCE_TYPES = {"government", "enterprise"}


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_json(path: str | Path, data: Any) -> None:
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def as_items(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        return data["items"]
    if isinstance(data, list):
        return data
    raise ValueError("items JSON must be a list or an object with an items list")


def text_of(item: dict[str, Any]) -> str:
    fields = [
        item.get("title", ""),
        item.get("summary", ""),
        item.get("content", ""),
        item.get("source", ""),
        item.get("region", ""),
        item.get("industry", ""),
        " ".join(item.get("entities", []) if isinstance(item.get("entities"), list) else []),
    ]
    return " ".join(str(field) for field in fields if field)


def count_matches(words: list[str], text: str) -> int:
    return sum(1 for word in words if word and word in text)


def clamp(value: int) -> int:
    return max(0, min(5, value))


def source_type(item: dict[str, Any]) -> str:
    explicit = str(item.get("source_type", "")).strip()
    if explicit:
        return explicit
    source = str(item.get("source", "")) + " " + str(item.get("url", ""))
    if any(word in source for word in ["gov.cn", "政府", "发改", "工信", "商务", "自然资源", "公共资源"]):
        return "government"
    if any(word in source for word in ["公告", "投资者关系", "股份", "集团", "公司官网"]):
        return "enterprise"
    if any(word in source for word in ["园区", "投促", "协会"]):
        return "park_association"
    if any(word in source for word in ["微信", "公众号", "自媒体"]):
        return "self_media"
    return "media"


def match_any(values: list[str], text: str) -> int:
    return sum(1 for value in values if value and value in text)


def scoring_result(item: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    text = text_of(item)
    stype = source_type(item)
    regions = config.get("regions", {}).get("primary", []) + config.get("regions", {}).get("secondary", [])
    industries = config.get("industries", {}).get("primary", []) + config.get("industries", {}).get("upstream_downstream", [])
    objectives = config.get("objectives", [])

    policy_fit = clamp(match_any(regions, text) + match_any(industries, text) + (1 if stype == "government" else 0))
    if "policies" in objectives and any(word in text for word in ["政策", "申报", "补贴", "试点"]):
        policy_fit = clamp(policy_fit + 1)

    budget_trace = clamp(count_matches(BUDGET_WORDS, text))
    customer_clarity = clamp(count_matches(CUSTOMER_WORDS, text) + min(2, len(item.get("entities", []) or [])))
    thirty_day_loop = clamp(count_matches(LOOP_WORDS, text))
    risk_noise_deduction = clamp(count_matches(RISK_WORDS, text) + (1 if stype == "self_media" else 0))
    if stype == "media" and config.get("collection", {}).get("cross_check_media_items", True):
        risk_noise_deduction = clamp(risk_noise_deduction + 1)
    total = policy_fit + budget_trace + customer_clarity + thirty_day_loop - risk_noise_deduction
    grade = "A" if total >= 14 else "B" if total >= 10 else "C" if total >= 6 else "D"
    primary_source_required = config.get("collection", {}).get("primary_source_required_for_a_grade", True)
    if primary_source_required and grade == "A" and stype not in PRIMARY_SOURCE_TYPES:
        grade = "B"
    has_url = bool(str(item.get("url", "")).strip())
    if stype in PRIMARY_SOURCE_TYPES and has_url:
        evidence_level = "primary_official"
    elif stype == "park_association" and has_url:
        evidence_level = "primary_industry"
    elif stype == "media":
        evidence_level = "secondary_media"
    else:
        evidence_level = "low_confidence"
    return {
        "policy_fit": policy_fit,
        "budget_trace": budget_trace,
        "customer_clarity": customer_clarity,
        "thirty_day_loop": thirty_day_loop,
        "risk_noise_deduction": risk_noise_deduction,
        "source_weight": SOURCE_TYPE_WEIGHT.get(stype, 1),
        "source_type": stype,
        "evidence_level": evidence_level,
        "confirmation_required": evidence_level in {"secondary_media", "low_confidence"},
        "total": total,
        "grade": grade,
    }


def first_entity(item: dict[str, Any]) -> str:
    entities = item.get("entities")
    if isinstance(entities, list) and entities:
        return str(entities[0])
    title = str(item.get("title", ""))
    match = re.search(r"([\u4e00-\u9fa5A-Za-z0-9]+(?:公司|集团|局|委|厅|园区|中心|政府|平台))", title)
    if match:
        return match.group(1)
    return str(item.get("source", "该来源"))


def project_type(item: dict[str, Any]) -> str:
    text = text_of(item)
    for word in ["技术合作", "招标", "采购", "中标", "申报", "补贴", "试点", "签约", "产能", "建设", "改造"]:
        if word in text:
            return word
    return "产业动态"


def likely_payer(item: dict[str, Any], score: dict[str, Any]) -> str:
    if item.get("payer"):
        return str(item["payer"])
    if item.get("buyer"):
        return str(item["buyer"])
    entity = first_entity(item)
    if score["source_type"] == "government":
        return f"{entity}或其主管/平台单位"
    if score["source_type"] == "enterprise":
        return f"{entity}或其采购/战略部门"
    return f"{entity}相关业主方"


def deterministic_analysis(item: dict[str, Any], score: dict[str, Any]) -> dict[str, Any]:
    title = str(item.get("title", "未命名线索"))
    entity = first_entity(item)
    ptype = project_type(item)
    payer = likely_payer(item, score)

    if ptype in ["招标", "采购", "中标", "建设", "改造"]:
        judgement = f"{title}属于{ptype}线索，先不要直接接工程，优先倒推{payer}、总包/分包和验收资料需求。"
        validation = f"30 天内核对{entity}招采文件、联系人和中标/候选公告，确认是否存在资料整理、台账或交付留痕需求。"
        do_not = "不要垫资进场或承诺承包施工。"
    elif ptype in ["申报", "补贴", "试点"]:
        judgement = f"{title}更像政策筛选信号，{payer}可能围绕申报材料、企业名单和示范场景付费。"
        validation = f"30 天内跟{entity}后续指南、答疑和入围名单，筛出可服务的企业或园区。"
        do_not = "不要把通知当作已经成交的项目。"
    elif ptype == "技术合作":
        judgement = f"{title}说明{entity}的技术合作需求已外溢，先做合规资料、台账和 PoC 场景，不碰重资产设备投资。"
        validation = f"30 天内确认{entity}合作方向、接口人和试点场景，形成一个低成本 PoC 清单。"
        do_not = "不要先投设备或承诺排他合作。"
    else:
        judgement = f"{title}显示{entity}出现{ptype}信号，适合作为观察入口，先验证付款方和30天内可交付的小闭环。"
        validation = f"30 天内查{entity}后续公告、联系人和上下游响应，确认是否有明确预算或采购动作。"
        do_not = "不要在付款方不清楚时启动重交付。"

    return {
        "commercial_meaning": f"{title}显示{entity}出现{ptype}信号，来源权重为{score['source_weight']}。",
        "likely_payer": payer,
        "observe_next": [f"{entity}后续公告", "中标/名单/合作方变化"],
        "thirty_day_validation": validation,
        "do_not_do": do_not,
        "consulting_judgement": judgement,
    }


def analysis_prompt(config: dict[str, Any], item: dict[str, Any], score: dict[str, Any]) -> str:
    compact_config = {
        "client": config.get("client", {}),
        "regions": config.get("regions", {}),
        "industries": config.get("industries", {}),
        "objectives": config.get("objectives", []),
        "risk_limits": config.get("risk_limits", {}),
    }
    payload = {
        "radar_config": compact_config,
        "item": item,
        "scoring_result": score,
        "output_schema": {
            "commercial_meaning": "",
            "likely_payer": "",
            "observe_next": [],
            "thirty_day_validation": "",
            "do_not_do": "",
            "consulting_judgement": "",
        },
    }
    return "只分析 1 条线索，输出 JSON，不要 Markdown。必须引用标题或来源里的具体实体、项目类型、付款方或执行方。\n" + json.dumps(payload, ensure_ascii=False)


def score_items(items: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for item in items:
        result = scoring_result(item, config)
        analysis = deterministic_analysis(item, result)
        enriched = dict(item)
        enriched["scoring_result"] = result
        enriched["analysis"] = analysis
        enriched["analysis_prompt"] = analysis_prompt(config, item, result)
        scored.append(enriched)
    return scored


def main() -> int:
    parser = argparse.ArgumentParser(description="Score radar items without network or model calls.")
    parser.add_argument("items", help="Path to items.json")
    parser.add_argument("--config", required=True, help="Path to radar_config.json")
    parser.add_argument("--output", "-o", default="scored_items.json", help="Output path")
    args = parser.parse_args()

    items = as_items(load_json(args.items))
    config = load_json(args.config)
    scored = score_items(items, config)
    save_json(args.output, {"items": scored})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
