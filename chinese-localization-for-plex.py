import sys
import time
import json
import logging
import pypinyin
import requests
import argparse
import datetime
import concurrent.futures
from pathlib import Path
from flask import Flask, request
from configparser import ConfigParser

# 创建一个日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

# 打印信息时带上时间戳
def print_with_timestamp(*args, **kwargs):
    logger.info(*args, **kwargs)

# 配置文件路径
config_file: Path = Path(__file__).parent / 'config' / 'config.ini'
tags_file: Path = Path(__file__).parent / 'config' / 'tags.json'
config = ConfigParser()
config.read(config_file)

# 读取标签映射
with open(tags_file, 'r', encoding='utf-8') as f:
    TAGS = json.load(f)

# 定义类型映射
TYPE = {"movie": 1, "show": 2, "artist": 8, "album": 9, "track": 10, "photo": 99}

# 检查字符串是否包含中文字符
def has_chinese(string):
    for char in string:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False

# 检查字符串是否为英文
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

# 将中文字符串转换为拼音
def convert_to_pinyin(text):
    str_a = pypinyin.pinyin(text, style=pypinyin.FIRST_LETTER)
    str_b = [str(str_a[i][0]).upper() for i in range(len(str_a))]
    return ''.join(str_b).replace("：", "").replace("（", "").replace("）", "").replace("，", "").replace("！", "").replace("？", "").replace("。", "").replace("；", "").replace("·", "").replace("-", "").replace("／", "").replace(",", "").replace("…", "").replace("!", "").replace("?", "").replace(".", "").replace(":", "").replace(";", "").replace("～", "").replace("~", "").replace("・", "").replace("“", "").replace("”", "").replace("《", "").replace("》", "").replace("〈", "").replace("〉", "").replace("(", "").replace(")", "").replace("<", "").replace(">", "").replace("\"", "")

# 定义 PlexServer 类
class PlexServer:

    def __init__(self):
        cfg = ConfigParser()
        self.s = requests.session()

        cfg.read(config_file)
        self.host = dict(cfg.items("server"))["address"]
        self.token = dict(cfg.items("server"))["token"]
        self.skip_libraries = dict(cfg.items("server"))["skip_libraries"].split('；')
        print_with_timestamp(f"已成功连接到服务器：{self.login()}")
        logger.info("")

    # 登录到 Plex 服务器
    def login(self):
        try:
            self.s.headers = {'X-Plex-Token': self.token, 'Accept': 'application/json'}
            friendly_name = self.s.get(url=self.host, ).json()['MediaContainer']['friendlyName']
            return friendly_name
        except Exception as e:
            print_with_timestamp(e)
            print_with_timestamp("服务器连接失败，请检查配置文件或网络的设置是否有误。如需帮助，请访问 https://github.com/x1ao4/chinese-localization-for-plex 查看使用说明。\n")
            time.sleep(10)
            return sys.exit()

    # 列出所有媒体库
    def list_library(self):
        data = self.s.get(
            url=f"{self.host}/library/sections/"
        ).json().get("MediaContainer", {}).get("Directory", [])
    
        libraries = [[int(x['key']), TYPE[x['type']], x['title']] for x in data]
        return libraries

    # 列出所有媒体键
    def list_media_keys(self, select, print_counts=True):
        response = self.s.get(url=f'{self.host}/library/sections/{select[0]}/all?type={select[1]}').json()
        datas = response.get("MediaContainer", {}).get("Metadata", [])
    
        if not datas:
            if print_counts:
                if select[1] == 8:
                    print_with_timestamp("艺人数：0")
                elif select[1] == 9:
                    print_with_timestamp("专辑数：0")
                elif select[1] == 10:
                    print_with_timestamp("曲目数：0")
                else:
                    print_with_timestamp("项目数：0")
            return []
    
        media_keys = [data["ratingKey"] for data in datas]
    
        if print_counts:
            if select[1] == 8:
                print_with_timestamp(f"艺人数：{len(media_keys)}")
            elif select[1] == 9:
                print_with_timestamp(f"专辑数：{len(media_keys)}")
            elif select[1] == 10:
                print_with_timestamp(f"曲目数：{len(media_keys)}")
            else:
                print_with_timestamp(f"项目数：{len(media_keys)}")
    
        return media_keys

    # 获取元数据
    def get_metadata(self, rating_key):
        metadata = self.s.get(url=f'{self.host}/library/metadata/{rating_key}').json()["MediaContainer"]["Metadata"][0]
        return metadata

    # 更新标题排序
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

    # 更新类型标签
    def put_genres(self, select, rating_key, tag, addtag):
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

    # 更新风格标签
    def put_styles(self, select, rating_key, tag, addtag):
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

    # 更新氛围标签
    def put_mood(self, select, rating_key, tag, addtag):
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

    # 处理项目
    def process_item(self, args):
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
            logger.info(f"{title} → {title_sort}")

        if select[1] != 10:
            for genre in genres:
                if new_genre := TAGS.get(genre):
                    self.put_genres(select, rating_key, genre, new_genre)
                    logger.info(f"{title}：{genre} → {new_genre}")

            for style in styles:
                if new_style := TAGS.get(style):
                    self.put_styles(select, rating_key, style, new_style)
                    logger.info(f"{title}：{style} → {new_style}")

            for mood in moods:
                if new_mood := TAGS.get(mood):
                    self.put_styles(select, rating_key, mood, new_mood)
                    logger.info(f"{title}：{mood} → {new_mood}")

    # 处理艺人
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
            logger.info(f"{title} → {title_sort}")
    
        for genre in genres:
            if new_genre := TAGS.get(genre):
                self.put_genres(select, rating_key, genre, new_genre)
                logger.info(f"{title}：{genre} → {new_genre}")
    
        for style in styles:
            if new_style := TAGS.get(style):
                self.put_styles(select, rating_key, style, new_style)
                logger.info(f"{title}：{style} → {new_style}")
    
        for mood in moods:
            if new_mood := TAGS.get(mood):
                self.put_mood(select, rating_key, mood, new_mood)
                logger.info(f"{title}：{mood} → {new_mood}")

    # 处理专辑
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
            logger.info(f"{title} → {title_sort}")
    
        for genre in genres:
            if new_genre := TAGS.get(genre):
                self.put_genres(select, rating_key, genre, new_genre)
                logger.info(f"{title}：{genre} → {new_genre}")
    
        for style in styles:
            if new_style := TAGS.get(style):
                self.put_styles(select, rating_key, style, new_style)
                logger.info(f"{title}：{style} → {new_style}")
    
        for mood in moods:
            if new_mood := TAGS.get(mood):
                self.put_mood(select, rating_key, mood, new_mood)
                logger.info(f"{title}：{mood} → {new_mood}")

    # 处理曲目
    def process_track(self, args):
        select, rating_key = args
        metadata = self.get_metadata(rating_key)
        title = metadata["title"]
        title_sort = metadata.get("titleSort", "")
        genres = [genre.get("tag") for genre in metadata.get('Genre', {})]
        moods = [mood.get("tag") for mood in metadata.get('Mood', {})]

        if not is_english(title) and (has_chinese(title_sort) or title_sort == ""):
            title_sort = convert_to_pinyin(title)
            self.put_title_sort(select, rating_key, title_sort, 1)
            logger.info(f"{title} → {title_sort}")

        for genre in genres:
            if new_genre := TAGS.get(genre):
                self.put_genres(select, rating_key, genre, new_genre)
                logger.info(f"{title}：{genre} → {new_genre}")

        for mood in moods:
            if new_mood := TAGS.get(mood):
                self.put_mood(select, rating_key, mood, new_mood)
                logger.info(f"{title}：{mood} → {new_mood}")

    # 循环处理所有项目
    def loop_all(self):
        library_list = self.list_library()
    
        for ll in library_list:
            if ll[1] != 99 and ll[2] not in self.skip_libraries:
                select = ll[:2]
                logger.info(f"处理库：{ll[2]}")
                if ll[1] == 8:
    
                    # 处理艺人
                    artist_keys = self.list_media_keys([select[0], 8], print_counts=True)
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        executor.map(self.process_artist, [(select, key) for key in artist_keys])
    
                    # 处理专辑
                    album_keys = self.list_media_keys([select[0], 9], print_counts=True)
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        executor.map(self.process_album, [(select, key) for key in album_keys])
    
                    # 处理曲目
                    track_keys = self.list_media_keys([select[0], 10], print_counts=True)
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        executor.map(self.process_track, [(select, key) for key in track_keys])
    
                else:
                    media_keys = self.list_media_keys(select, print_counts=True)
    
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        executor.map(self.process_item, [(select, key) for key in media_keys])
    
                logger.info("")

    # 更新合集标题排序
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

    # 循环处理所有合集
    def loop_all_collections(self):
        library_list = self.list_library()

        for ll in library_list:
            if ll[1] != 99 and ll[2] not in self.skip_libraries:
                select = ll[:2]
                logger.info(f"处理库：{ll[2]}")
                response = self.s.get(url=f'{self.host}/library/sections/{select[0]}/collections').json()
                if "Metadata" not in response["MediaContainer"]:
                    logger.info(f"合集数：0")
                    logger.info("")
                    continue
                collections = response["MediaContainer"]["Metadata"]
                logger.info(f"合集数：{len(collections)}")
                for collection in collections:
                    rating_key = collection['ratingKey']
                    title = collection['title']
                    title_sort = collection.get('titleSort', '')
                    if not is_english(title) and (has_chinese(title_sort) or title_sort == ""):
                        title_sort = convert_to_pinyin(title)
                        self.put_collection_title_sort(select, rating_key, title_sort, 1)
                        logger.info(f"{title} → {title_sort}")
                logger.info("")

    # 处理新合集
    def process_new_collections(self, library_section_id, new_collections):
        library = next((lib for lib in self.list_library() if lib[0] == library_section_id))

        select = library[:2]
        response = self.s.get(url=f'{self.host}/library/sections/{select[0]}/collections?sort=titleSort:desc').json()
        if "Metadata" not in response["MediaContainer"]:
            return
        collections = response["MediaContainer"]["Metadata"]
        for collection in collections:
            rating_key = collection['ratingKey']
            guid = collection['guid']
            title = collection['title']
            title_sort = collection.get('titleSort', '')
            if guid in new_collections:
                if not is_english(title) and (has_chinese(title_sort) or title_sort == ""):
                    title_sort = convert_to_pinyin(title)
                    self.put_collection_title_sort(select, rating_key, title_sort, 1)
                    logger.info(f"{title} → {title_sort}")

    # 处理新项目
    def process_new_item(self, metadata):
        # 从元数据中提取必要的信息
        rating_key = metadata['ratingKey']
        library_section_id = metadata['librarySectionID']
        media_type = metadata['type']

        # 如果项目类型是 episode 则跳过该项目
        if media_type == 'episode':
            return

        # 获取此项目所在库的类型和标题
        library = next((lib for lib in self.list_library() if lib[0] == library_section_id), None)
        if library is None:
            return

        library_type, library_title = library[1], library[2]

        # 检查此库是否在跳过列表中
        if library_title in self.skip_libraries:
            return

        # 根据项目类型处理项目
        if library_type == TYPE['artist']:
            self.process_artist(([library_section_id, library_type], rating_key))
            # 获取并处理所有属于这个 artist 的 album 和 track
            album_keys = self.list_media_keys([library_section_id, TYPE['album']], print_counts=False)
            track_keys = self.list_media_keys([library_section_id, TYPE['track']], print_counts=False)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(self.process_album, [([library_section_id, library_type], key) for key in album_keys])
                executor.map(self.process_track, [([library_section_id, library_type], key) for key in track_keys])
        elif library_type == TYPE['album']:
            self.process_album(([library_section_id, library_type], rating_key))
            # 获取并处理所有属于这个 album 的 track
            track_keys = self.list_media_keys([library_section_id, TYPE['track']], print_counts=False)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(self.process_track, [([library_section_id, library_type], key) for key in track_keys])
        elif library_type == TYPE['track']:
            self.process_track(([library_section_id, library_type], rating_key))
        else:
            self.process_item(([library_section_id, library_type], rating_key))

        # 如果新项目属于一个或多个合集，处理这些合集
        if 'Collection' in metadata:
            new_collections = [collection['guid'] for collection in metadata['Collection']]
            self.process_new_collections(library_section_id, new_collections)

if __name__ == '__main__':
    # 创建一个解析器
    parser = argparse.ArgumentParser(description='处理 Plex 服务器的媒体库项目')
    # 添加选项，用户可以通过这些选项来选择运行哪个功能
    parser.add_argument('--all', action='store_true', help='处理所有项目')
    parser.add_argument('--new', action='store_true', help='处理新增项目')

    args = parser.parse_args()

    plex_server = PlexServer()

    if args.all:
        plex_server.loop_all()
        plex_server.loop_all_collections()
    elif args.new:
        app = Flask(__name__)
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        # 定义 webhook 路由
        @app.route('/', methods=['POST'])
        def webhook():
            file = request.files.get('thumb')
            payload = request.form.get('payload')
            if payload:
                data = json.loads(payload)
                event = data.get('event')
                if event == 'library.new':
                    metadata = data.get('Metadata')
                    if metadata:
                        plex_server.process_new_item(metadata)
            return 'OK', 200

        # 启动 Flask 服务器
        app.run(host='0.0.0.0', port=8088)
