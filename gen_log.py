"""生成假的 nginx access.log，用于开发和演示。"""
import random
import datetime

random.seed(11)
start = datetime.datetime(2026, 11, 18, 8, 0, 0)
lines = []


def add(t, ip, method, path, status, size=None):
    size = size or random.randint(180, 9000)
    lines.append(
        f'{ip} - - [{t:%d/%b/%Y:%H:%M:%S} +0800] '
        f'"{method} {path} HTTP/1.1" {status} {size} "-" "Mozilla/5.0"'
    )


t = start
for _ in range(1200):  # 正常流量
    t += datetime.timedelta(seconds=random.randint(5, 40))
    add(
        t,
        f"10.0.{random.randint(1, 3)}.{random.randint(2, 254)}",
        "GET",
        random.choice(["/", "/index.html", "/static/app.js", "/api/v1/orders"]),
        200,
    )

t = start + datetime.timedelta(minutes=37)  # 撞库：同一 IP 连打 /login
for _ in range(300):
    t += datetime.timedelta(seconds=random.randint(0, 1))
    add(t, "45.148.10.7", "POST", "/api/v1/login", 401, 233)

t = start + datetime.timedelta(minutes=95)  # 扫描器
for p in ["/wp-login.php", "/admin", "/.env", "/phpmyadmin"] * 6:
    t += datetime.timedelta(seconds=random.randint(1, 6))
    add(t, "193.32.162.11", "GET", p, 404, 153)

out = "\n".join(lines) + "\n"
open("access.log", "w").write(out)
print(len(lines), "行 ->", "access.log")
