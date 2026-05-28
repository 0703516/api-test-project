"""
从 allure-results JSON 生成可视化的 HTML 报告（无需 Allure CLI）
用法：python generate_allure_report.py
"""
import json
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "reports" / "allure-results"
OUTPUT_FILE = BASE_DIR / "reports" / "allure_report.html"


def parse_results():
    """解析 allure-results 目录下的所有 JSON 文件"""
    test_cases = []
    containers = []

    for f in sorted(RESULTS_DIR.glob("*.json")):
        with open(f, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        name = data.get("name", "")
        if "testCase" in str(f) or (
            "fullName" in data and data.get("status")
        ):
            test_cases.append(data)

    # 按状态排序：失败 > 跳过 > 通过
    status_order = {"failed": 0, "broken": 1, "skipped": 2, "passed": 3}
    test_cases.sort(key=lambda t: status_order.get(t.get("status", "passed"), 99))

    return test_cases


def status_badge(status):
    badges = {
        "passed": '<span class="badge pass">PASSED</span>',
        "failed": '<span class="badge fail">FAILED</span>',
        "broken": '<span class="badge fail">BROKEN</span>',
        "skipped": '<span class="badge skip">SKIPPED</span>',
    }
    return badges.get(status, f'<span class="badge">{status}</span>')


def status_icon(status):
    icons = {
        "passed": "✅",
        "failed": "❌",
        "broken": "💥",
        "skipped": "⏭️",
    }
    return icons.get(status, "❓")


def generate_report():
    test_cases = parse_results()

    passed = sum(1 for t in test_cases if t.get("status") == "passed")
    failed = sum(1 for t in test_cases if t.get("status") in ("failed", "broken"))
    skipped = sum(1 for t in test_cases if t.get("status") == "skipped")
    total = len(test_cases)
    pass_rate = (passed / total * 100) if total > 0 else 0

    # 统计各文件
    from collections import Counter
    file_stats = Counter()
    for t in test_cases:
        group = t.get("labels", [])
        for lbl in group:
            if lbl.get("name") == "parentSuite":
                file_stats[lbl["value"]] += 1

    rows_html = ""
    for tc in test_cases:
        full_name = tc.get("fullName", tc.get("name", "unknown"))
        name = tc.get("name", full_name)
        status = tc.get("status", "unknown")
        duration = tc.get("time", {}).get("duration", 0) / 1000 if isinstance(tc.get("time"), dict) else 0
        status_msg = tc.get("statusMessage", "")
        status_trace = tc.get("statusTrace", "")

        # 提取 feature/story 标签
        labels = {l["name"]: l["value"] for l in tc.get("labels", [])}
        feature = labels.get("feature", "")
        story = labels.get("story", "")
        epic = labels.get("epic", "")

        error_html = ""
        if status in ("failed", "broken") and (status_msg or status_trace):
            error_html = f"""
            <tr class="error-row" style="display:none" id="err-{hash(full_name) & 0x7fffffff}">
                <td colspan="4">
                    <div class="error-block">
                        <pre>{status_msg}</pre>
                        <pre class="trace">{status_trace[:2000]}</pre>
                    </div>
                </td>
            </tr>"""

        rows_html += f"""
        <tr class="row-{status}" onclick="toggleError('err-{hash(full_name) & 0x7fffffff}')">
            <td>{status_icon(status)}</td>
            <td class="test-name">{name}</td>
            <td>{epic or feature or '-'}</td>
            <td>{duration:.2f}s</td>
            <td>{status_badge(status)}</td>
        </tr>{error_html}"""

    suite_rows = ""
    for name, count in file_stats.most_common():
        suite_rows += f"<tr><td>{name}</td><td>{count}</td></tr>"

    ring_color = "#4CAF50" if pass_rate >= 90 else ("#FF9800" if pass_rate >= 70 else "#F44336")

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>API 自动化测试报告 - Allure Style</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f6fa; color: #333; }}
.header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 40px; }}
.header h1 {{ font-size: 24px; margin-bottom: 8px; }}
.header .subtitle {{ opacity: 0.85; font-size: 14px; }}
.stats {{ display: flex; gap: 20px; padding: 30px 40px; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.06); flex-wrap: wrap; }}
.stat-card {{ flex: 1; min-width: 160px; text-align: center; padding: 20px; border-radius: 12px; background: #f8f9fc; }}
.stat-card .number {{ font-size: 36px; font-weight: 700; margin-bottom: 4px; }}
.stat-card .label {{ color: #888; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; }}
.stat-card.pass .number {{ color: #4CAF50; }}
.stat-card.fail .number {{ color: #F44336; }}
.stat-card.total .number {{ color: #2196F3; }}
.stat-card.rate .number {{ color: {ring_color}; }}
.ring-wrap {{ display: flex; justify-content: center; align-items: center; }}
.ring {{ width: 120px; height: 120px; border-radius: 50%; position: relative; display: flex; align-items: center; justify-content: center; }}
.ring svg {{ transform: rotate(-90deg); width: 120px; height: 120px; }}
.ring circle {{ fill: none; stroke-width: 10; }}
.ring .bg {{ stroke: #e0e0e0; }}
.ring .fg {{ stroke: {ring_color}; stroke-linecap: round; transition: stroke-dashoffset 1s ease; }}
.ring .inner {{ position: absolute; font-size: 28px; font-weight: 700; color: {ring_color}; }}
.container {{ max-width: 1200px; margin: 0 auto; padding: 30px 40px; }}
.section {{ background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 24px; overflow: hidden; }}
.section h2 {{ padding: 18px 24px; font-size: 16px; border-bottom: 1px solid #f0f0f0; }}
table {{ width: 100%; border-collapse: collapse; }}
th {{ text-align: left; padding: 12px 24px; font-size: 12px; text-transform: uppercase; color: #888; letter-spacing: 0.5px; border-bottom: 2px solid #f0f0f0; }}
td {{ padding: 12px 24px; font-size: 14px; border-bottom: 1px solid #f5f5f5; }}
.test-name {{ font-weight: 500; max-width: 500px; word-break: break-word; }}
.row-failed {{ background: #fff5f5; cursor: pointer; }}
.row-passed {{ cursor: pointer; }}
.row-passed:hover {{ background: #f8f9fc; }}
.row-failed:hover {{ background: #ffebeb; }}
.badge {{ display: inline-block; padding: 3px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }}
.badge.pass {{ background: #e8f5e9; color: #2e7d32; }}
.badge.fail {{ background: #ffebee; color: #c62828; }}
.badge.skip {{ background: #fff3e0; color: #e65100; }}
.error-block {{ background: #2d2d2d; color: #ff6b6b; padding: 16px 24px; margin: 8px 24px 16px; border-radius: 8px; overflow-x: auto; }}
.error-block pre {{ font-family: 'Fira Code', 'Consolas', monospace; font-size: 13px; white-space: pre-wrap; }}
.error-block .trace {{ color: #aaa; margin-top: 8px; }}
.footer {{ text-align: center; padding: 40px; color: #aaa; font-size: 13px; }}
.summary-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; padding: 24px; }}

@media (max-width: 768px) {{
  .stats {{ flex-direction: column; padding: 20px; }}
  .container {{ padding: 20px; }}
}}
</style>
</head>
<body>

<div class="header">
  <h1>🔬 API 自动化测试报告</h1>
  <div class="subtitle">
    执行时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} &nbsp;|&nbsp;
    被测系统: JSONPlaceholder + DummyJSON &nbsp;|&nbsp;
    框架: Python + Pytest + Requests
  </div>
</div>

<div class="stats">
  <div class="stat-card total">
    <div class="number">{total}</div>
    <div class="label">总用例数</div>
  </div>
  <div class="stat-card pass">
    <div class="number">{passed}</div>
    <div class="label">通过</div>
  </div>
  <div class="stat-card fail">
    <div class="number">{failed}</div>
    <div class="label">失败</div>
  </div>
  <div class="stat-card" style="min-width:120px">
    <div class="ring-wrap">
      <div class="ring">
        <svg viewBox="0 0 120 120">
          <circle class="bg" cx="60" cy="60" r="52"/>
          <circle class="fg" cx="60" cy="60" r="52"
            stroke-dasharray="{pass_rate / 100 * 326.73} 326.73"/>
        </svg>
        <div class="inner">{pass_rate:.1f}%</div>
      </div>
    </div>
    <div class="label" style="margin-top:8px">通过率</div>
  </div>
</div>

<div class="container">
  <div class="section">
    <h2>📊 测试套件概览</h2>
    <table>
      <thead><tr><th>测试文件</th><th>用例数</th></tr></thead>
      <tbody>{suite_rows}</tbody>
    </table>
  </div>

  <div class="section">
    <h2>📋 测试用例详情</h2>
    <table>
      <thead><tr><th style="width:40px"></th><th>用例名称</th><th>模块</th><th style="width:80px">耗时</th><th style="width:100px">状态</th></tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
  </div>
</div>

<div class="footer">
  Generated by Allure-Style Report Builder &nbsp;|&nbsp; Pytest + Requests &nbsp;|&nbsp; {datetime.now().year}
</div>

<script>
function toggleError(id) {{
  const el = document.getElementById(id);
  if (el) el.style.display = el.style.display === 'none' ? 'table-row' : 'none';
}}
</script>

</body>
</html>"""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ 报告已生成: {OUTPUT_FILE}")
    print(f"   总计: {total} | 通过: {passed} | 失败: {failed} | 跳过: {skipped}")
    print(f"   通过率: {pass_rate:.1f}%")


if __name__ == "__main__":
    generate_report()
