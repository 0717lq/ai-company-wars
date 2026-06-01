#!/usr/bin/env python3
"""
check-github.py — AI Company Wars GitHub 连通性检测

用途：DevOps Agent 在执行 GitHub 操作前调用此脚本，
判断当前环境是否支持 GitHub API / Release 操作。

返回值：
  exit 0 → GitHub 可达，可以执行 Release
  exit 1 → DNS 被劫持（如 VPN 代理），跳过 GitHub 操作
  exit 2 → GitHub 不可达但原因不是 DNS 劫持

输出（stdout）JSON：
  {"status": "ok" | "dns_hijacked" | "unreachable", "detail": "..."}
"""

import json
import socket
import ssl
import sys
import urllib.request
import urllib.error

# GitHub 真实 IP 范围（部分）——用于判断 DNS 是否被劫持
# 198.18.0.0/15 是 RFC 2544 保留段，不应出现在正常 DNS 解析中
KNOWN_FAKE_RANGES = [
    ("198.18.", "RFC 2544 benchmark range — likely VPN/security software DNS hijack"),
]

GITHUB_TEST_URLS = [
    "https://api.github.com",
]


def check_dns_hijack(hostname="api.github.com"):
    """检测 DNS 是否被劫持到虚拟 IP"""
    try:
        ips = socket.getaddrinfo(hostname, 443, family=socket.AF_INET)
        for addr_info in ips:
            ip = str(addr_info[4][0])
            for prefix, desc in KNOWN_FAKE_RANGES:
                if str(ip).startswith(prefix):
                    return True, ip, desc
        return False, ips[0][4][0] if ips else "N/A", "DNS resolution normal"
    except socket.gaierror as e:
        return True, "N/A", f"DNS resolution failed: {e}"


def check_https_reachable(url="https://api.github.com", timeout=5):
    """检测 HTTPS 是否可达"""
    ctx = ssl.create_default_context()
    try:
        req = urllib.request.Request(url, method="HEAD")
        resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return True, resp.status
    except urllib.error.URLError as e:
        return False, str(e.reason)[:100] if hasattr(e, 'reason') else str(e)[:100]
    except Exception as e:
        return False, str(e)[:100]


def main():
    result = {"status": "unknown", "detail": "", "checks": {}}

    # 1. DNS 检查
    hijacked, resolved_ip, detail = check_dns_hijack()
    result["checks"]["dns"] = {
        "resolved_ip": resolved_ip,
        "hijacked": hijacked,
        "detail": detail,
    }

    # 2. HTTPS 检查
    reachable, http_detail = check_https_reachable()
    result["checks"]["https"] = {
        "reachable": reachable,
        "detail": http_detail,
    }

    # 综合判定
    if hijacked:
        result["status"] = "dns_hijacked"
        result["detail"] = f"DNS resolved {resolved_ip} in virtual range — likely VPN/security software active"
    elif not reachable:
        result["status"] = "unreachable"
        result["detail"] = f"HTTPS unreachable: {http_detail}"
    else:
        result["status"] = "ok"
        result["detail"] = "GitHub reachable"

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] == "ok":
        sys.exit(0)
    elif result["status"] == "dns_hijacked":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
