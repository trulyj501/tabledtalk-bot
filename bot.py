import requests
from bs4 import BeautifulSoup
import os

TARGET_URL = 'https://www.tabletalk.club/'
# 깃허브 Secret에서 가져옵니다
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')
LAST_POST_FILE = 'last_post.txt'

def get_latest_post():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(TARGET_URL, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        post_item = soup.find('div', class_='list-heading-wrapper')
        if post_item:
            title_element = post_item.find('h2')
            if title_element:
                title = title_element.get_text(strip=True)
                link_element = title_element.find_parent('a')
                if link_element and link_element.has_attr('href'):
                    href = link_element['href']
                    full_link = href if href.startswith('http') else "https://www.tabletalk.club" + href
                    return title, full_link
        return None, None
    except Exception as e:
        print(f"오류: {e}")
        return None, None

def send_slack_message(title, link):
    payload = {"text": f"🔔 *테이블 토크 새 게시물 알림*\n*제목:* {title}\n*바로가기:* {link}"}
    requests.post(SLACK_WEBHOOK_URL, json=payload)

def main():
    title, link = get_latest_post()
    if not title: return

    last_link = ""
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, 'r', encoding='utf-8') as f:
            last_link = f.read().strip()

    if link != last_link:
        send_slack_message(title, link)
        with open(LAST_POST_FILE, 'w', encoding='utf-8') as f:
            f.write(link)
        print(f"새 글 알림 전송: {title}")

if __name__ == "__main__":
    main()
