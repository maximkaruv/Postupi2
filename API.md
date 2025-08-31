# Каталог вузов

`https://postupi.online/specialnost/01.03.02/vuzi/?page_num=1`
`01.03.02` - специальность
`1` - текущая страница

## Карточки вузов

`.list-cover > ul > li`

Превью: `div.list__img-wrap > a > img` (src)

Название вуза: `h2 > a`

Ссылка на страницу вуза: `h2 > a` (href)
`https://spb.postupi.online/vuz/spbpu/`
`spb` - город
`spbpu` - код вуза

Город вуза: `.list__pre > span`[0] (если span-ов <= 2 иначе [1])

Стоимость обучения: `.list__price > b`

Кол-во бюджетных мест: `div.list__score-wrap b`[?]
"мест|бюджет" - `div.list__score-wrap span.hidden-mid`[?]

Кол-во платных мест: `div.list__score-wrap b`[?]
"мест|платно" - `div.list__score-wrap span.hidden-mid`[?]

# Каталог программ обучения по специальности в вузе

`https://spb.postupi.online/vuz/spbpu/specialnost/01.03.02/programmy-obucheniya/forma-ochno/`
`spb` - город
`spbpu` - код вуза
`02.03.02` - специальность

## Программы обучения

`.list-cover > ul > li`

Название программы: `h2 > a`

Ссылка на страницу программы: `h2 > a` (href)
`https://spb.postupi.online/vuz/spbpu/programma/29/`
`spb` - город
`spbpu` - код вуза
`29` - айди программы

Стоимость обучения: `.list__price > b`

Балл ЕГЭ на бюджет: `div.list__score-wrap b`[?]
"бал|бюджет" - `div.list__score-wrap span.hidden-mid`[?]

Балл ЕГЭ на платное: `div.list__score-wrap b`[?]
"бал|платно" - `div.list__score-wrap span.hidden-mid`[?]

Кол-во бюджетных мест: `div.list__score-wrap b`[?]
"мест|бюджет" - `div.list__score-wrap span.hidden-mid`[?]

Кол-во платных мест: `div.list__score-wrap b`[?]
"мест|платно" - `div.list__score-wrap span.hidden-mid`[?]

# Страница программы обучения

`https://spb.postupi.online/vuz/spbpu/programma/29/`

Описание программы: `.descr-max`
Формат описания:
p.../p
...
p.../p
p`Основные профессиональные дисциплины:`/p
ul[] -> li../li
