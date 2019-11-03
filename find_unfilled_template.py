from db import load_db
import sys
import re

db = load_db()

if len(sys.argv) < 2:
    print("usage", sys.argv[0], "template count/field")
    exit()

template_name, arg = sys.argv[1].lower(), sys.argv[2].lower()


def parse_page(page):
    result = dict()
    text = page["wikitext"].lower()
    if template_name not in text:
        return {}

    regexp = "{{" + template_name + ".*?}}"


match_list = dict()
for i in db.values():
    match_list.update(parse_page(i))
