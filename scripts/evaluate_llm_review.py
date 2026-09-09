#!/usr/bin/env python3
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENT_LEVEL_TYPES = {"ambiguous_requirement", "context_contradiction"}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalized_key(f):
    """Type-specific semantic key.

    Requirement-level findings intentionally ignore test_id so the same requirement
    problem is not counted as both FP and FN merely because the reviewer attached a
    test reference.
    """
    ftype = f.get("type")
    req = f.get("requirement_id")
    test = None if ftype in REQUIREMENT_LEVEL_TYPES else f.get("test_id")
    return (ftype, req, test)


def exact_key(f):
    return (f.get("type"), f.get("requirement_id"), f.get("test_id"))


def _metrics(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {"tp":tp,"fp":fp,"fn":fn,"precision":round(precision,4),"recall":round(recall,4),"f1":round(f1,4)}


def evaluate(ground_truth, prediction):
    observable_gt = [g for g in ground_truth if g.get("observable", True)]
    unobservable_gt = [g for g in ground_truth if not g.get("observable", True)]

    gt_map = {normalized_key(x): x for x in observable_gt}
    pred_map = {}
    for p in prediction:
        pred_map.setdefault(normalized_key(p), p)

    matched_keys = sorted(set(gt_map) & set(pred_map), key=str)
    missed_keys = sorted(set(gt_map) - set(pred_map), key=str)
    discovery_keys = sorted(set(pred_map) - set(gt_map), key=str)

    # v0.4 benchmark deliberately does not call unmatched open-ended findings false positives.
    # They require human/domain-expert adjudication first.
    benchmark = {
        "observable_targets": len(gt_map),
        "hits": len(matched_keys),
        "misses": len(missed_keys),
        "recall": round(len(matched_keys) / len(gt_map), 4) if gt_map else 0.0,
        "matched_keys": matched_keys,
        "missed_keys": missed_keys,
        "unobservable_ground_truth": [normalized_key(x) for x in unobservable_gt],
    }

    discovery = {
        "candidate_count": len(discovery_keys),
        "candidate_keys": discovery_keys,
        "precision_status": "requires_human_or_domain_expert_adjudication",
    }

    # Preserve legacy exact-match metrics only as a diagnostic / comparability view.
    exact_gt = {exact_key(x) for x in observable_gt}
    exact_pred = {exact_key(x) for x in prediction}
    legacy_tp = len(exact_gt & exact_pred)
    legacy_fp = len(exact_pred - exact_gt)
    legacy_fn = len(exact_gt - exact_pred)

    return {
        "evaluation_contract_version":"0.4",
        "benchmark": benchmark,
        "discovery": discovery,
        "legacy_exact_match_diagnostic": _metrics(legacy_tp, legacy_fp, legacy_fn),
        "notes":[
            "Requirement-level findings ignore test_id during benchmark matching.",
            "Only observable ground-truth defects are benchmark targets.",
            "Unmatched open-ended findings are Discovery candidates, not automatic false positives.",
            "Discovery precision is calculated only after expert/human adjudication."
        ]
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prediction", default=str(ROOT / "findings" / "llm_review_openai.json"))
    parser.add_argument("--ground-truth", default=str(ROOT / "evidence" / "ground_truth_findings.json"))
    parser.add_argument("--output", default=str(ROOT / "evidence" / "llm_evaluation_v0.4.json"))
    args = parser.parse_args()

    gt = load_json(args.ground_truth)
    pred_obj = load_json(args.prediction)
    pred = pred_obj["findings"] if isinstance(pred_obj, dict) else pred_obj
    result = evaluate(gt, pred)
    Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")

    b=result["benchmark"]; d=result["discovery"]
    print(f"Benchmark: hits={b['hits']}/{b['observable_targets']} misses={b['misses']} recall={b['recall']:.3f}")
    print(f"Discovery candidates: {d['candidate_count']} (precision requires human/expert adjudication)")
    print(f"Saved: {Path(args.output).relative_to(ROOT) if Path(args.output).is_relative_to(ROOT) else args.output}")

if __name__ == "__main__":
    main()
