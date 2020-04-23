from util import init_wiki
import discord
import asyncio
import pywikiapi.utils
import os
import re

# проверка известных паттернов спамботов
# WwordNNWword WwordNN Wordd 
mainspace_spambots = re.compile("(?:[a-zA-Z]+[0-9]{1,2}[a-zA-Z]+|[a-zA-Z]+[0-9]{1,2}|[A-Z][a-z]{4,9})")
# Woooooooord WooordNNNN
userspace_spambots = re.compile("(?:[A-Z][a-z]{9,13}|[A-Z][a-z]{4,8}[0-9]{4})")


class SpamWatch(discord.Client):
    def __init__(self):
        super().__init__()
        self.timestamp = "20010115145600"
        self.wiki = init_wiki(False)
        self.channel_text = self.get_channel(int(os.environ["CHANNEL_ID"]))
        self.main_loop = self.loop.create_task(self.main_loop())

    def check_nickname(self, name, page_name):
        global mainspace_spambots
        global userspace_spambots

        if mainspace_spambots.fullmatch(name) is not None or \
                userspace_spambots.fullmatch(name) and "Участник:" in page_name:
            return True
        return False

    def is_less_then_five_actions(self, name):
        try:
            change_list = self.wiki("query", list="usercontribs", ucuser=name, ucprop="sizediff")
        except (TypeError, pywikiapi.utils.ApiError) as ex:
            print(ex)
            return self.is_less_then_five_actions(name)

        if len(change_list["query"]["usercontribs"]) < 5:
            return True
        return False

    def get_log(self):
        try:
            return self.wiki("query", list="recentchanges", rcend=self.timestamp,
                             rcshow="!bot", rcprop="user|title|timestamp", rctype="new|edit", rclimit=50)
        except Exception as ex:  # слишком много исключений потенциально могут быть
            try:
                print(ex)
            except TypeError:
                print("pywikiapi ex")
            return None

    async def delete_page(self, title, nick, reason):
        reason_list = {
            1: "создание страниц без аккаунта запрещено",
            2: "создание новой страницы с подозрительным никнеймом"
        }
        page = self.wiki("parse", page=title, prop="wikitext")["parse"]["wikitext"].replace("http", "")
        try:
            self.wiki("delete", title=title, reason=reason_list[reason], token=self.wiki.token(), POST=True)
        except pywikiapi.utils.ApiError as ex:
            if ex.data["code"] == "badtoken":
                await asyncio.sleep(2)
                self.wiki = init_wiki(False)
                return self.delete_page(title, nick, reason)
        msg = "**удалено:** `" + title + "` **автор**: <http://dfwk.ru/Служебная:Заблокировать/" + nick + \
              "> **причина:** `" + reason_list[reason] + "` **содержание:**" + page[:100] + "..."
        await self.send_message(msg)

    async def send_message(self, msg):
        try:
            await self.channel_text.send(msg)
        except Exception as e:
            print(e)
            await asyncio.sleep(2)
            return self.send_message(msg)

    async def main_loop(self):
        await self.wait_until_ready()
        while True:
            await asyncio.sleep(10)
            log_json = self.get_log()
            if log_json is None:
                continue
            log_json = log_json["query"]["recentchanges"]

            if len(log_json) and self.timestamp != log_json[0]["timestamp"]:
                timestamp = log_json[0]["timestamp"]
                for i in log_json:
                    # новые страницы
                    if i["type"] == "new":
                        # пользователи без авторизации
                        if "anon" in i:
                            # print(i)
                            await self.delete_page(i["title"], i["user"], 1)
                            continue
                        # спам боты по паттерну
                        if self.check_nickname(i["user"], i["title"]) and self.is_less_then_five_actions(i["user"]):
                            # print(i)
                            await self.delete_page(i["title"], i["user"], 2)
                            continue


def run():
    try:
        client = SpamWatch()
        client.run(os.environ["BOT_TOKEN"])
    except Exception as ex:
        print(ex)
        asyncio.sleep(10)
        return run()


run()
