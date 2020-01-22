import wikitextparser as wtp
from util import load_db
db = load_db()

topic_page = db[11931]  # id страницы Topic
topic_parsed = wtp.parse(topic_page["wikitext"])
header = "{| class = \"wikitable sortable\" style=\"width: 80%\"\n\
! scope=\"col\" style=\"width: 16%;\" | Тема\n\
! scope=\"col\" style=\"width: 16%;\" | Перевод\n\
! scope=\"col\" style=\"width: 33%;\" | Описание\n\
! scope=\"col\" style=\"width: 16%;\" | Статья в Википедии\n\
! scope=\"col\" style=\"width: 9%;\" | Категория\n\
! scope=\"col\" style=\"width: 9%;\" | Навык исследователя\n"
result = dict()
for table in topic_parsed.tables:
    first_row = True
    for row in table.data():
        if first_row:  # пропускаем заголовок
            first_row = False
            continue
        for skill in row[5].split(", "):
            page_name = skill.split("|")[0].replace("[[", "")
            if page_name not in result:
                result[page_name] = list()
            result[page_name].append(row)


with open("tables", "w") as file:
    for skill, table_list in result.items():
        skill_table = header
        for row in table_list:
            skill_table += "|-\n"
            for cell in row:
                skill_table += "|" + cell + "\n"
        skill_table += "|}\n\n\n\n\n\n"
        file.write("http://dfwk.ru/index.php?title=" + skill + "\n")
        file.write(skill_table)
