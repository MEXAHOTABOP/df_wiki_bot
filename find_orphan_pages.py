from util import load_db, find_redirect_and_not_redirect_pages

db = load_db()

redirect_dict, non_redirect_dict, broken_dict = find_redirect_and_not_redirect_pages(db)


for k, v in non_redirect_dict.items():
    found = False
    title = v["title"].lower()
    #if title[-4:] == ".txt":  # не проверяем .txt
    #    continue

    for k2, v2 in non_redirect_dict.items():
        if "категория" in title:
            for lst in v2["categories"]:
                if title.replace("категория:", "").replace(" ", "_") == lst["category"].lower():
                    found = True
                    break
        for lst in v2["templates"]:
            if title == lst["title"].lower():
                found = True
                break
        for lst in v2["links"]:
            if title == lst["title"].lower():
                found = True
                break
        if found:
            break

    if not found:
        print("\"http://dfwk.ru/" + v["title"] + "\" orphan")