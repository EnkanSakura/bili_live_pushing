# coding: utf8

import time
import threading
import json
import asyncio
import pyppeteer
import configparser
from bilibili_api import user, live, dynamic, Verify, exceptions

usr = 4275270
room = 210479
live_url = 'http://api.live.bilibili.com/room/v1/Room/room_init?id={}'
info_url = 'http://api.live.bilibili.com/live_user/v1/Master/info?uid={}'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/32.0.1700.76 Safari/537.36'
}


class LiveStatus:
    def __init__(self):
        self.ini = configparser.ConfigParser()
        self.ini.read("live_status.ini", encoding="utf-8")

    def read(self, rid):
        if isinstance(rid, int):
            rid = str(rid)
        return self.ini.get(rid, "status"), self.ini.get(rid, "dynamic")

    def write(self, rid, status, dynamicid):
        if isinstance(rid, int):
            rid = str(rid)
        if isinstance(status, int):
            status = str(status)
        if isinstance(dynamicid, int):
            dynamicid = str(dynamicid)
        self.ini.set(rid, "status", status)
        self.ini.set(rid, "dynamic", dynamicid)
        with open("live_status.ini", "w+") as f:
            self.ini.write(f)


async def get_title(rid):
    browser = await pyppeteer.launch()
    page = await browser.newPage()
    await page.goto("https://live.bilibili.com/{}".format(rid))
    title = await (
        await (
            await page.querySelector(
                "#head-info-vm > div > div > div.room-info-upper-row.p-relative > div.normal-mode > div:nth-child(1) > h1 > span.title-length-limit.live-skin-main-text.v-middle.dp-i-block.small-title"
            )
        ).getProperty('textContent')
    ).jsonValue()
    return title


def listen(uid, rid):
    try:
        status = live.get_room_play_info(rid)['live_status']
        pre = time.strftime("%H:%M:%S", time.localtime())
    except exceptions.BilibiliApiException:
        print("Exception")
    else:
        if status == 1:
            print("{0}\t\t{1}\t\t\t{2}".format(pre, user.get_user_info(uid)['name'], "直播中……"))
            room_title = asyncio.get_event_loop().run_until_complete(get_title(rid))
            return "群友 @{}  开始直播啦\n直播间标题：{}\n直播间地址：https://live.bilibili.com/{}".format(
                uid, room_title, rid)
        else:
            print("{0}\t\t{1}\t\t\t{2}".format(pre, user.get_user_info(uid)['name'], "没有直播"))
            return False


def main():
    live_status = LiveStatus()
    with open('./config.json', 'r', encoding="utf-8") as config:
        json_data = json.load(config)
        verify = Verify(json_data["BiliVerify"]["sessdata"], json_data["BiliVerify"]["csrf"])
        while True:
            for r in json_data["Live"]:
                dynamic_text = listen(r["uid"], r["rid"])
                status, dynamic_id = live_status.read(r["rid"])
                if dynamic_text and dynamic_id == "1":
                    dynamic_id = dynamic.send_dynamic(text=dynamic_text, verify=verify)["dynamic_id"]
                    live_status.write(r["rid"], "1", dynamic_id)
                if not dynamic_text and dynamic_id != "1":
                    dynamic.delete(dynamic_id=dynamic_id, verify=verify)
                    live_status.write(r["rid"], "0", "1")
                time.sleep(5)
            time.sleep(60)


if __name__ == '__main__':
    t = threading.Thread(target=main())
    t.start()
    print("Start Listing")
    t.join()
    main()
