import requests
from bs4 import BeautifulSoup
import re
import os

urls = [
    "https://api.uouin.com/cloudflare.html",
    "https://ip.164746.xyz",
    "https://www.wetest.vip/page/cloudflare/address_v6.html",
    "https://stock.hostmonit.com/CloudFlareYes",      # IPv4
    "https://stock.hostmonit.com/CloudFlareYesV6"     # IPv6
]

ip_pattern = re.compile(r'''
    \b
    (?:
        (?: (?:25[0-5]|2[0-4]\d|[01]?\d{1,2}) \.){3}
        (?:25[0-5]|2[0-4]\d|[01]?\d{1,2})                # IPv4
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

            # 按站点结构选容器
            if 'api.uouin.com' in url:
                containers = soup.find_all('li')
            else:
                containers = soup.find_all('tr')

            for tag in containers:
                for ip in ip_pattern.findall(tag.get_text()):
                    if ip not in seen:
                        seen.add(ip)
                        f.write(ip + '\n')
        except Exception as e:
            print(f"[ERROR] {url} -> {e}")

print('IPv4 & IPv6 已写入 ip.txt')
