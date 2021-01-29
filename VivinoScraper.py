import re
import requests
from time import sleep
from bs4 import BeautifulSoup

url = 'https://www.vivino.com/search/wines?q={kw}&start={page}'
prices_url = 'https://www.vivino.com/prices'
headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0'}

def get_wines(kw):
    with requests.session() as s:
        page = 1
        while True:
            soup = BeautifulSoup(s.get(url.format(kw=kw, page=page), headers=headers).content, 'html.parser')
            print(soup)
            if not soup.select('.default-wine-card'):
                break

            params = {'vintages[]': [wc['data-vintage'] for wc in soup.select('.default-wine-card')]}
            prices_js = s.get(prices_url, params=params, headers={
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0',
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01'
                }).text

            wine_prices = dict(re.findall(r"\$\('\.vintage-price-id-(\d+)'\)\.find\( '\.wine-price-value' \)\.text\( '(.*?)' \);", prices_js))

            for wine_card in soup.select('.default-wine-card'):
                title = wine_card.select_one('.header-smaller').get_text(strip=True, separator=' ')
                price = wine_prices.get(wine_card['data-vintage'], '-')

                average = wine_card.select_one('.average__number')
                average = average.get_text(strip=True) if average else '-'

                ratings = wine_card.select_one('.text-micro')
                ratings = ratings.get_text(strip=True) if ratings else '-'

                link = 'https://www.vivino.com' + wine_card.a['href']

                yield title, price, average, ratings, link

            sleep(3)
            page +=1

kw = 'primitivo'
for title, price, average, ratings, link in get_wines(kw):
    print(title)
    print(ratings)
    print(price)
