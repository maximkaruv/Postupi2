from modules.parser import Parser
from types import SimpleNamespace as DictIt
import re


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
