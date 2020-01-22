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
    global db
    if results is None:
        results = list()

    if target == "allpages":  # костыли
        next_cont = "gapcontinue"
        json = wiki("query", generator=target, rawcontinue=1, gaplimit=1000, gapfrom=continue_from,
                    prop="revisions", rvprop="ids")
    elif target == "allcategories":
        next_cont = "gaccontinue"
        json = wiki("query", generator=target, rawcontinue=1, gaclimit=1000, gacfrom=continue_from,
                    prop="revisions", rvprop="ids")
    else:  # alltransclusions
        next_cont = "gatcontinue"
        json = wiki("query", generator=target, rawcontinue=1, gatunique=1, gatlimit=1000, gatfrom=continue_from,
                    prop="revisions", rvprop="ids")

    for page in json["query"]["pages"]:
        if "pageid" in page and (page["pageid"] not in db or \
                page["revisions"][0]["revid"] != db[page["pageid"]]["revid"]):
            results.append(page["title"])

    if "query-continue" in json:
        return get_full_list(target=target, continue_from=json["query-continue"][target][next_cont], results=results)
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
        page_full_info = wiki("parse", page=name,
                              prop="wikitext|categories|langlinks|links|externallinks|revid|templates")
    except pywikiapi.utils.ApiError as ex:
        if ex.data["code"] == "missingtitle":  # игнорируем пустые категории
            return
    except TypeError:
        cur -= 1
        return parse_names(name)

    page_full_info = parse_redirects(page_full_info)
    page_id = page_full_info["parse"]["pageid"]
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
