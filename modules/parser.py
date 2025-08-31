from loguru import logger
import requests
import chardet
from lxml import html as htmlx
from lxml.html import HtmlElement
import re


class Elements:
    def __init__(self, elements):
        if isinstance(elements, HtmlElement):
            self.elements = [elements]
        else:
            self.elements = elements

    def __iter__(self):
        for el in self.elements:
            yield Elements(el)

    def __len__(self):
        return len(self.elements)
    
    def tag(self, index=0):
        return self.elements[index].tag

    def text(self, index=0, default=''):
        try:
            text = self.elements[index].text_content()
            text = text.replace('\xa0', ' ')
            text = re.sub(r'\s+', ' ', text).strip()
            if not text or all(c in '.·' for c in text):
                return default
            return text
        except IndexError:
            return default

    def attr(self, name, index=0, default=''):
        try:
            return self.elements[index].get(name, default)
        except IndexError:
            return default

    def select(self, selector):
        new_elements = []
        for el in self.elements:
            new_elements.extend(el.cssselect(selector))
        return Elements(new_elements)


class Tree:
    def __init__(self, content):
        if isinstance(content, str):
            self.tree = htmlx.fromstring(content)
        elif isinstance(content, HtmlElement):
            self.tree = content
        else:
            raise ValueError("Tree странный объект")

    def select(self, selector):
        elements = self.tree.cssselect(selector)
        return Elements(elements)


class Parser:
    def getpage(self, link):
        try:
            res = requests.get(link)
            res.raise_for_status()
            encoding = chardet.detect(res.content)['encoding']
            html = res.content.decode(encoding, errors='replace')

            with open('last-fetch.html', 'w', encoding='utf-8') as file:
                file.write(html)
            return html
        
        except Exception as e:
            logger.error(f"Не удалось запросить страницу: {e}")
            return None
    
    def newtree(self, content):
        return Tree(content)