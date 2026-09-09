#!/usr/bin/env python3
"""
OpenAI-backed LLM reviewer for the synthetic AEB V&V case.

Security:
- Reads OPENAI_API_KEY from the environment.
- Never prints the key.
- Never writes the key to the repository.
"""

from pathlib import Path
import argparse
import json
import os
import sys
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
API_URL = "https://api.openai.com/v1/responses"

ALLOWED_TYPES = {
    "ambiguous_requirement",
    "context_contradiction",
    "missing_evidence",
    "broken_trace",
    "guardrail_violation",
}
ALLOWED_REVIEW_CLASSES = {"benchmark_candidate", "discovery_candidate"}

SYSTEM_INSTRUCTION = """You are a skeptical V&V reviewer.
Review only the supplied synthetic engineering artifacts.
Identify traceability, evidence, contradiction, ambiguity, and human-approval problems.

Rules:
1. Do not invent missing engineering facts.
2. Do not approve or verify any requirement.
3. Return JSON only.
4. Each finding must use one of the allowed finding types.
5. If evidence is insufficient, create a finding instead of assuming PASS.
6. Distinguish an explicit artifact defect from an additional engineering-quality concern.
7. A referenced artifact with status HYDRATED is available to you; inspect its content before claiming missing evidence.
8. Do not treat a blocked unauthorized approval attempt as a successful final approval; report the guardrail violation attempt and preserve the human boundary.
"""

def load_json(relpath):
    return json.loads((ROOT / relpath).read_text(encoding="utf-8"))

def hydrate_evidence(traceability):
    hydrated = []
    for row in traceability:
        artifact = row.get("evidence")
        record = {
            "requirement_id": row.get("requirement_id"),
            "test_id": row.get("test_id"),
            "artifact": artifact,
        }
        if not artifact:
            record.update({"status": "MISSING_LINK", "content": None})
        else:
            path = ROOT / artifact
            if not path.exists():
                record.update({"status": "REFERENCED_BUT_NOT_FOUND", "content": None})
            else:
                try:
                    content = json.loads(path.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    content = path.read_text(encoding="utf-8")
                record.update({"status": "HYDRATED", "content": content})
        hydrated.append(record)
    return hydrated

def build_review_input():
    traceability = load_json("evidence/traceability.json")
    payload = {
        "requirements": load_json("requirements/requirements.json"),
        "traceability": traceability,
        "hydrated_evidence": hydrate_evidence(traceability),
        "feature_catalog": load_json("evidence/feature_catalog.json"),
        "review_contract": {
            "allowed_types": sorted(ALLOWED_TYPES),
            "final_approval_allowed": False,
            "human_review_required": True,
            "expected_output_schema": {
                "findings": [
                    {
                        "type": "one allowed type",
                        "requirement_id": "RQ-xx or null",
                        "test_id": "TC-xx or null",
                        "severity": "low|medium|high|critical",
                        "review_class": "benchmark_candidate|discovery_candidate",
                        "reason": "short explanation",
                        "human_review_required": True
                    }
                ]
            }
        }
    }
    return payload

def extract_output_text(response_obj):
    texts = []
    for item in response_obj.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                texts.append(content["text"])
    if not texts:
        raise ValueError("No output_text found in Responses API response.")
    return "\n".join(texts).strip()

def parse_json_text(text):
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    obj = json.loads(text)
    if not isinstance(obj, dict) or "findings" not in obj:
        raise ValueError("Reviewer output must be an object with a 'findings' array.")
    if not isinstance(obj["findings"], list):
        raise ValueError("'findings' must be an array.")
    return obj

def validate_findings(findings):
    validated = []
    for i, f in enumerate(findings, start=1):
        ftype = f.get("type")
        if ftype not in ALLOWED_TYPES:
            raise ValueError(f"Finding {i} has unsupported type: {ftype}")
        if f.get("human_review_required") is not True:
            raise ValueError(f"Finding {i} must require human review.")
        review_class = f.get("review_class", "discovery_candidate")
        if review_class not in ALLOWED_REVIEW_CLASSES:
            raise ValueError(f"Finding {i} has unsupported review_class: {review_class}")
        validated.append({
            "type": ftype,
            "requirement_id": f.get("requirement_id"),
            "test_id": f.get("test_id"),
            "severity": f.get("severity", "medium"),
            "review_class": review_class,
            "reason": f.get("reason", ""),
            "human_review_required": True,
        })
    return validated

def call_openai(model):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. The key must be provided through the local environment; "
            "do not paste it into source files."
        )

    review_input = build_review_input()
    prompt = (
        SYSTEM_INSTRUCTION
        + "\n\nAllowed finding types:\n- "
        + "\n- ".join(sorted(ALLOWED_TYPES))
        + "\n\nReturn exactly this JSON shape:\n"
        + '{"findings":[{"type":"...","requirement_id":"RQ-xx or null",'
          '"test_id":"TC-xx or null","severity":"low|medium|high|critical",'
          '"review_class":"benchmark_candidate|discovery_candidate",'
          '"reason":"...","human_review_required":true}]}'
        + "\n\nArtifacts:\n"
        + json.dumps(review_input, indent=2)
    )

    body = {
        "model": model,
        "input": prompt,
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            response_obj = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        safe_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API HTTP {e.code}: {safe_body[:1000]}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"OpenAI API network error: {e.reason}") from e

    raw_text = extract_output_text(response_obj)
    parsed = parse_json_text(raw_text)
    findings = validate_findings(parsed["findings"])

    result = {
        "provider": "openai",
        "model": model,
        "response_id": response_obj.get("id"),
        "usage": response_obj.get("usage"),
        "findings": findings,
        "final_approval_performed": False,
    }
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="gpt-5.6-luna")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        review_input = build_review_input()
        print("LLM reviewer contract: OK")
        print(f"Requirements: {len(review_input['requirements'])}")
        print(f"Trace rows: {len(review_input['traceability'])}")
        print(f"Hydrated evidence rows: {sum(1 for x in review_input['hydrated_evidence'] if x['status'] == 'HYDRATED')}")
        print("Human final approval: DISALLOWED")
        return 0

    result = call_openai(args.model)
    out = ROOT / "findings" / "llm_review_openai.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"Model: {result['model']}")
    print(f"Findings: {len(result['findings'])}")
    print(f"Saved: {out.relative_to(ROOT)}")
    print("Final approval performed: NO")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
