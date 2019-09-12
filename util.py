import pickle
import pywikiapi
import os


# загрузить дб
def load_db():
    try:
        with open("db.pkl", "rb") as f:
            return pickle.load(f)
    except IOError:  # нет файла
        return dict()


# сохранить дб
def save_db(data_base):
    with open("db.pkl", "wb") as f:
        pickle.dump(data_base, f)


# создать словари с редиректами, не редиректами, и сломанными редиректами
def find_redirect_and_not_redirect_pages(db):
    non_redirect_dict = db.copy()
    redirect_dict = {}
    broken_dict = {}
    for k, v in db.items():  # удаляем перенаправления из основного списка и переносим в новый
        if len(v["redirect"]) != 0:
            if not v["links"][0].get("exists", False):  # я все ещё не уверен работает ли эта переменная
                broken_dict.update({k: non_redirect_dict.pop(k)})
                continue
            non_redirect_dict[k]["redirect"][0] = v["redirect"][0].split("#")[0]
            redirect_dict.update({k: non_redirect_dict.pop(k)})
    return redirect_dict, non_redirect_dict, broken_dict


# сгенерировать словарь с парами имя, id
def generate_name_id(db, lower=True):
    ni_db = {}
    for k, v in db.items():
        ni_db.update({v["title"].lower(): k} if lower else {v["title"]: k})
    return ni_db


def init_wiki():
    wiki = pywikiapi.Site(url="http://dfwk.ru/api.php")
    wiki.no_ssl = True
    if not os.environ["BOT_LOGIN"] or not os.environ["BOT_PASSWORD"]:
        print("env BOT_LOGIN or BOT_PASSWORD not set")
    wiki.login(os.environ["BOT_LOGIN"], os.environ["BOT_PASSWORD"], True)
    return wiki
