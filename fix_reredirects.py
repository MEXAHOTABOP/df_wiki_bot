from util import load_db, find_redirect_and_not_redirect_pages, generate_name_id, init_wiki

db = load_db()
redirect_dict, _, _ = find_redirect_and_not_redirect_pages(db)
ni_redirect, ni_db = generate_name_id(redirect_dict), generate_name_id(db, False)
fixed_redirects = {}
wiki = init_wiki()


# рекурсивная функция которая находит страницы на которые ссылаются редиректы
# убрал поиск группами из за перенаправлений с #
def fix_redirect(obj, orig_name=None, redirection_counter=0, suffix=None):
    if orig_name is None:
        orig_name = obj["title"]

        redirect = obj["wikitext"].split("#")
        if len(redirect) > 2:
            redirect = obj["wikitext"].split("#")
            suffix = "#" + redirect[2].replace("]]", "")
        else:
            suffix = ""

    redirection_counter += 1

    if obj["title"].lower() == obj["redirect"][0].lower():  # игнорируем редиректы с разницой только в регистре
        return None, None, None                            # что бы не уйти в рекурсию

    if len(obj["redirect"]) > 0 and obj["redirect"][0].lower() in ni_redirect.keys():
        return fix_redirect(db[ni_redirect[obj["redirect"][0].lower()]], orig_name, redirection_counter, suffix=suffix)
    else:
        return orig_name, obj["redirect"][0] + suffix, redirection_counter


# генерация исправленного списка страница > цель
for k, v in redirect_dict.items():
    name, target, redir_c = fix_redirect(v)
    if name is not None and redir_c > 1:
        # print(name + " >  " + target)
        fixed_redirects.update({name: target})

token = wiki.token()
for k, v in fixed_redirects.items():
    text = "#перенаправление [[" + v + "]]"
    wiki("edit", pageid=ni_db[k], watchlist="unwatch", minor=1, bot=1, token=token, text=text)
