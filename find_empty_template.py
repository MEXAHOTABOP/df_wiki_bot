from db import load_db
import sys
import re

db = load_db()

if len(sys.argv) < 1:
    print("usage", sys.argv[0], "template")
    exit()

template_name = sys.argv[1].lower()
regexp = re.compile("{{" + template_name + ".*?}}", flags=re.DOTALL)


def parse_page(page):
    result = dict()
    text = page["wikitext"].lower()
    if template_name not in text:
        return {}

    re_results = regexp.findall(text)
    for j in re_results:
        if "|" in j:
            result.update({page["title"]: len(j.split("|"))})
        else:
            result.update({page["title"]: 0})
    return result


match_list = dict()
for i in db.values():
    match_list.update(parse_page(i))

for k, v in match_list.items():
    if v == 0:
        print("http://dfwk.ru/" + k)
