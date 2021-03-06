from util import load_db, init_wiki, add_category
db = load_db()
wiki = init_wiki()
token = wiki.token()

for k, v in db.items():
    if len(v["links"]) == 0 \
            and "Шаблон" not in v["title"] \
            and "Категория" not in v["title"]\
            and "Тупиковые_страницы" not in v["wikitext"]:
        add_category(wiki, token, k, "Тупиковые_страницы")
