from util import load_db
import re

db = load_db()


def find_pages_with_cat():
    page_list = []
    for v in db.values():
        if len(v["categories"]):
            for i in v["categories"]:
                if (i["category"] == "Вредители" or i["category"] == "Растения") and "Категория" not in v["title"]:
                    page_list.append(v)
    return page_list


def check_pages():
    page_list = find_pages_with_cat()
    for i in page_list:
        name = re.search("\'\'\'.+?\'\'\'", i["wikitext"]).group(0)
        if len(name) - 6 < 5:  # если меньше 5 символов то берём целое название -1 символ иначе максимум 5 символов
            short_name = name[3:len(name) - 4]
        else:
            short_name = name[3:8]
        pattern = "некоторы[ем].+?дварф(ы|ам).+?(любят|нрав[ия]тся|предпочитают).+?" + short_name.lower() + ".+?за.+\."
        like = re.search(pattern, i["wikitext"].lower())
        if like is None:
            pattern_have = "некоторы[ем].+?дварф(ы|ам).+?(любят|нрав[ия]тся|предпочитают).+?за.+\."
            have = re.search(pattern_have, i["wikitext"].lower())
            have_str = "Но ничего не нашел"
            if have is not None:
                have_str = "Получил: " + have.group(0)
            print("\"http://dfwk.ru/index.php?title=" + i["title"] + "\"", "Ожидал:", name, "ака:", short_name.lower(), have_str)


check_pages()
