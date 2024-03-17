# plex-localization-zh
使用 plex-localization-zh 可以将 Plex 媒体库中的媒体信息进行中文本地化。它可以通过与 Plex 服务器进行交互，获取媒体库中的电影、电视节目、艺术家、专辑、音轨和合集信息，将媒体的标题排序修改为媒体标题的拼音首字母缩写，并获取媒体的类型标签、风格标签和情绪标签等标签，将英文标签进行汉化。从而实现 Plex 媒体库的拼音排序、拼音搜索及类型标签汉化功能。

## 示例
通过运行 plex-localization-zh，可以自动将媒体的标题排序修改为媒体标题的拼音首字母缩写，例如：
```
将电影的标题排序从 "重庆森林" 变更为 "CQSL"。
将电视节目的标题排序从 "怪奇物语" 变更为 "GQWY"。
将艺术家的艺术家排序从 "王菲" 变更为 "WF"。
将合集的标题排序从 "黑客帝国（系列）" 变更为 "HKDGXL"。
```
标题排序只影响排列顺序，不影响显示效果，媒体在 Plex 中依然会以中文标题进行显示，但是在使用标题排序时会根据拼音首字母缩写进行排序，并且可以通过拼音首字母缩写进行搜索，包括模糊搜索。

通过运行 plex-localization-zh 还可以自动将媒体的元数据标签从英文翻译成中文，例如：
```
将电影的类型从 "Action" 变更为 "动作"。
将电视节目的类型从 "Comedy" 变更为 "喜剧"。
将专辑的情绪从 "Sad" 变更为 "悲伤"。
将艺术家的风格从 "Pop" 变更为 "流行"。
```
脚本中已经预置了一些常用标签的中英翻译，主要是影视类型，若有其他标签需要汉化可以自己在脚本中添加中英翻译。

## 运行条件
- 安装了 Python 3.0 或更高版本。
- 安装了必要的第三方库：requests、pypinyin。（可以通过 `pip3 install requests pypinyin` 安装）

## 配置文件
在运行脚本前，请先打开配置文件 `config.ini`，参照以下提示（示例）进行配置。
```
[server]
# Plex 服务器的地址，格式为 http://服务器 IP 地址:32400 或 http(s)://域名:端口号
address = http://127.0.0.1:32400
# Plex 服务器的 token，用于身份验证
token = xxxxxxxxxxxxxxxxxxxx
# 指定需要跳过的库，格式为 库名1；库名2；库名3，如果没有设置此项则默认对所有库进行处理
skip_libraries = 云电影；云电视剧；演唱会
```

## 使用方法
1. 将仓库克隆或下载到计算机上的一个目录中。
2. 修改 `start.command (Mac)` 或 `start.bat (Win)` 中的路径，以指向你存放 `plex-localization-zh.py` 脚本的目录。
3. 打开 `config.ini`，填写你的 Plex 服务器地址（`address`）和 [X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)（`token`），按照需要选填其他配置选项。
4. 双击运行 `start.command` 或 `start.bat` 脚本以执行 `plex-localization-zh.py` 脚本。
6. 脚本将连接到你的 Plex 服务器并自动遍历所有（指定的）媒体库，将中文标题的标题排序修改为媒体标题的拼音首字母缩写，根据预定义的标签映射将元数据标签翻译为中文，并在控制台显示媒体库的信息和处理结果。

## 注意事项
- 请确保你提供了正确的 Plex 服务器地址和正确的 X-Plex-Token。
- 如果脚本无法连接到 Plex 服务器，请检查你的网络连接，并确保服务器可以访问。
- 请使用服务器管理员账号的 X-Plex-Token 运行脚本，以确保你对 Plex 服务器具有足够的权限。

## 感谢
此脚本的原作是 [plex_localization_zhcn](https://github.com/sqkkyzx/plex_localization_zhcn)，我在原作的修改版 [plexpy](https://github.com/anooki-c/plexpy) 的基础上增加了对合集标题的支持，感谢 [timmy0209](https://github.com/timmy0209)、[sqkkyzx](https://github.com/sqkkyzx)、[anooki-c](https://github.com/anooki-c) 贡献的代码。
<br>
<br>
# plex-localization-zh
plex-localization-zh is a script that allows you to localize media information in your Plex media library. It interacts with your Plex server to retrieve information about movies, TV shows, artists, albums, tracks and collections. The script modifies the title sort of media to the initials of the Chinese pinyin of the title. It also translates metadata labels such as genre, style, and mood from English to Chinese. This provides features like Chinese pinyin sorting, searching, and Chinese labeling for your Plex media library.

## Example
By running plex-localization-zh, you can automatically change the title sort of media to the initials of the Chinese pinyin of the title, for example:
```
Change the title sort of a movie from "重庆森林" to "CQSL".
Change the title sort of a TV show from "怪奇物语" to "GQWY".
Change the artist sort of an artist from "王菲" to "WF".
Change the title sort of a collection from "黑客帝国（系列）" to "HKDGXL".
```
Title sorting affects the order of display but doesn't impact the actual display of media in Chinese. When using title sorting, the media will be sorted based on the initials of the Chinese pinyin abbreviation, and you can also search using these initials, including fuzzy searching.

By running plex-localization-zh, you can also automatically translate metadata labels from English to Chinese, for example:
```
Translate the genre of a movie from "Action" to "动作".
Translate the genre of a TV show from "Comedy" to "喜剧".
Translate the mood of an album from "Sad" to "悲伤".
Translate the style of an artist from "Pop" to "流行".
```
The script has preset some commonly used tag translations in Chinese and English, mainly film and television types. If there are other tags that need to be localized into Chinese, you can add Chinese-English translations in the script yourself.

## Requirements
- Installed Python 3.0 or higher.
- Installed required third-party libraries: requests, pypinyin. (Install with `pip3 install requests pypinyin`)

## Config
Before running the script, please open the configuration file `config.ini` and configure it according to the following prompts (examples).
```
[server]
# Address of the Plex server, formatted as http://server IP address:32400 or http(s)://domain:port
address = http://127.0.0.1:32400
# Token of the Plex server for authentication
token = xxxxxxxxxxxxxxxxxxxx
# Specify the libraries to skip, in the format Library1；Library2；Library3, if not set, all libraries will be processed by default
skip_libraries = 云电影；云电视剧；演唱会
```

## Usage
1. Clone or download the repository to a directory on your computer.
2. Modify the path in `start.command (Mac)` or `start.bat (Win)` to point to the directory where you store the `plex-localization-zh.py` script.
3. Open `config.ini`, fill in your Plex server address (`address`) and [X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/) (`token`), and fill in other configuration options as needed.
4. Double-click `start.command` or `start.bat` to execute the `plex-localization-zh.py` script.
6. The script will connect to your Plex server and automatically traverse all (specified) media libraries, modify the title sorting of Chinese titles to the acronym of the media title’s pinyin, translate the metadata tags into Chinese according to the predefined tag mapping, and display the information and processing results of the media library on the console.

## Notes
- Ensure you provide the correct Plex server address and the correct X-Plex-Token.
- If the script cannot connect to the Plex server, check your network connection and make sure the server is accessible.
- Run the script using the X-Plex-Token of a server administrator account to ensure you have sufficient permissions on the Plex server.

## Credits
This script is based on the original work of [plex_localization_zhcn](https://github.com/sqkkyzx/plex_localization_zhcn). I added support for collection titles based on [plexpy](https://github.com/anooki-c/plexpy). Thanks to contributions from [timmy0209](https://github.com/timmy0209)、[sqkkyzx](https://github.com/sqkkyzx)、[anooki-c](https://github.com/anooki-c).
