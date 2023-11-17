import sys
import time
from configparser import ConfigParser
import pypinyin
import requests
from pathlib import Path
import concurrent.futures

# 版本 1.0

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

TYPE = {"movie": 1, "show": 2, "artist": 8, "album": 9, "track": 10, "photo":99} #99随手写的

config_file: Path = Path(__file__).parent / 'config.ini'

def has_chinese(string):
    for char in string:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False

def is_english(s):
    # 移除 "・" 字符
    s = s.replace('・', '')
    # 检查是否包含中文
    if not has_chinese(s):
        return True
    # 检查是否为日文
    for char in s:
        if '\u3040' <= char <= '\u30ff':
            return True
    return False

def convert_to_pinyin(text):
    str_a = pypinyin.pinyin(text, style=pypinyin.FIRST_LETTER)
    str_b = [str(str_a[i][0]).upper() for i in range(len(str_a))]
    return ''.join(str_b).replace("：", "").replace("（", "").replace("）", "").replace("，", "").replace("！", "").replace("？", "").replace("。", "").replace("；", "").replace("·", "").replace("-", "").replace("／", "").replace(",", "").replace("…", "").replace("!", "").replace("?", "").replace(".", "").replace(":", "").replace(";", "").replace("～", "").replace("~", "").replace("・", "")

class PlexServer:

    def __init__(self):
        cfg = ConfigParser()
        self.s = requests.session()

        try:
            cfg.read(config_file)
            self.host = dict(cfg.items("server"))["host"]
            self.token = dict(cfg.items("server"))["token"]
            self.skip = dict(cfg.items("server"))["skip"]
            print(f"已成功连接到服务器: {self.login()}\n")
        except Exception as error:
            print(error)
            print("\n配置文件读取失败，开始创建配置文件...\n")
            self.host = input('请输入您的 Plex 服务器地址（例如 http://127.0.0.1:32400）: ') or "http://127.0.0.1:32400"
            if self.host[-1] == "/":
                self.host = self.host[:-1]
            self.token = input('请输入您的 X-Plex-Token: ')
            self.skip = input('请输入您想跳过的库，用英文,分隔(如果没有需要跳过的库，直接回车即可): ')
            if self.skip:
                self.skip = self.skip.strip()
                self.skip = self.skip.strip(',')
            try:
                cfg.add_section("server")
                cfg.set("server", "host", self.host)
                cfg.set("server", "token", self.token)
                cfg.set("server", "skip", self.skip)
                with open(config_file, 'w') as f:
                    cfg.write(f)
                print(f"\n配置文件已写入 {config_file}\n")
                self.host = self.host
                self.token = self.token
                self.skip = self.skip
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

        skip_list = []
        if self.skip:
            skip_list = self.skip.split(',')
        libraries = [[int(x['key']), TYPE[x['type']], x['title']] for x in data if x['title'] not in skip_list]
        return libraries

    def list_media_keys(self, select):
        response = self.s.get(url=f'{self.host}/library/sections/{select[0]}/all?type={select[1]}').json()
        datas = response.get("MediaContainer", {}).get("Metadata", [])

        if not datas:
            if select[1] == 8:  # 如果是艺术家（歌手）
                print("歌手数: 0")
            elif select[1] == 9:  # 如果是专辑
                print("专辑数: 0")
            elif select[1] == 10:  # 如果是音轨
                print("音轨数: 0")
            else:
                print("媒体数: 0")
            return []

        media_keys = [data["ratingKey"] for data in datas]

        if select[1] == 8:  # 如果是艺术家（歌手）
            print(f"歌手数: {len(media_keys)}")
        elif select[1] == 9:  # 如果是专辑
            print(f"专辑数: {len(media_keys)}")
        elif select[1] == 10:  # 如果是音轨
            print(f"音轨数: {len(media_keys)}")
        else:
            print(f"媒体数: {len(media_keys)}")

        return media_keys

    def get_metadata(self, rating_key):
        metadata = self.s.get(url=f'{self.host}/library/metadata/{rating_key}').json()["MediaContainer"]["Metadata"][0]
        return metadata

    def put_title_sort(self, select, rating_key, sort_title, lock):
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

    def put_genres(self, select, rating_key, tag, addtag):
        """变更流派标签。"""
        if TAGS.get(tag):
            # 获取当前的所有标签
            current_tags = [genre.get("tag") for genre in self.get_metadata(rating_key).get('Genre', {})]
            # 移除原有的英文标签
            current_tags = [current_tag for current_tag in current_tags if current_tag != tag]
            # 创建一个新的参数列表
            params = {
                "type": select[1],
                "id": rating_key,
                "genre.locked": 1,
            }
            # 添加新的标签
            params.update({f"genre[{i}].tag.tag": current_tag for i, current_tag in enumerate(current_tags)})
            params[f"genre[{len(current_tags)}].tag.tag"] = addtag
            res = self.s.put(url=f"{self.host}/library/metadata/{rating_key}", params=params).text
            return res

    def put_styles(self, select, rating_key, tag, addtag):
        """变更风格标签。"""
        if TAGS.get(tag):
            # 获取当前的所有标签
            current_tags = [style.get("tag") for style in self.get_metadata(rating_key).get('Style', {})]
            # 移除原有的英文标签
            current_tags = [current_tag for current_tag in current_tags if current_tag != tag]
            # 创建一个新的参数列表
            params = {
                "type": select[1],
                "id": rating_key,
                "style.locked": 1,
            }
            # 添加新的标签
            params.update({f"style[{i}].tag.tag": current_tag for i, current_tag in enumerate(current_tags)})
            params[f"style[{len(current_tags)}].tag.tag"] = addtag
            res = self.s.put(url=f"{self.host}/library/metadata/{rating_key}", params=params).text
            return res

    def put_mood(self, select, rating_key, tag, addtag):
        """变更情绪标签。"""
        if TAGS.get(tag):
            # 获取当前的所有标签
            current_tags = [mood.get("tag") for mood in self.get_metadata(rating_key).get('Mood', {})]
            # 移除原有的英文标签
            current_tags = [current_tag for current_tag in current_tags if current_tag != tag]
            # 创建一个新的参数列表
            params = {
                "type": select[1],
                "id": rating_key,
                "mood.locked": 1,
            }
            # 添加新的标签
            params.update({f"mood[{i}].tag.tag": current_tag for i, current_tag in enumerate(current_tags)})
            params[f"mood[{len(current_tags)}].tag.tag"] = addtag
            res = self.s.put(url=f"{self.host}/library/metadata/{rating_key}", params=params).text
            return res

    def process_media(self, args):
        select, rating_key = args
        metadata = self.get_metadata(rating_key)
        title = metadata["title"]
        title_sort = metadata.get("titleSort", "")
        genres = [genre.get("tag") for genre in metadata.get('Genre', {})]
        styles = [style.get("tag") for style in metadata.get('Style', {})]
        moods = [mood.get("tag") for mood in metadata.get('Mood', {})]

        if not is_english(title) and (has_chinese(title_sort) or title_sort == ""):
            title_sort = convert_to_pinyin(title)
            self.put_title_sort(select, rating_key, title_sort, 1)
            print(f"{title} → {title_sort}")

        if select[1] != 10:
            for genre in genres:
                if new_genre := TAGS.get(genre):
                    self.put_genres(select, rating_key, genre, new_genre)
                    print(f"{title}: {genre} → {new_genre}")

            for style in styles:
                if new_style := TAGS.get(style):
                    self.put_styles(select, rating_key, style, new_style)
                    print(f"{title}: {style} → {new_style}")

            for mood in moods:
                if new_mood := TAGS.get(mood):
                    self.put_styles(select, rating_key, mood, new_mood)
                    print(f"{title}: {mood} → {new_mood}")

    def process_artist(self, args):
        select, rating_key = args
        metadata = self.get_metadata(rating_key)
        title = metadata["title"]
        title_sort = metadata.get("titleSort", "")
        genres = [genre.get("tag") for genre in metadata.get('Genre', {})]
        styles = [style.get("tag") for style in metadata.get('Style', {})]
        moods = [mood.get("tag") for mood in metadata.get('Mood', {})]

        if not is_english(title) and (has_chinese(title_sort) or title_sort == ""):
            title_sort = convert_to_pinyin(title)
            self.put_title_sort(select, rating_key, title_sort, 1)
            print(f"{title} → {title_sort}")

        for genre in genres:
            if new_genre := TAGS.get(genre):
                self.put_genres(select, rating_key, genre, new_genre)
                print(f"{title}: {genre} → {new_genre}")

        for style in styles:
            if new_style := TAGS.get(style):
                self.put_styles(select, rating_key, style, new_style)
                print(f"{title}: {style} → {new_style}")

        for mood in moods:
            if new_mood := TAGS.get(mood):
                self.put_mood(select, rating_key, mood, new_mood)
                print(f"{title}: {mood} → {new_mood}")

    def process_album(self, args):
        select, rating_key = args
        metadata = self.get_metadata(rating_key)
        title = metadata["title"]
        title_sort = metadata.get("titleSort", "")
        genres = [genre.get("tag") for genre in metadata.get('Genre', {})]
        styles = [style.get("tag") for style in metadata.get('Style', {})]
        moods = [mood.get("tag") for mood in metadata.get('Mood', {})]

        if not is_english(title) and (has_chinese(title_sort) or title_sort == ""):
            title_sort = convert_to_pinyin(title)
            self.put_title_sort(select, rating_key, title_sort, 1)
            print(f"{title} → {title_sort}")

        for genre in genres:
            if new_genre := TAGS.get(genre):
                self.put_genres(select, rating_key, genre, new_genre)
                print(f"{title}: {genre} → {new_genre}")

        for style in styles:
            if new_style := TAGS.get(style):
                self.put_styles(select, rating_key, style, new_style)
                print(f"{title}: {style} → {new_style}")

        for mood in moods:
            if new_mood := TAGS.get(mood):
                self.put_mood(select, rating_key, mood, new_mood)
                print(f"{title}: {mood} → {new_mood}")

    def process_track(self, args):
        select, rating_key = args
        metadata = self.get_metadata(rating_key)
        title = metadata["title"]
        title_sort = metadata.get("titleSort", "")
        moods = [mood.get("tag") for mood in metadata.get('Mood', {})]

        if not is_english(title) and (has_chinese(title_sort) or title_sort == ""):
            title_sort = convert_to_pinyin(title)
            self.put_title_sort(select, rating_key, title_sort, 1)
            print(f"{title} → {title_sort}")

        for mood in moods:
            if new_mood := TAGS.get(mood):
                self.put_mood(select, rating_key, mood, new_mood)
                print(f"{title}: {mood} → {new_mood}")

    def loop_all(self):
        library_list = self.list_library()

        for ll in library_list:
            if ll[1] != 99:
                select = ll[:2]
                print(f"处理库: {ll[2]}")
                if ll[1] == 8:  # 如果是音乐库

                    # 处理艺术家（歌手）
                    artist_keys = self.list_media_keys([select[0], 8])
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        executor.map(self.process_artist, [(select, key) for key in artist_keys])

                    # 处理专辑
                    album_keys = self.list_media_keys([select[0], 9])
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        executor.map(self.process_album, [(select, key) for key in album_keys])

                    # 处理音轨
                    track_keys = self.list_media_keys([select[0], 10])
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        executor.map(self.process_track, [(select, key) for key in track_keys])

                else:
                    media_keys = self.list_media_keys(select)

                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        executor.map(self.process_media, [(select, key) for key in media_keys])

                print()

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
                select = ll[:2]
                print(f"处理库: {ll[2]}")
                response = self.s.get(url=f'{self.host}/library/sections/{select[0]}/collections').json()
                if "Metadata" not in response["MediaContainer"]:
                    print(f"合集数: 0")
                    print()
                    continue
                collections = response["MediaContainer"]["Metadata"]
                print(f"合集数: {len(collections)}")
                for collection in collections:
                    rating_key = collection['ratingKey']
                    title = collection['title']
                    title_sort = collection.get('titleSort', '')
                    if not is_english(title) and (has_chinese(title_sort) or title_sort == ""):
                        title_sort = convert_to_pinyin(title)
                        self.put_collection_title_sort(select, rating_key, title_sort, 1)
                        print(f"{title} → {title_sort}")
                print()

if __name__ == '__main__':
    plex_server = PlexServer()
    plex_server.loop_all()
    plex_server.loop_all_collections()
