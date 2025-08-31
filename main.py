from loguru import logger
import requests
import chardet
from lxml import html as htmlx
from lxml.html import HtmlElement
import re
from types import SimpleNamespace as DictIt


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.205 Safari/537.36"
}

class Parser:
    def getpage(self, link):
        try:
            res = requests.get(link, headers=headers)
            res.raise_for_status()
            encoding = chardet.detect(res.content)['encoding']
            html = res.content.decode(encoding, errors='replace')

            with open('last-fetch.html', 'w', encoding='utf-8') as file:
                file.write(html)
            return html
        
        except Exception as e:
            logger.error(f"Не удалось запросить страницу: {e}")
            return None

    class Tree:
        def __init__(self, content):
            if isinstance(content, str):
                self.tree = htmlx.fromstring(content)
            elif isinstance(content, HtmlElement):
                self.tree = content
            else:
                raise ValueError("Tree странный объект")

        def select(self, selector):

            class Elements:
                def __init__(self, elements):
                    self.elements = elements

                def __iter__(self):
                    return iter(self.elements)
                
                def __len__(self):
                    return len(self.elements)

                def text(self, index=0, default=''):
                    try:
                        text = self.elements[index].text_content().strip()
                        text = re.sub(r'\s+', ' ', text)
                        return text
                    
                    except IndexError:
                        return default

                def attr(self, name, index=0, default=''):
                    try:
                        return self.elements[index].get(name, default)
                    except IndexError:
                        return default

            elements = self.tree.cssselect(selector)
            return Elements(elements)
    
    def newtree(self, content):
        return Parser.Tree(content)


parser = Parser()

class PostupiAPI:
    def __init__(self):
        pass
    
    def univs(self):
        class Univs:
            def getcatalog(self, spec, page=1):
                html = parser.getpage(
                    f"https://postupi.online/specialnost/{spec}/vuzi/?page_num={page}"
                )
                tree = parser.newtree(html)
                cards = tree.select('.list-cover > ul > li')#.elements

                for card_elem in cards:
                    #card = parser.newtree(card_elem)
                    card = card_elem

                    title = card.select('h2 > a').text()
                    link = card.select('h2 > a').attr('href')

                    city_id, univ_id = '', ''
                    match = re.match(r'https://(.*?)\.postupi\.online/vuz/(.*?)/', link)
                    if match:
                        city_id = match.group(1)
                        univ_id = match.group(2)

                    metadata = tree.select('.list__pre > span')
                    print(len(metadata), metadata.text(index=0), metadata.text(index=1), metadata.text(index=2))
                    if len(metadata) <= 2:
                        city = metadata.text(index=0)
                    else:
                        city = metadata.text(index=1)
                    
                    learning_cost = tree.select('.list__price > b').text()

                    budget_places, paid_places = '', ''
                    for i in range(0, 4):
                        row_title = tree.select('div.list__score-wrap span.hidden-mid').text(index=i)
                        row_value = tree.select('div.list__score-wrap b').text(index=i)

                        if "мест" in row_title:
                            if "бюджет" in row_title:
                                budget_places = row_value
                            elif "платно" in row_title:
                                paid_places = row_value
                    
                    yield DictIt(
                        title=title,
                        univ_id=univ_id,
                        link=link,
                        city=city,
                        city_id=city_id,
                        learning_cost=learning_cost,
                        budget_places=budget_places,
                        paid_places=paid_places
                    )

        return Univs()


postupi = PostupiAPI()
univs = postupi.univs().getcatalog("01.03.02")
for univ in univs:
    print(univ)

# python postupi.py