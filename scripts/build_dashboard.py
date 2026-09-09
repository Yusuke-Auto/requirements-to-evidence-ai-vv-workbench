#!/usr/bin/env python3
from pathlib import Path
import argparse
import html
import json

ROOT = Path(__file__).resolve().parents[1]

def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def esc(x):
    return html.escape("" if x is None else str(x))

def badge(text, kind="neutral"):
    return f'<span class="badge badge-{kind}">{esc(text)}</span>'

def build():
    requirements = load("requirements/requirements.json")
    traces = load("evidence/traceability.json")
    llm = load("findings/llm_review_openai_v0.4.json")
    evalv = load("evidence/llm_evaluation_v0.4.json")
    adj = load("evidence/discovery_adjudication_v0.4.json")
    structural = load("evidence/deterministic_evidence_validation.json")

    decisions = {}
    for d in adj["decisions"]:
        key = (d["type"], d["requirement_id"], d.get("test_id"))
        decisions[key] = d

    finding_rows = []
    for i, f in enumerate(llm["findings"], 1):
        key = (f["type"], f["requirement_id"], f.get("test_id"))
        d = decisions.get(key)
        if f.get("review_class") == "benchmark_candidate":
            human = "Seeded benchmark hit"
            human_kind = "good"
        elif d and d["decision"] == "VALID_DISCOVERY":
            human = "Valid discovery"
            human_kind = "good"
        elif d and d["decision"] == "FALSE_POSITIVE":
            human = "False positive"
            human_kind = "bad"
        else:
            human = "Needs adjudication"
            human_kind = "warn"

        cls = "Benchmark" if f.get("review_class") == "benchmark_candidate" else "Discovery"
        finding_rows.append(f"""
          <tr data-class="{cls.lower()}" data-decision="{human_kind}">
            <td><span class="finding-index">F{i:02d}</span></td>
            <td>{badge(cls, "benchmark" if cls=="Benchmark" else "discovery")}</td>
            <td><code>{esc(f["requirement_id"])}</code></td>
            <td><code>{esc(f.get("test_id") or "—")}</code></td>
            <td>{badge(f["severity"].upper(), "critical" if f["severity"]=="critical" else "severity")}</td>
            <td><strong>{esc(f["type"])}</strong><div class="reason">{esc(f["reason"])}</div></td>
            <td>{badge(human, human_kind)}</td>
          </tr>
        """)

    req_rows = []
    trace_map = {t["requirement_id"]: t for t in traces}
    for r in requirements:
        t = trace_map.get(r["id"], {})
        evidence = t.get("evidence")
        status = "Missing" if not evidence else "Linked"
        req_rows.append(f"""
          <tr>
            <td><code>{esc(r["id"])}</code></td>
            <td>{esc(r["text"])}</td>
            <td>{esc(t.get("component") or "—")}</td>
            <td><code>{esc(t.get("test_id") or "—")}</code></td>
            <td>{badge(status, "bad" if status=="Missing" else "good")}</td>
          </tr>
        """)

    benchmark = evalv["benchmark"]
    discovery = adj["summary"]

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI V&V Review Console</title>
<style>
:root {{
  --bg:#0b1020;
  --panel:#121a2d;
  --panel2:#172238;
  --text:#ecf2ff;
  --muted:#9eabc4;
  --line:#283654;
  --accent:#6ea8fe;
  --good:#39d98a;
  --warn:#ffcf5c;
  --bad:#ff6b7a;
  --purple:#b69cff;
  --shadow:0 18px 50px rgba(0,0,0,.24);
}}
* {{ box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{
  margin:0;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color:var(--text);
  background:
    radial-gradient(circle at 10% -10%, rgba(110,168,254,.18), transparent 35%),
    radial-gradient(circle at 90% 0%, rgba(182,156,255,.12), transparent 32%),
    var(--bg);
  line-height:1.55;
}}
a {{ color:var(--accent); text-decoration:none; }}
code {{ color:#dce8ff; background:#0c1324; padding:.12rem .35rem; border-radius:5px; }}
.shell {{ max-width:1280px; margin:auto; padding:28px 28px 72px; }}
.topbar {{
  display:flex; justify-content:space-between; align-items:center; gap:24px;
  padding:10px 0 30px;
}}
.brand {{ display:flex; align-items:center; gap:12px; font-weight:750; letter-spacing:-.02em; }}
.logo {{
  width:38px; height:38px; border-radius:11px; display:grid; place-items:center;
  background:linear-gradient(135deg,var(--accent),var(--purple)); color:#081020; font-weight:900;
}}
.nav {{ display:flex; gap:18px; flex-wrap:wrap; font-size:.92rem; }}
.nav a {{ color:var(--muted); }}
.nav a:hover {{ color:var(--text); }}
.hero {{
  display:grid; grid-template-columns:minmax(0,1.4fr) minmax(300px,.6fr); gap:24px;
  align-items:stretch; margin-bottom:24px;
}}
.hero-main, .panel {{
  border:1px solid var(--line); background:linear-gradient(180deg,rgba(23,34,56,.94),rgba(18,26,45,.94));
  border-radius:18px; box-shadow:var(--shadow);
}}
.hero-main {{ padding:34px; }}
.eyebrow {{ color:var(--accent); font-weight:800; text-transform:uppercase; letter-spacing:.12em; font-size:.72rem; }}
h1 {{ font-size:clamp(2.15rem,4vw,4.15rem); line-height:1.03; margin:12px 0 18px; letter-spacing:-.055em; }}
.lead {{ color:#c5d2e9; max-width:760px; font-size:1.08rem; }}
.callout {{
  margin-top:24px; padding:16px 18px; border-left:3px solid var(--accent);
  background:rgba(110,168,254,.08); border-radius:0 12px 12px 0;
}}
.metrics {{ display:grid; grid-template-columns:repeat(2,1fr); gap:12px; padding:18px; }}
.metric {{
  min-height:130px; padding:20px; border:1px solid var(--line); border-radius:14px;
  background:rgba(10,16,32,.46); display:flex; flex-direction:column; justify-content:space-between;
}}
.metric .value {{ font-size:2.25rem; font-weight:850; letter-spacing:-.04em; }}
.metric .label {{ color:var(--muted); font-size:.87rem; }}
.metric.good .value {{ color:var(--good); }}
.metric.warn .value {{ color:var(--warn); }}
.metric.bad .value {{ color:var(--bad); }}
.grid-3 {{ display:grid; grid-template-columns:repeat(3,1fr); gap:18px; margin:18px 0 28px; }}
.panel {{ padding:24px; }}
.panel h2, section h2 {{ margin:0 0 8px; letter-spacing:-.025em; }}
.panel p, .muted {{ color:var(--muted); }}
.section {{ margin-top:34px; }}
.section-head {{ display:flex; justify-content:space-between; align-items:end; gap:20px; margin-bottom:14px; }}
.section-head p {{ color:var(--muted); max-width:720px; margin:0; }}
.flow {{
  display:grid; grid-template-columns:repeat(7,1fr); gap:9px; align-items:center; margin-top:18px;
}}
.flow .step {{
  min-height:98px; padding:14px; border-radius:12px; border:1px solid var(--line);
  background:rgba(10,16,32,.48); display:flex; flex-direction:column; justify-content:center;
}}
.flow .arrow {{ color:var(--muted); text-align:center; font-size:1.3rem; }}
.flow .num {{ color:var(--accent); font-size:.72rem; font-weight:800; text-transform:uppercase; }}
.flow strong {{ margin-top:4px; line-height:1.25; }}
.table-wrap {{
  overflow:auto; border:1px solid var(--line); border-radius:14px; background:rgba(10,16,32,.4);
}}
table {{ width:100%; border-collapse:collapse; font-size:.9rem; }}
th,td {{ padding:13px 14px; text-align:left; vertical-align:top; border-bottom:1px solid var(--line); }}
th {{ position:sticky; top:0; background:#121b2f; color:#b8c6df; font-size:.77rem; text-transform:uppercase; letter-spacing:.06em; }}
tr:last-child td {{ border-bottom:none; }}
.reason {{ color:var(--muted); margin-top:5px; min-width:330px; }}
.badge {{
  display:inline-flex; align-items:center; border-radius:999px; padding:4px 9px;
  font-size:.72rem; font-weight:780; white-space:nowrap; border:1px solid transparent;
}}
.badge-good {{ color:var(--good); background:rgba(57,217,138,.09); border-color:rgba(57,217,138,.28); }}
.badge-bad {{ color:var(--bad); background:rgba(255,107,122,.09); border-color:rgba(255,107,122,.28); }}
.badge-warn {{ color:var(--warn); background:rgba(255,207,92,.09); border-color:rgba(255,207,92,.28); }}
.badge-benchmark {{ color:var(--accent); background:rgba(110,168,254,.1); border-color:rgba(110,168,254,.3); }}
.badge-discovery {{ color:var(--purple); background:rgba(182,156,255,.1); border-color:rgba(182,156,255,.3); }}
.badge-severity {{ color:#c7d6ee; background:#1a263d; border-color:#334464; }}
.badge-critical {{ color:var(--bad); background:rgba(255,107,122,.1); border-color:rgba(255,107,122,.32); }}
.finding-index {{ color:var(--muted); font-weight:800; }}
.filters {{ display:flex; gap:8px; flex-wrap:wrap; }}
button {{
  border:1px solid var(--line); background:#111a2c; color:var(--muted);
  border-radius:999px; padding:8px 12px; cursor:pointer; font:inherit; font-size:.82rem;
}}
button.active, button:hover {{ color:var(--text); border-color:#5275ab; background:#19263e; }}
.split {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}
.timeline {{ display:grid; grid-template-columns:1fr auto 1fr; align-items:stretch; gap:14px; }}
.version {{
  padding:22px; border-radius:14px; border:1px solid var(--line); background:rgba(10,16,32,.46);
}}
.version .big {{ font-size:2rem; font-weight:850; letter-spacing:-.04em; }}
.version.v03 .big {{ color:var(--warn); }}
.version.v04 .big {{ color:var(--good); }}
.timeline .to {{ align-self:center; color:var(--muted); font-size:1.5rem; }}
pre {{
  overflow:auto; padding:18px; border-radius:12px; background:#080d18; border:1px solid var(--line);
  color:#d7e4f8; font-size:.87rem;
}}
.footer {{ color:var(--muted); margin-top:46px; padding-top:22px; border-top:1px solid var(--line); font-size:.88rem; }}
@media(max-width:980px) {{
  .hero, .split, .grid-3 {{ grid-template-columns:1fr; }}
  .flow {{ grid-template-columns:1fr; }}
  .flow .arrow {{ transform:rotate(90deg); }}
}}
@media(max-width:640px) {{
  .shell {{ padding:18px 14px 50px; }}
  .topbar {{ align-items:flex-start; flex-direction:column; }}
  .hero-main {{ padding:24px; }}
  .metrics {{ grid-template-columns:1fr 1fr; padding:12px; }}
  .metric {{ min-height:105px; padding:15px; }}
  .metric .value {{ font-size:1.75rem; }}
}}
</style>
</head>
<body>
<div class="shell">
  <header class="topbar">
    <div class="brand"><div class="logo">V&V</div><div>Requirements-to-Evidence<br><span class="muted">AI V&V Workbench</span></div></div>
    <nav class="nav">
      <a href="#overview">Overview</a>
      <a href="#findings">Findings</a>
      <a href="#trace">Traceability</a>
      <a href="#reproduce">Reproduce</a>
    </nav>
  </header>

  <main>
    <section class="hero" id="overview">
      <div class="hero-main">
        <div class="eyebrow">Synthetic engineering work sample</div>
        <h1>Verify the artifacts.<br>Verify the AI reviewer.</h1>
        <p class="lead">
          A compact AEB-like case demonstrating Requirement → Test → Evidence traceability,
          LLM-assisted semantic review, deterministic structural validation, and a human-controlled approval boundary.
        </p>
        <div class="callout">
          <strong>Claim boundary:</strong> 5/5 means all five seeded defects in this small synthetic benchmark were detected.
          It is <strong>not</strong> a production-accuracy, safety-compliance, or regulatory claim.
        </div>
      </div>

      <div class="hero-main metrics">
        <div class="metric good"><div class="label">Seeded benchmark</div><div class="value">{benchmark["hits"]}/{benchmark["observable_targets"]}</div><div class="label">known defects detected</div></div>
        <div class="metric good"><div class="label">Benchmark recall</div><div class="value">{benchmark["recall"]:.2f}</div><div class="label">on this synthetic set</div></div>
        <div class="metric good"><div class="label">Valid discoveries</div><div class="value">{discovery["valid_discoveries"]}</div><div class="label">after human adjudication</div></div>
        <div class="metric bad"><div class="label">Confirmed false positives</div><div class="value">{discovery["false_positives"]}</div><div class="label">LLM reviewer failure retained</div></div>
      </div>
    </section>

    <div class="grid-3">
      <div class="panel"><h2>12 Requirements</h2><p>Public/synthetic AEB-like requirements with component, test, and evidence relations.</p></div>
      <div class="panel"><h2>5 Seeded Defects</h2><p>Ambiguity, contradiction, missing evidence, broken trace, and approval-guardrail violation.</p></div>
      <div class="panel"><h2>Human Final Decision</h2><p>The LLM creates findings; it cannot promote a requirement or test to final Verified/Approved state.</p></div>
    </div>

    <section class="section">
      <div class="section-head">
        <div><div class="eyebrow">Review architecture</div><h2>Deterministic-first, LLM-second</h2></div>
        <p>Simple structural facts are checked by code. The LLM focuses on semantic engineering judgment. Open-ended findings go to a human/domain expert.</p>
      </div>
      <div class="panel">
        <div class="flow">
          <div class="step"><span class="num">01 Input</span><strong>Requirements<br>Trace<br>Evidence</strong></div>
          <div class="arrow">→</div>
          <div class="step"><span class="num">02 Exact facts</span><strong>Deterministic validation</strong></div>
          <div class="arrow">→</div>
          <div class="step"><span class="num">03 Semantics</span><strong>LLM review</strong></div>
          <div class="arrow">→</div>
          <div class="step"><span class="num">04 Authority</span><strong>Human adjudication &amp; approval</strong></div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <div><div class="eyebrow">Evaluation evolution</div><h2>Why the first F1 = 0.40 was misleading</h2></div>
        <p>The model was not the only thing under test. The evaluator and context architecture were V&V targets too.</p>
      </div>
      <div class="timeline">
        <div class="version v03">
          <div class="eyebrow">v0.3 raw exact match</div>
          <div class="big">F1 = 0.40</div>
          <p class="muted">TP=3 / FP=7 / FN=2. Failure analysis found incidental test-ID matching, unobservable ground truth, and non-hydrated evidence.</p>
        </div>
        <div class="to">→</div>
        <div class="version v04">
          <div class="eyebrow">v0.4 corrected contract</div>
          <div class="big">5 / 5 benchmark hits</div>
          <p class="muted">Only observable targets; requirement-level semantic matching; evidence hydration; discovery separated from benchmark scoring.</p>
        </div>
      </div>
    </section>

    <section class="section" id="findings">
      <div class="section-head">
        <div><div class="eyebrow">Live LLM result</div><h2>Findings & human adjudication</h2></div>
        <div class="filters">
          <button class="active" data-filter="all">All</button>
          <button data-filter="benchmark">Benchmark</button>
          <button data-filter="discovery">Discovery</button>
          <button data-filter="good">Accepted</button>
          <button data-filter="bad">False positive</button>
        </div>
      </div>
      <div class="table-wrap">
        <table id="findings-table">
          <thead><tr><th>#</th><th>Class</th><th>Req</th><th>Test</th><th>Severity</th><th>Finding</th><th>Human decision</th></tr></thead>
          <tbody>{''.join(finding_rows)}</tbody>
        </table>
      </div>
    </section>

    <section class="section" id="trace">
      <div class="section-head">
        <div><div class="eyebrow">Traceability</div><h2>Requirement → Component → Test → Evidence</h2></div>
        <p>The table deliberately retains the seeded missing-evidence case instead of hiding it.</p>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Req</th><th>Requirement</th><th>Component</th><th>Test</th><th>Evidence</th></tr></thead>
          <tbody>{''.join(req_rows)}</tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <div class="split">
        <div class="panel">
          <div class="eyebrow">Known reviewer failure</div>
          <h2>RQ-09 false positive</h2>
          <p>The LLM claimed the decision record lacked <code>requirement_id</code>. The hydrated JSON actually contains the field.</p>
          <p><strong>Design response:</strong> field/file/schema presence is now a deterministic validation responsibility.</p>
          <div>{badge(structural["overall_result"], "good" if structural["overall_result"]=="PASS" else "bad")} structural evidence validation</div>
        </div>
        <div class="panel">
          <div class="eyebrow">Useful semantic discovery</div>
          <h2>RQ-05 ambiguity</h2>
          <p>The phrase <code>collision risk is cleared</code> does not define a measurable clearance criterion. A recorded clearance timestamp does not solve the requirement ambiguity.</p>
          <div>{badge("VALID DISCOVERY","good")} after human adjudication</div>
        </div>
      </div>
    </section>

    <section class="section" id="reproduce">
      <div class="section-head">
        <div><div class="eyebrow">Reproducibility</div><h2>Run the evidence locally</h2></div>
        <p>No API key is required to reproduce the saved evaluation and regression tests.</p>
      </div>
      <div class="panel">
        <pre><code>python scripts/run_public_demo.py

# Optional safety scan
python scripts/public_safety_check.py</code></pre>
        <p class="muted">Optional live review stays outside the browser so an API key is never exposed in client-side UI.</p>
      </div>
    </section>
  </main>

  <footer class="footer">
    Synthetic public work sample · no OEM/confidential data · no production-compliance claim · final approval remains human-controlled
  </footer>
</div>

<script>
document.querySelectorAll('[data-filter]').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('[data-filter]').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const f = btn.dataset.filter;
    document.querySelectorAll('#findings-table tbody tr').forEach(row => {{
      const show = f === 'all' || row.dataset.class === f || row.dataset.decision === f;
      row.style.display = show ? '' : 'none';
    }});
  }});
}});
</script>
</body>
</html>
"""
    return html_doc

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="docs/dashboard.html")
    args = parser.parse_args()

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(), encoding="utf-8")
    print(f"Built dashboard: {out.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
