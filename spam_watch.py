from util import init_wiki
import discord
import asyncio
import pywikiapi.utils
import os
import re

wiki = init_wiki(False)
bot_token = os.environ["BOT_TOKEN"]
channel_text_id = os.environ["CHANNEL_ID"]
client = discord.Client()
channel_text = ""
timestamp = "20010115145600"


# проверка известных паттернов спамботов
re_popular_spambot = re.compile("[A-Z][a-z]{4,8}")  # самый агрессивный из этих парней


def check_nickname(name):
    global re_popular_spambot

    if re_popular_spambot.fullmatch(name) is not None:
        return True
    return False


def is_first_action(name):
    try:
        change_list = wiki("query", list="usercontribs", ucuser=name, ucprop="sizediff")
    except (TypeError, pywikiapi.utils.ApiError) as ex:
        print(ex)
        return is_first_action(name)

    if len(change_list["query"]["usercontribs"]) == 1:
        return True
    return False


def get_log():
    global timestamp

    try:
        return wiki("query", list="recentchanges", rcend=timestamp,
                    rcshow="!bot", rcprop="user|title|timestamp", rctype="new|edit", rclimit=50)
    except Exception as ex:  # слишком много исключений потенциально могут быть
        print(ex)
        return None


async def delete_page(title, nick, reason):
    reason_list = {
        1: "создание страниц без аккаунта запрещено",
        2: "создание новой страницы с подозрительным никнеймом"
    }
    page = wiki("parse", page=title, prop="wikitext")["parse"]["wikitext"].replace("http", "")
    wiki("delete", title=title, reason=reason_list[reason], token=wiki.token(), POST=True)
    msg = "**удалено:** `" + title + "` **автор**: <http://dfwk.ru/Служебная:Заблокировать/" + nick + \
          "> **причина:** `" + reason_list[reason] + "` **содержание:**" + page[:100] + "..."
    await channel_text.send(msg)


async def main_loop():
    global timestamp
    while True:
        await asyncio.sleep(10)
        log_json = get_log()
        if log_json is None:
            continue
        log_json = log_json["query"]["recentchanges"]

        if len(log_json) and timestamp != log_json[0]["timestamp"]:
            timestamp = log_json[0]["timestamp"]
            for i in log_json:
                # новые страницы
                if i["type"] == "new":
                    # пользователи без авторизации
                    if "anon" in i:
                        # print(i)
                        await delete_page(i["title"], i["user"], 1)
                        continue
                    # спам боты по паттерну
                    if check_nickname(i["user"]) and is_first_action(i["user"]):
                        # print(i)
                        await delete_page(i["title"], i["user"], 2)
                        continue

#  копипаста
@client.event
async def on_ready():
    global client
    global channel_text
    global channel_text_id

    print("ник {}".format(client.user.name))

    # выбор текстового канала
    channel_text = client.get_channel(int(channel_text_id))
    print("текстовый канал {}".format(channel_text.name))

    client.loop.create_task(main_loop())

client.run(bot_token)
