# 简介

---

一个简单的Python程序

名单内用户开播时，指定账号自动发送开播提醒动态

# 配置

---

使用轮子：

- [bilibili_api](https://github.com/Passkou/bilibili_api/)

- BeautifulSoup4

- pyppeteer

用pip配置环境：

```commandline
pip install -r requirements.txt
```

# 使用

---

1.`sample_config.json`：认证信息，监听名单

```json
{
  "BiliVerify": {
    "//": "",
    "sessdata": "",
    "csrf": ""
  },
  "Live": [
    {
      "//": "",
      "uid": 1,
      "rid": 1
    },
    {
      "//": "",
      "uid": 2,
      "rid": 2
    }
  ]
}

```

获取 SESSDATA 和 CSRF 后填入`BiliVerift`

`Live`内填写监听的主播`uid`和直播间号`room_id`

2.`sanple_live_status.ini`：存储直播间状态数据

```ini
[room_id_here]
status = 0
dynamic = 1
```

配置后运行`run.py`即可
