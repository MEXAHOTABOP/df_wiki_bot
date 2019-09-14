import pywikiapi
import re
import progressbar
from multiprocessing.dummy import Pool
from util import load_db, save_db, init_wiki
wiki = init_wiki()
bar = None

cur = 1
db = dict()


# список всех страниц на вики
def get_all_lists():
    results = get_full_list(target="allpages")
    results = get_full_list(target="allcategories", results=results)
    results = get_full_list(target="alltransclusions", results=results)
    results.sort()
    return results


def get_full_list(target="", continue_from="", results=None):
    if results is None:
        results = list()
    if target == "allpages":  # костыли
        next_ap = "apcontinue"
        title = "title"
        json = wiki("query", list=target, rawcontinue=1, aplimit="max", apfrom=continue_from)
        prefix = ""
    elif target == "allcategories":
        next_ap = "accontinue"
        title = "category"
        json = wiki("query", list=target, rawcontinue=1, aclimit="max", acfrom=continue_from)
        prefix = "Категория:"
    else:  # alltransclusions
        next_ap = "atcontinue"
        title = "title"
        json = wiki("query", list=target, rawcontinue=1, atunique=1, atlimit="max", atfrom=continue_from)
        prefix = ""

    for name in json["query"][target]:
        results.append(prefix + name[title])

    if "query-continue" in json:
        return get_full_list(target=target, continue_from=json["query-continue"][target][next_ap], results=results)
    else:
        return results


def parse_redirects(page_full_info):
    text = page_full_info["parse"]["wikitext"]
    add = {"redirect": {}}
    if "#перенаправление" in text.lower() or \
            "#redirect" in text.lower():
        link = re.search("\[.+\]", text).group(0)
        link = link.replace("[", "")
        link = link.replace("]", "")
        add["redirect"].update({0: link})
    page_full_info["parse"].update(add)
    return page_full_info


def parse_names(name):
    global db
    global bar
    global cur

    bar.update(cur)
    cur += 1

    try:
        page_info = wiki("parse", page=name, prop="revid")["parse"]
    except pywikiapi.utils.ApiError as ex:
        try:
            if ex.data["code"] == "missingtitle":  # игнорируем пустые категории
                return
            if ex.message == "Call failed":
                print(ex.data)
                cur -= 1
                return parse_names(name)
            print(name + " api исключение ")
            print(ex)  # баги библиотеки
        except TypeError:
            cur -= 1
            return parse_names(name)
        return

    except Exception as ex:
        print(name + " неизвестное исключение ")
        print(ex)
        return

    page_id = page_info["pageid"]

    if page_id in db:  # надо закостылять используя action=query&prop=revisions&rvprop=ids
        if page_info["revid"] == db[page_id]["revid"]:  # актуально больше ничего делать не нужно
            return
        else:
            db.pop(page_id)
    try:
        page_full_info = wiki("parse", page=name,
                              prop="wikitext|categories|langlinks|links|externallinks|revid|templates")
    except (TypeError, pywikiapi.utils.ApiError):
        cur -= 1
        return parse_names(name)
    page_full_info = parse_redirects(page_full_info)

    page_full_info[page_id] = page_full_info.pop("parse")  # меняем парсер на id
    page_full_info[page_id].pop("pageid")  # удаляем ставший не нужным id
    db.update(page_full_info)
    if cur % 100 == 0:  # сохранение дб в прогрессе на всякий случай
        save_db(db)


# обновить бд
def update_db():
    global bar

    names = get_all_lists()
    bar = progressbar.ProgressBar(max_value=len(names), redirect_stdout=True)
    with Pool(10) as pool:
        pool.map(parse_names, names)


if __name__ == "__main__":
    db = load_db()
    update_db()
    save_db(db)
