import requests
from bs4 import BeautifulSoup
import re
import os

# ✅ 1. 只保留纯 URL
urls = [
    "https://api.uouin.com/cloudflare.html",
    "https://ip.164746.xyz",
    "https://www.wetest.vip/page/cloudflare/address_v6.html"
]

# 2. 正则不变
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

if os.path.exists('ip.txt'):
    os.remove('ip.txt')

seen = set()
with open('ip.txt', 'w', encoding='utf-8') as f:
    for url in urls:
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            # 3. 根据站点结构选择容器
            if 'api.uouin.com' in url:
                # 该站是 <li> 列表
                containers = soup.find_all('li')
            else:
                # 另外两个是表格
                containers = soup.find_all('tr')

            for tag in containers:
                for ip in ip_pattern.findall(tag.get_text()):
                    if ip not in seen:
                        seen.add(ip)
                        f.write(ip + '\n')
        except Exception as e:
            print(f"[ERROR] {url} -> {e}")

print('IPv4 & IPv6 已写入 ip.txt')
