import json
import os

import httpx
from dotenv import load_dotenv

from analyzer import analyze

load_dotenv()
GLM_API_KEY = os.getenv("GLM_API_KEY")
if not GLM_API_KEY:
    raise RuntimeError("缺少环境变量 GLM_API_KEY")


def explain(analysis: dict) -> str:
    response = httpx.post(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        headers={
            "Authorization": f"Bearer {GLM_API_KEY}",
        },
        json={
            "model": "glm-5.3",
            "messages": [
                {
                    "role": "system",
                    "content": """你是日志分析助手。用户会给你一份已经统计好的 JSON，来自一份 nginx 访问日志。
1. 只依据 JSON 里的数据说话。IP 归属地、攻击者身份、地理位置、动机——这些数据里没有，一律不许推测。
2. 信息不足以支撑判断时，直接说「数据不足以判断」，不要用猜测填补。
3. 不要重复罗列数字，那些用户自己看得见。
4. 输出 150 字以内中文，不超过三段。
5. 你回答的是：这段日志里最值得注意的是什么，为什么，按优先级排。""",
                },
                {"role": "user", "content": json.dumps(analysis, ensure_ascii=False)},
            ],
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


if __name__ == "__main__":
    print(explain(analyze("test.log")))
