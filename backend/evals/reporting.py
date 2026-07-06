def format_eval_report(suite_result: dict) -> str:
    total = suite_result.get("total", 0)
    passed = suite_result.get("passed", 0)
    failed = suite_result.get("failed", 0)
    score = suite_result.get("score", 0.0) * 100
    
    lines = []
    lines.append("=" * 40)
    lines.append("LeanBulk Coach - Evaluation Report")
    lines.append("=" * 40)
    lines.append(f"Total Cases: {total}")
    lines.append(f"Passed:      {passed}")
    lines.append(f"Failed:      {failed}")
    lines.append(f"Score:       {score:.1f}%")
    
    categories = {}
    for res in suite_result.get("results", []):
        cat = res["category"]
        if cat not in categories:
            categories[cat] = {"pass": 0, "fail": 0}
        if res["passed"]:
            categories[cat]["pass"] += 1
        else:
            categories[cat]["fail"] += 1
            
    lines.append("")
    lines.append("Per-Category Breakdown:")
    for cat in sorted(categories.keys()):
        stats = categories[cat]
        lines.append(f"  {cat}: {stats['pass']} passed, {stats['fail']} failed")
        
    if failed > 0:
        lines.append("")
        lines.append("Failed Case IDs:")
        for res in suite_result.get("results", []):
            if not res["passed"]:
                lines.append(f"  - {res['case_id']} ({res['category']})")
                
    lines.append("=" * 40)
    return "\n".join(lines)
