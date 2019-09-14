from util import init_wiki
wiki = init_wiki()

categories = ("Страницы_без_категорий", "Страницы_без_интервики", "Тупиковые_страницы")  # категории страниц для обновы
page_id_list = set()

for i in categories:
    json = wiki("query", list="categorymembers", cmtitle="Категория:" + i, cmlimit="max")  # лимит для бота 5000 страниц
    for page in json["query"]["categorymembers"]:
        page_id_list.add(page["pageid"])

page_id_list = list(page_id_list)
parts = list()
limit_per_request = 100  # ботам можно до 500 но может не выполнить запрос
part_num = int(len(page_id_list) / limit_per_request) + 1

for i in range(1, part_num + 1):
    start = (i - 1) * limit_per_request if (i - 1) * limit_per_request > 0 else 0
    end = len(page_id_list) if len(page_id_list) < i * limit_per_request else i * limit_per_request
    parts.append(page_id_list[start:end])


for i in parts:
    id_string = str(i).replace("[", "").replace("]", "").replace(", ", "|")
    wiki("purge", pageids=id_string, forcerecursivelinkupdate=1)
