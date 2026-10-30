from urllib.parse import urljoin, urlparse
import time
from bs4 import BeautifulSoup
import pandas as pd
import requests

start_url = 'https://www.musashino-u.ac.jp/'
domain = urlparse(start_url).netloc

sitemap_dict = {}
visited = set()
to_visit = [start_url]

headers = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
}

# 全ページを巡回（to_visitが空になるまで実行）
while to_visit:
    current_url = to_visit.pop(0).split('#')[0]

    if not current_url or current_url in visited:
        continue

    visited.add(current_url)
    print(f'取得中 ({len(sitemap_dict)} 件完了): {current_url}')

    try:
        # サーバー負荷軽減のため1秒待機
        time.sleep(1)

        response = requests.get(current_url, headers=headers, timeout=10)

        # HTML以外（PDFや画像等）はスキップ
        if 'text/html' not in response.headers.get('Content-Type', ''):
            continue

        # デコードエラー警告防止
        html_text = response.content.decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html_text, 'html.parser')

        # タイトル取得
        title_tag = soup.find('title')
        title_text = (
            title_tag.text.strip().replace('\n', ' ') if title_tag else ''
        )
        sitemap_dict[current_url] = title_text

        # 同一ドメイン内のリンクを抽出して未訪問リストに追加
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(current_url, href).split('#')[0]
            parsed_url = urlparse(full_url)

            if (
                parsed_url.netloc == domain
                and parsed_url.scheme in ['http', 'https']
            ):
                if full_url not in visited and full_url not in to_visit:
                    to_visit.append(full_url)

    except Exception as e:
        print(f'スキップ ({current_url}): {e}')

# 完了後にCSV出力
df = pd.DataFrame(list(sitemap_dict.items()), columns=['URL', 'Title'])
df.to_csv('musashino_u_sitemap.csv', index=False, encoding='utf-8-sig')

print(
    f'全ページの取得が完了しました！ 計 {len(sitemap_dict)} 件を musashino_u_sitemap.csv に保存しました。'
)