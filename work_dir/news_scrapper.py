import requests
import jinja2
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse


def soup_maker(url_for_scrap) -> BeautifulSoup:
    '''
    :param url_for_scrap: url of article
    :return: BeautifulSoup object of web page
    '''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}
    result = requests.get(url_for_scrap, headers=headers)
    soup = BeautifulSoup(result.content, "html.parser")
    return soup


def article_scrap(article_url) -> dict:

    '''
    Scraps and Returns dict of item content
    :param article_url: url of article
    :return: dict of item content
    '''

    soup = soup_maker(article_url)
    item_dict = {}

    try:

        # Main content
        a = soup.find(attrs={"id": "content"})

        title = a.find(attrs={"data-testid": "Canon"})
        if title is None:
            title = a.find(attrs={"data-testid": "Foolscap"}).text
        else:
            title = title.text

        category = a.find(attrs={"data-testid": "CategoryLink"}).text

        date = soup.find(attrs={"property": "article:published_time"})['content'][:10]

        d = a.find_all(attrs={"data-testid": "HtmlContent"})
        description = ''.join([marker.get_text() for marker in d])

    except:
        item_dict = {'title': 'Non standard article structure',
            'category': "Non standard",
            'link': article_url
        }

    else:

        item_dict = {
            'title': title,
            'category': category,
            'date': date,
            'link': article_url,
            'description': description,
        }

    finally:
        return item_dict


def load_more_and_get_links(articles_grid_url, global_main_link, pages=5) -> list:
    '''
    Returns recursively generated list of article's urls
    :param articles_grid_url: page of articles
    :param global_main_link: global site link
    :param pages: number of pages to scrap
    :return: list of article's urls
    '''

    pages -= 1
    grid_soup = soup_maker(articles_grid_url)

    # load_more Null if doesn't exist
    load_more = grid_soup.find(attrs={"data-testid": "LoadMore"}).a.get('href')
    next_page = main_link + load_more

    # creates list of articles urls
    articles = grid_soup.select('a[class*="CardLink"]')
    temp_article_list = [main_link + index.get('href') for index in articles]

    # recursion block
    if pages >= 0 and load_more is not None:
        temp_article_list += load_more_and_get_links(next_page, global_main_link, pages)

    return temp_article_list


url = 'https://www.topgear.com/car-news/concept'
soup = soup_maker(url)


# Title info
title = soup.find(attrs={"property": "og:site_name"})['content']
link = soup.find(attrs={"rel": "canonical"})['href']
parse_link = urlparse(link, scheme='https')
empty = parse_link[:2] + ('',) * 4
main_link = urlunparse(empty)

channel = {
    'title': title,
    'link': main_link,
    }

# list of all articles
all_articles_urls = load_more_and_get_links(url, main_link, 5)

# load template
file_loader = jinja2.FileSystemLoader('.')
env = jinja2.Environment(loader=file_loader)
template_start = env.get_template('./work_dir/general_start.xml')
template_item = env.get_template('./work_dir/item.xml')
template_end = env.get_template('./work_dir/general_end.xml')

# uses template and writes file
start = template_start.render(channel=channel)
end = template_end.render()

result_file = open('../result/result.xml', 'w', encoding="utf-8")
result_file.writelines(start.replace("&", "&amp;"))

article_info = (article_scrap(url) for url in all_articles_urls)
main_article = template_item.render(article=article_info)

result_file.writelines(main_article.replace("&", "&amp;"))

result_file.writelines(end.replace("&", "&amp;"))

result_file.close()


