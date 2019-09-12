from db import load_db

db = load_db()

for k, v in db.items():
    if len(v["categories"]) == 0 and \
            "#перенаправление" not in v["wikitext"].lower() and \
            "#redirect" not in v["wikitext"].lower():
        print("http://dfwk.ru/" + v["title"] + "\" no category")
