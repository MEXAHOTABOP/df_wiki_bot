from util import load_db, generate_name_id, init_wiki

db = load_db()
ni_db = generate_name_id(db, False)
wiki = init_wiki()

redirect_pages = dict()
#  сбор списка новых страниц перенаправлений на версии
for i in ni_db.keys():
    if "Версия" in i and "/" in i and i[-3:-2] == ".":  # для других форматов править или заменить на регэксп
        version = i.split("/")[1]
        redirect_pages[version] = i
        redirect_pages["Release information/" + version] = i

# удаление существующих страниц из списка
redirect_pages_b = redirect_pages.copy()
for i in redirect_pages_b.keys():
    if i in ni_db:
        redirect_pages.pop(i)


token = wiki.token()
for k, v in redirect_pages.items():
    text = "#перенаправление [[" + v + "]]"
    wiki("edit", title=k, watchlist="unwatch", minor=1, bot=1, token=token, text=text)
