import sys
import time
from configparser import ConfigParser
import pypinyin
import requests
from pathlib import Path

TAGS = {
    "Anime": "动画",
    "Action": "动作",
    "Mystery": "悬疑",
    "Tv Movie": "电视电影",
    "Animation": "动画",
    "Crime": "犯罪",
    "Family": "家庭",
    "Fantasy": "奇幻",
    "Disaster": "灾难",
    "Adventure": "冒险",
    "Short": "短片",
    "Horror": "恐怖",
    "History": "历史",
    "Suspense": "悬疑",
    "Biography": "传记",
    "Sport": "运动",
    "Comedy": "喜剧",
    "Romance": "爱情",
    "Thriller": "惊悚",
    "Documentary": "纪录",
    "Indie": "独立",
    "Music": "音乐",
    "Sci-Fi": "科幻",
    "Western": "西部",
    "Children": "儿童",
    "Martial Arts": "武侠",
    "Drama": "剧情",
    "War": "战争",
    "Musical": "歌舞",
    "Film-noir": "黑色",
    "Science Fiction": "科幻",
    "Film-Noir": "黑色",
    "Food": "饮食",
    "War & Politics": "战争与政治",
    "Sci-Fi & Fantasy": "科幻",
    "Mini-Series": "迷你剧",
    "Reality": "真人秀",
    "Home and Garden": "家居与园艺",
    "Game Show": "游戏",
    "Awards Show": "颁奖典礼",
    "News": "新闻",
    "Talk": "访谈",
    "Talk Show": "脱口秀",
    "Travel": "旅行",
    "Soap": "肥皂剧",
}

TYPE = {"movie": 1, "show": 2, "artist": 8, "photo":99} #99随手写的，不知道官方代码是多少

config_file: Path = Path(__file__).parent / 'config.ini'


def has_chinese(string):
    """判断是否有中文"""
    for char in string:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False


def convert_to_pinyin(text):
    """将字符串转换为拼音首字母形式。"""
    str_a = pypinyin.pinyin(text, style=pypinyin.FIRST_LETTER)
    str_b = [str(str_a[i][0]).upper() for i in range(len(str_a))]
    return ''.join(str_b).replace("：", ":").replace("（", "(").replace("）", ")").replace("，", ",")


class PlexServer:

    def __init__(self):
        cfg = ConfigParser()
        self.s = requests.session()

        try:
            cfg.read(config_file)
            self.host = dict(cfg.items("server"))["host"]
            self.token = dict(cfg.items("server"))["token"]
            print(f"已成功连接到服务器: {self.login()}\n")
        except Exception as error:
            print(error)
            print("\n配置文件读取失败，开始创建配置文件...\n")
            self.host = input('请输入您的 Plex 服务器地址 (例如 http://127.0.0.1:32400): ') or "http://127.0.0.1:32400"
            if self.host[-1] == "/":
                self.host = self.host[:-1]
            self.token = input('请输入您的 X-Plex-Token: ')
            try:
                cfg.add_section("server")
                cfg.set("server", "host", self.host)
                cfg.set("server", "token", self.token)
                with open(config_file, 'w') as f:
                    cfg.write(f)
                print(f"\n配置文件已写入 {config_file}\n")
                self.host = self.host
                self.token = self.token
                print(f"已成功连接到服务器: {self.login()}\n")

            except Exception as error:
                print(error)
                print("\n配置文件写入失败\n")

    def login(self):
        try:
            self.s.headers = {'X-Plex-Token': self.token, 'Accept': 'application/json'}
            friendly_name = self.s.get(url=self.host, ).json()['MediaContainer']['friendlyName']
            return friendly_name
        except Exception as e:
            print(e)
            print("\n服务器连接不成功，请检查配置文件是否正确。\n")
            time.sleep(10)
            return sys.exit()

    def select_library(self):
        """列出并选择库"""
        data = self.s.get(
            url=f"{self.host}/library/sections/"
        ).json().get("MediaContainer", {}).get("Directory", [])

        library = [
            "{}> {}".format(i, data[i]["title"])
            for i in range(len(data))
        ]
        # print(data)
        index = int(input("\n".join(library) + "\n请选择库: "))
        action_key = data[index]['key']
        action_type = int(input("\n1> 电影\n2> 节目\n8> 艺术家\n9> 专辑\n10> 单曲\n请选择要操作的类型: "))
        return action_key, action_type

    def list_library(self):
        data = self.s.get(
            url=f"{self.host}/library/sections/"
        ).json().get("MediaContainer", {}).get("Directory", [])

        libraries = [[int(x['key']), TYPE[x['type']]] for x in data]
        return libraries

    def list_media_keys(self, select):
        datas = \
            self.s.get(url=f'{self.host}/library/sections/{select[0]}/all?type={select[1]}').json()["MediaContainer"][
                "Metadata"]
        media_keys = [data["ratingKey"] for data in datas]
        print(F"共计 {len(media_keys)} 个媒体")
        return media_keys

    def get_metadata(self, rating_key):
        metadata = self.s.get(url=f'{self.host}/library/metadata/{rating_key}').json()["MediaContainer"]["Metadata"][0]
        return metadata

    def put_title_sort(self, select, rating_key, sort_title, lock):
        self.s.put(
            url=f"{self.host}/library/sections/{select[0]}/all",
            params={
                "type": select[1],
                "id": rating_key,
                "includeExternalMedia": 1,
                "titleSort.value": sort_title,
                "titleSort.locked": lock
            }
        )

    def put_genres(self, select, rating_key, tag, addtag):
        """变更分类标签。"""
        res = self.s.put(url=f"{self.host}/library/sections/{select[0]}/all",
                         params={
                             "type": select[1],
                             "id": rating_key,
                             "genre.locked": 1,
                             "genre[0].tag.tag": addtag,
                             "genre[].tag.tag-": tag
                         }).text
        return res

    def put_styles(self, select, rating_key, tag, addtag):
        """变更风格标签。"""
        res = self.s.put(url=f"{self.host}/library/sections/{select[0]}/all",
                         params={
                             "type": select[1],
                             "id": rating_key,
                             "style.locked": 1,
                             "style[0].tag.tag": addtag,
                             "style[].tag.tag-": tag
                         }).text
        return res

    def put_mood(self, select, rating_key, tag, addtag):
        """变更情绪标签。"""
        res = self.s.put(url=f"{self.host}/library/sections/{select[0]}/all",
                         params={
                             "type": select[1],
                             "id": rating_key,
                             "mood.locked": 1,
                             "mood[0].tag.tag": addtag,
                             "mood[].tag.tag-": tag
                         }).text
        return res

    def loop_all(self):
        """选择一个媒体库并遍历其中的每一个媒体。"""
        library_list = self.list_library()
        print(library_list)
        # select = self.select_library()
        for ll in library_list:
            if ll[1] != 99:
                select = ll
                print(select)
                media_keys = self.list_media_keys(select)

                for rating_key in media_keys:
                    metadata = self.get_metadata(rating_key)
                    title = metadata["title"]
                    title_sort = metadata.get("titleSort", "")
                    genres = [genre.get("tag") for genre in metadata.get('Genre', {})]
                    styles = [style.get("tag") for style in metadata.get('Style', {})]
                    moods = [mood.get("tag") for mood in metadata.get('Mood', {})]

                    if select[1] != 10:
                        if has_chinese(title_sort) or title_sort == "":
                            title_sort = convert_to_pinyin(title)
                            self.put_title_sort(select, rating_key, title_sort, 1)
                            print(f"{title} → {title_sort}")

                    if select[1] != 10:
                        for genre in genres:
                            if new_genre := TAGS.get(genre):
                                self.put_genres(select, rating_key, genre, new_genre)
                                print(f"{title}: {genre} → {new_genre}")

                    if select[1] in [8, 9]:
                        for style in styles:
                            if new_style := TAGS.get(style):
                                self.put_styles(select, rating_key, style, new_style)
                                print(f"{title}: {style} → {new_style}")

                    if select[1] in [8, 9, 10]:
                        for mood in moods:
                            if new_mood := TAGS.get(mood):
                                self.put_styles(select, rating_key, mood, new_mood)
                                print(f"{title}: {mood} → {new_mood}")
            else:
                continue

    def put_collection_title_sort(self, select, rating_key, sort_title, lock):
        self.s.put(
            url=f"{self.host}/library/metadata/{rating_key}",
            params={
                "type": select[1],
                "id": rating_key,
                "includeExternalMedia": 1,
                "titleSort.value": sort_title,
                "titleSort.locked": lock
            }
        )

    def loop_all_collections(self):
        library_list = self.list_library()
        for ll in library_list:
            if ll[1] != 99:
                select = ll
                response = self.s.get(url=f'{self.host}/library/sections/{select[0]}/collections').json()
                if "Metadata" not in response["MediaContainer"]:
                    continue
                collections = response["MediaContainer"]["Metadata"]
                for collection in collections:
                    rating_key = collection['ratingKey']
                    title = collection['title']
                    title_sort = collection.get('titleSort', '')
                    if has_chinese(title_sort) or title_sort == '':
                        title_sort = convert_to_pinyin(title)
                        self.put_collection_title_sort(select, rating_key, title_sort, 1)
                        print(f"{title} → {title_sort}")

if __name__ == '__main__':
    plex_server = PlexServer()
    plex_server.loop_all()
    plex_server.loop_all_collections()
