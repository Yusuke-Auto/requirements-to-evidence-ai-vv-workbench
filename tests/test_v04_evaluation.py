import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from evaluate_llm_review import evaluate, normalized_key
from llm_review_openai import build_review_input

class TestV04Evaluation(unittest.TestCase):
    def test_requirement_level_ignores_test_id(self):
        gt=[{"type":"ambiguous_requirement","requirement_id":"RQ-11","test_id":None,"observable":True}]
        pred=[{"type":"ambiguous_requirement","requirement_id":"RQ-11","test_id":"TC-11"}]
        r=evaluate(gt,pred)
        self.assertEqual(r["benchmark"]["hits"],1)
        self.assertEqual(r["benchmark"]["misses"],0)

    def test_unobservable_not_benchmark_target(self):
        gt=[{"type":"guardrail_violation","requirement_id":"RQ-12","test_id":"TC-12","observable":False}]
        r=evaluate(gt,[])
        self.assertEqual(r["benchmark"]["observable_targets"],0)

    def test_unmatched_prediction_is_discovery_not_automatic_fp(self):
        gt=[{"type":"ambiguous_requirement","requirement_id":"RQ-11","test_id":None,"observable":True}]
        pred=[
            {"type":"ambiguous_requirement","requirement_id":"RQ-11","test_id":"TC-11"},
            {"type":"ambiguous_requirement","requirement_id":"RQ-03","test_id":"TC-03"},
        ]
        r=evaluate(gt,pred)
        self.assertEqual(r["benchmark"]["hits"],1)
        self.assertEqual(r["discovery"]["candidate_count"],1)

    def test_context_hydrates_approval_audit(self):
        x=build_review_input()
        a=next(e for e in x["hydrated_evidence"] if e["test_id"]=="TC-12")
        self.assertEqual(a["status"],"HYDRATED")
        self.assertTrue(a["content"]["policy_check"]["violation_detected"])

    def test_rq10_is_explicit_missing_link(self):
        x=build_review_input()
        a=next(e for e in x["hydrated_evidence"] if e["test_id"]=="TC-10")
        self.assertEqual(a["status"],"MISSING_LINK")

if __name__=='__main__': unittest.main()
