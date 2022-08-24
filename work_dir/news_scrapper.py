import requests
import jinja2
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse

url = 'https://www.topgear.com/car-news/concept/lincoln-model-l100-concept-effortlessly-cool'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}
result = requests.get(url, headers=headers)

soup = BeautifulSoup(result.content, "html.parser")

# Title info
title = soup.find(attrs={"property": "og:site_name"})['content']
link = soup.find(attrs={"property": "og:url"})['content']
parse_link = urlparse(link, scheme='https')
empty = parse_link[:2] + ('',) * 4
main_link = urlunparse(empty)


channel = {
    'title': title,
    'link': main_link,
    }

# Main content
a = soup.find(attrs={"data-testid": "MainContent"})

title = a.find(attrs={"data-testid": "Canon"}).text
category = a.find(attrs={"data-testid": "CategoryLink"}).text
date = list(a.find(attrs={"data-testid": "Brevier"}).stripped_strings)[1]
link = a.select_one(".disqus-comment-count")['data-disqus-url']

d = a.find_all(attrs={"data-testid": "HtmlContent"})
description = ''.join([marker.get_text() for marker in d])

item = {
    'title': title,
    'category': category,
    'date': date,
    'link': link,
    'description': description,
    }

# tuple of content
article_list = (channel, item)

# load template
file_loader = jinja2.FileSystemLoader('.')
env = jinja2.Environment(loader=file_loader)
template = env.get_template('./work_dir/a.xml')

# uses template and writes file
ans = template.render(article_list=article_list)
with open('./result/result.xml', 'w') as f:
    f.writelines(ans)



