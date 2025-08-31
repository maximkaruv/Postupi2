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
                    # если один HtmlElement, оборачиваем в список
                    if isinstance(elements, HtmlElement):
                        self.elements = [elements]
                    else:
                        self.elements = elements

                def __iter__(self):
                    for el in self.elements:
                        yield Elements(el)  # возвращаем обёрнутый элемент

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
            def get_catalog(self, spec_code, page=1):
                html = parser.getpage(
                    f"https://postupi.online/specialnost/{spec_code}/vuzi/?page_num={page}"
                )
                tree = parser.newtree(html)
                cards = tree.select('.list-cover > ul > li.list')

                for card in cards:
                    title = card.select('h2 > a').text()
                    link = card.select('h2 > a').attr('href')

                    city_id, univ_id = '', ''
                    match = re.search(r'https://(.*?)\.postupi\.online/vuz/(.*?)/', link)
                    if match:
                        city_id = match.group(1)
                        univ_id = match.group(2)

                    metadata = card.select('.list__pre > span')
                    if len(metadata) <= 2:
                        city = metadata.text(index=0)
                    else:
                        city = metadata.text(index=1)
                    
                    learning_cost = card.select('.list__price > b').text()

                    budget_places, paid_places = '', ''
                    for i in range(0, 4):
                        row_title = card.select('div.list__score-wrap span.hidden-mid').text(index=i)
                        row_value = card.select('div.list__score-wrap b').text(index=i)

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
    
    def programs(self, city_id, univ_id):
        class Programs:
            def get_catalog(self, spec_code):
                html = parser.getpage(
                    f"https://{city_id}.postupi.online/vuz/{univ_id}/specialnost/{spec_code}/programmy-obucheniya/forma-ochno/"
                )
                tree = parser.newtree(html)
                cards = tree.select('.list-cover > ul > li.list')

                for card in cards:
                    title = card.select('h2 > a').text()
                    link = card.select('h2 > a').attr('href')

                    match = re.search(r'programma/(.*?)/', link)
                    prog_id = match.group(1) if match else ''

                    learning_cost = card.select('.list__price > b').text()

                    budget_places, paid_places = '', ''
                    budget_score, paid_score = '', ''
                    for i in range(0, 4):
                        row_title = card.select('div.list__score-wrap span.hidden-mid').text(index=i)
                        row_value = card.select('div.list__score-wrap b').text(index=i)

                        if "мест" in row_title:
                            if "бюджет" in row_title:
                                budget_places = row_value
                            elif "платно" in row_title:
                                paid_places = row_value
                        elif "бал" in row_title:
                            if "бюджет" in row_title:
                                budget_score = row_value
                            elif "платно" in row_title:
                                paid_score = row_value

                    yield DictIt(
                        title=title,
                        prog_id=prog_id,
                        link=link,
                        learning_cost=learning_cost,
                        budget_places=budget_places,
                        paid_places=paid_places,
                        budget_score=budget_score,
                        paid_score=paid_score
                    )
            
            def get_details(self, prog_id):
                html = parser.getpage(
                    f"https://{city_id}.postupi.online/vuz/{univ_id}/programma/{prog_id}/"
                )
                tree = parser.newtree(html)
                description = tree.select('.descr-max > *')

                decs, subs = [], []
                get_next_ul = False

                for element in description:
                    match element.tag():

                        case 'p':
                            text = element.text()
                            if len(text) > 40:
                                decs.append(text)
                            elif "Основн" in text:
                                get_next_ul = True
                        
                        case 'ul':
                            if get_next_ul:
                                for sub in element.select('li'):
                                    subs.append(sub.text())
                                get_next_ul = False

                decs = '\n\n'.join(decs)

                return DictIt(
                    description=decs,
                    subjects=subs
                )

        return Programs()


postupi = PostupiAPI()

# univs = postupi.univs().get_catalog("01.03.02")
# for univ in univs:
#     print(univ)

# namespace(title='Российский экономический университет имени Г.В. Плеханова', univ_id='reu-im-g-v-plehanova', link='https://msk.postupi.online/vuz/reu-im-g-v-plehanova/', city='Москва', city_id='msk', learning_cost='157 000', budget_places='1 347', paid_places='3 160')



# progs = postupi.programs('msk', 'reu-im-g-v-plehanova').get_catalog("01.03.02")
# for prog in progs:
#     print(prog)

# namespace(title='Интеллектуальный анализ данных и поддержка принятия решений', prog_id='11887', link='https://msk.postupi.online/vuz/reu-im-g-v-plehanova/programma/11887/', learning_cost='360 000', budget_places='5', paid_places='18', budget_score='94', paid_score='80')



#print(postupi.programs('msk', 'reu-im-g-v-plehanova').get_details('11887'))

# namespace(description='Студенты этой программы изучают широкий спектр тем, связанных с обработкой и анализом данных, а также созданием интеллектуальных систем. Они изучают основы программирования, алгоритмы и структуры данных, базы данных и SQL. Кроме того, они получают знания в области статистики и вероятности, машинного обучения, искусственного интеллекта и глубокого обучения. Программа также включает изучение методов визуализации данных и разработку навыков работы с большими объемами информации. Студенты учатся применять эти знания для решения реальных проблем и задач, связанных с анализом данных и разработкой интеллектуальных систем. В результате обучения выпускники программы готовы эффективно работать с данными, использовать инструменты и методы анализа данных, а также создавать интеллектуальные системы, способные автоматизировать и оптимизировать процессы на основе данных.\n\nДисциплины специализации, с оанных, а также создавать интеллектуальные системы, способные автоматизировать и оптимизировать процессы на основе данных.\n\nДисциплины специализации, с одной стороны, дают фундаментальные основы интеллектуальных систем, а с другой стороны знакомят с самыми современными инструментами исследователей и аналитдной стороны, дают фундаментальные основы интеллектуальных систем, а с другой стороны знакомят с самыми современными инструментами исследователей и аналитиков в области интеллектуального анализа данных.', subjects=['Искусственный интеллект (Artificial Intelligent) и разработка интеллектуальных систем (Intelligent Systems Development).', 'Методы анализа «больших данных» (Big Data Analysis), майнинг данных (Data Mining) и визуализация данных (Data Visualization).', 'Машинное обучение (Machine Learning).', 'Анализ формальных понятий (Formal Concept Analysis).', 'Анализ сетей (Network Analysis) и прикладная теория графов (Applied Graph Theory).', 'Онтологическое моделирование (Ontology Engineering) и семантические технологии (Semantic Technologies).', 'Мультимодальная кластеризация (Multi-Modal Clustering) и рекомендательные системы (Recommender Systems).', 'Автоматическая обработка текста (Natural Language Processing) и распознавание образов (Pattern Recognition).'])

### python postupi.py ###