import re
from collections import Counter

PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<path>\S+) \S+" '
    r'(?P<status>\d{3}) (?P<size>\d+)'
)

rows = []
with open("access.log") as f:
    for line in f:
        m = PATTERN.match(line)
        if m:
            rows.append(m.groupdict())

print("总请求数:", len(rows))

print("\n状态码分布:")
for code, n in Counter(r["status"] for r in rows).most_common():
    print(f"  {code}  {n}")

print("\n访问最多的 5 个 IP:")
for ip, n in Counter(r["ip"] for r in rows).most_common(5):
    print(f"  {ip}  {n}")


print("\n按 IP 看状态码:")
by_ip = {}
for r in rows:
    by_ip.setdefault(r["ip"], Counter())[r["status"]] += 1

for ip, c in sorted(by_ip.items(), key=lambda kv: -sum(kv[1].values()))[:5]:
    detail = ", ".join(f"{k}x{v}" for k, v in c.most_common())
    print(f"  {ip}  共 {sum(c.values())} 次：{detail}")

from datetime import datetime

print("\n可疑 IP 的时间跨度:")
for ip in ["45.148.10.7", "193.32.162.11"]:
    times = [datetime.strptime(r["time"], "%d/%b/%Y:%H:%M:%S %z")
             for r in rows if r["ip"] == ip]
    span = (max(times) - min(times)).total_seconds()
    print(f"  {ip}  {len(times)} 次 / {span:.0f} 秒 = {len(times)/span:.2f} 次/秒")
    print(f"    从 {min(times):%H:%M:%S} 到 {max(times):%H:%M:%S}")