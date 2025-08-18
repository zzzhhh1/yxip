import requests, re, os, json
from bs4 import BeautifulSoup

# 1. 接口映射：url -> 真实数据地址
API_MAP = {
    "https://api.uouin.com/cloudflare.html":
        "https://api.uouin.com/api/get_cdn_ip_list",      # IPv4
    "https://stock.hostmonit.com/CloudFlareYes":
        "https://stock.hostmonit.com/CloudFlareYes.json", # IPv4
    "https://stock.hostmonit.com/CloudFlareYesV6":
        "https://stock.hostmonit.com/CloudFlareYesV6.json" # IPv6
}

# 2. 其余普通页面
normal_urls = [
    "https://ip.164746.xyz",
    "https://www.wetest.vip/page/cloudflare/address_v6.html"
]

ip_pattern = re.compile(r'''
    \b
    (?:
        (?: (?:25[0-5]|2[0-4]\d|[01]?\d{1,2}) \.){3}
        (?:25[0-5]|2[0-4]\d|[01]?\d{1,2})
      |
        (?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}
      | (?:[0-9a-fA-F]{1,4}:)*::(?:[0-9a-fA-F]{1,4}:)*[0-9a-fA-F]{1,4}
      | ::(?:[0-9a-fA-F]{1,4}:){0,6}[0-9a-fA-F]{1,4}
      | (?:[0-9a-fA-F]{1,4}:){1,7}:
    )
    \b
''', re.VERBOSE)

seen = set()
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

with open('ip.txt', 'w', encoding='utf-8') as f:
    # ---- 处理 Ajax 接口 ----
    for display_url, api_url in API_MAP.items():
        try:
            r = requests.get(api_url, timeout=10)
            r.raise_for_status()
            try:
                data = r.json()          # uouin 返回 {"data":[...]}
                if 'data' in data:
                    raw_list = data['data']
                else:
                    raw_list = data      # hostmonit 直接返回 [...]
            except ValueError:
                raw_list = []            # 兜底
            ips = [ip for item in raw_list
                   for ip in ip_pattern.findall(str(item))]
            new_ips = [ip for ip in ips if ip not in seen]
            for ip in new_ips:
                seen.add(ip)
                f.write(ip + '\n')
            print(f"[{display_url}] 抓到 {len(new_ips)} 个新 IP")
        except Exception as e:
            print(f"[ERROR] {display_url} -> {e}")

    # ---- 处理普通网页 ----
    for url in normal_urls:
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            containers = soup.find_all('tr') if 'wetest.vip' in url else soup.find_all('tr')
            ips = [ip for tag in containers for ip in ip_pattern.findall(tag.get_text())]
            new_ips = [ip for ip in ips if ip not in seen]
            for ip in new_ips:
                seen.add(ip)
                f.write(ip + '\n')
            print(f"[{url}] 抓到 {len(new_ips)} 个新 IP")
        except Exception as e:
            print(f"[ERROR] {url} -> {e}")

print(f"全部完成，共 {len(seen)} 个 IP 写入 ip.txt")
