from database.table import CsvTable
from postupi.api import PostupiAPI
from logs.logger import setlogger, logger


univs_db = CsvTable('data/universities.csv', ['id', 'title', 'link', 'city', 'city_id', 'learning_cost', 'budget_places', 'paid_places'])
progs_db = CsvTable('data/programs.csv', ['id', 'title', 'link', 'learning_cost', 'budget_places', 'paid_places'])
subs_db = CsvTable('data/subjects.csv', ['id', 'title'])

univs_progs_db = CsvTable('data/univs-progs.csv', ['university-id', 'program-id'])
progs_subs_db = CsvTable('data/progs-subs.csv', ['program-id', 'subject-id'])

setlogger('logs/main.log')
postupi = PostupiAPI()

spec_codes = ["01.03.02", ...]


def main():
    for spec_code in spec_codes:
        logger.info(f"Специальность: {spec_code}")

        for page in range(1, 21):
            logger.info(f"Страница: {page}")

            univs = postupi.univs().get_catalog(spec_code, page)
            logger.success(f"Получен список из {len(univs)} вузов")

            if univs.current_page != page:
                logger.warning(f"Достигнута последняя страница: {page-1}")
                break

            univs.next()

            for univ in univs:
                logger.info(f"Вуз: \"{univ.title}\"")

                programs = postupi.programs(univ.city_id, univ.id)

                progs = programs.get_catalog(spec_code)
                logger.success(f"Получен список из {len(progs)} программ")

                for prog in progs:
                    logger.info(f"Программа: \"{prog.title}\"")

                    details = programs.get_details(prog.id)
                    logger.success(f"Детали программы: \"{details.decs[:20]}..\"")


if __name__ == '__main__':
    main()