from db import load_db

db = load_db()

for k, v in db.items():
    if len(v["links"]) == 0:
        print("http://dfwk.ru/" + v["title"] + "\" no links")
