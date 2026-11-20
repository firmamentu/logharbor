"""日志解析与统计，不依赖任何 Web 框架。"""
import re
from collections import Counter
from datetime import datetime

PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<path>\S+) \S+" '
    r'(?P<status>\d{3}) (?P<size>\d+)'
)

TIME_FMT = "%d/%b/%Y:%H:%M:%S %z"


def parse(lines):
    rows = []
    for line in lines:
        m = PATTERN.match(line)
        if m:
            rows.append(m.groupdict())
    return rows


def find_suspects(rows, min_errors=10, min_ratio=0.8):
    """4xx 次数够多且占自己全部请求比例够高的 IP。"""
    by_ip = {}
    for r in rows:
        by_ip.setdefault(r["ip"], []).append(r)

    suspects = []
    for ip, items in by_ip.items():
        errors = [r for r in items if r["status"].startswith("4")]
        if len(errors) < min_errors:
            continue
        if len(errors) / len(items) < min_ratio:
            continue

        times = [datetime.strptime(r["time"], TIME_FMT) for r in items]
        span = (max(times) - min(times)).total_seconds()

        suspects.append({
            "ip": ip,
            "count": len(items),
            "errors": len(errors),
            "error_ratio": round(len(errors) / len(items), 2),
            "span_seconds": round(span),
            "rate": round(len(items) / span, 2) if span else None,
            "paths": [p for p, _ in Counter(r["path"] for r in items).most_common(3)],
        })

    return sorted(suspects, key=lambda s: -s["errors"])


def summarize(result):
    """把数字翻译成人话。现在用规则，后面换成 LLM。"""
    status = result["status"]
    errors = sum(n for code, n in status.items() if code.startswith("4"))
    lines = [f"共 {result['total']} 次请求，其中 4xx 异常 {errors} 次。"]

    for s in result["suspects"]:
        if len(s["paths"]) == 1:
            kind = "反复尝试同一个入口"
        else:
            kind = "在多个路径上试探"
        lines.append(
            f"{s['ip']} 在 {s['span_seconds']} 秒内发起 {s['count']} 次请求，"
            f"{s['errors']} 次被拒（占 {s['error_ratio']:.0%}），"
            f"平均 {s['rate'] or 0} 次/秒，{kind}：{s['paths'][0]}。"
        )
    return lines


def analyze(path):
    with open(path) as f:
        rows = parse(f)

    by_ip = {}
    for r in rows:
        by_ip.setdefault(r["ip"], Counter())[r["status"]] += 1

    top_ips = [
        {"ip": ip, "count": sum(c.values()), "status": dict(c)}
        for ip, c in sorted(by_ip.items(), key=lambda kv: -sum(kv[1].values()))[:10]
    ]

    result = {
        "total": len(rows),
        "status": dict(Counter(r["status"] for r in rows)),
        "top_ips": top_ips,
        "suspects": find_suspects(rows),
    }
    result["summary"] = summarize(result)
    return result


if __name__ == "__main__":
    from pprint import pprint
    pprint(analyze("access.log"))