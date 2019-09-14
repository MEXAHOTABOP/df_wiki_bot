from util import load_db, init_wiki, add_category
db = load_db()
wiki = init_wiki()
token = wiki.token()

for k, v in db.items():
    if len(v["categories"]) == 0 \
            and "#перенаправление" not in v["wikitext"].lower()\
            and "#redirect" not in v["wikitext"].lower()\
            and "Страницы_без_категорий" not in v["wikitext"]:
        add_category(wiki, token, k, "Страницы_без_категорий")

