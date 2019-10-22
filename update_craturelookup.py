import pywikiapi
import wikitextparser as wtp
from util import load_db, init_wiki

db = load_db()
wiki = init_wiki()
token = wiki.token()
wiki_en = pywikiapi.Site(url="https://dwarffortresswiki.org/api.php")


# составляем список страниц с шаблоном
def create_list():
    match_list = dict()
    for k, v in db.items():
        if "{{Creaturelookup/0".lower() in v["wikitext"].lower():
            if len(v["langlinks"]) == 0:
                print(v["title"], "missed langlink")
                continue
            if "{{Creatures}}".lower() not in v["wikitext"].lower():
                print(v["title"], "missed {{Creatures}} template")
                continue
            match_list.update({k: v})
    return match_list


# получаем англ версию страницы в случае ошибки возвращаем {}
def parse_en_wiki(name):
    try:
        en_wiki_page = wiki_en("parse", page=name, prop="wikitext|langlinks", redirects=1)
    except pywikiapi.utils.ApiError as ex:
        try:
            if ex.data["code"] == "missingtitle":
                print(name, "not found")
                return {}
            if ex.message == "Call failed":
                print(ex.data)
                return parse_en_wiki(name)
            print(name, "api exception")
            print(ex)
        except TypeError:
            return parse_en_wiki(name)
        return {}

    en_wiki_page = en_wiki_page["parse"]
    if len(en_wiki_page["langlinks"]) == 0:
        print(name, "missed langlink to ru wiki")
    if "{{Creaturelookup/0".lower() not in en_wiki_page["wikitext"].lower():
        print(name, "did not contain Creaturelookup/0 skipping")
        return {}

    return en_wiki_page


def find_template(page):
    template = wtp.parse(page["wikitext"]).templates
    for i in template:
        if i.normal_name(capitalize=True) == "Creaturelookup/0":
            return i
    return None


# обновляем шаблоны
def process_pages(ru_id, ru_page):
    en_name = ru_page["langlinks"][0]["title"]
    en_page = parse_en_wiki(en_name)
    if len(en_page) == 0:
        print("err from", ru_page["title"])
        return

    template_ru = find_template(ru_page)
    template_en = find_template(en_page)
    if template_en is None:
        print(ru_page["title"], "something wrong")
        return

    wiki_lnk = "no"
    if template_ru.has_arg("wiki"):
        wiki_lnk = template_ru.get_arg("wiki").value
    template_en.del_arg("wiki")  # не интересует куда вела англ ссылка

    need_update = False
    for arg_en in template_en.arguments:
        if arg_en.name == "contrib":
            continue
        arg_ru = template_ru.get_arg(arg_en.name)
        if arg_ru is None or arg_ru.value != arg_en.value:
            need_update = True
            break
    if not need_update:
        return

    template_en.set_arg("wiki", wiki_lnk)
    print("tml-orig:", template_ru)
    print("tml-en:", template_en)
    new_wikitext = ru_page["wikitext"].replace(str(template_ru), str(template_en))
    print("newwikitext:", new_wikitext)
    try:
        wiki("edit", pageid=ru_id, watchlist="unwatch", minor=1, bot=1, token=token,
             summary="обновление Creaturelookup/0", text=new_wikitext)
    except pywikiapi.utils.ApiError as ex:
        print(ex)


for key, val in create_list().items():
    process_pages(key, val)
