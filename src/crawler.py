import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 只给一个首页作为起点
START_URL = "https://www.dadi360.com/"

def discovery_engine():
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    all_data = []
    
    print(f"🚀 启动自动发现引擎，目标：{START_URL}")
    
    try:
        # 第一步：获取首页，寻找分类链接
        resp = requests.get(START_URL, headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 自动寻找所有包含 "class_" 或 "list" 字样的链接
        links = soup.find_all('a', href=True)
        category_urls = []
        for l in links:
            href = l['href']
            # 自动识别分类页面的新特征
            if 'list' in href or 'class' in href:
                full_url = href if href.startswith('http') else START_URL + href.lstrip('/')
                if full_url not in category_urls:
                    category_urls.append(full_url)
        
        print(f"🔍 自动发现 {len(category_urls)} 个潜在分类入口。")
        
        # 第二步：自动深入前 3 个分类抓取内容
        for cat_url in category_urls[:50]:
            print(f"📡 正在自动钻取: {cat_url}")
            r = requests.get(cat_url, headers=headers, verify=False, timeout=10)
            if r.status_code == 200:
                s = BeautifulSoup(r.text, 'html.parser')
                items = s.find_all('a')
                count = 0
                for i in items:
                    t = i.get_text().strip()
                    if 15 < len(t) < 80:
                        all_data.append({'Title': t, 'Source': cat_url})
                        count += 1
                print(f"✅ 成功捕获 {count} 条条目")
                time.sleep(1)
            else:
                print(f"❌ 入口失效 (Status: {r.status_code})")

    except Exception as e:
        print(f"💥 引擎故障: {e}")

    if all_data:
        pd.DataFrame(all_data).to_csv('bayarea_services.csv', index=False)
        print(f"\n🏆 自动化任务圆满完成！共捕获 {len(all_data)} 条数据。")
    else:
        print("\n🤔 首页虽在，但未发现有效链接。建议直接手动复制浏览器里的一个分类页 URL。")

if __name__ == "__main__":
    discovery_engine()