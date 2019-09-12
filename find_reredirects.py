from util import load_db, find_redirect_and_not_redirect_pages, generate_name_id

db = load_db()

redirect_dict, non_redirect_dict, broken_dict = find_redirect_and_not_redirect_pages(db)
ni_list = generate_name_id(redirect_dict)

for k, v in redirect_dict.items():
    if v["redirect"][0].lower() in ni_list.keys():
        print("\"http://dfwk.ru/" + v["title"] + "\" reredirect to " + v["redirect"][0])
