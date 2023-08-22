# plex-localization-zh
使用 plex-localization-zh 可以将 Plex 媒体库中的媒体信息进行中文本地化。它可以通过与 Plex 服务器进行交互，获取媒体库中的电影、电视节目、专辑和合集信息，将媒体标题的标题排序修改为媒体标题的拼音首字母缩写，并获取媒体的类型标签、风格标签和情绪标签等标签，将英文标签进行汉化。从而实现 Plex 媒体库的拼音排序、拼音搜索及类型标签汉化功能。

## 示例
通过运行 plex-localization-zh，可以自动将媒体的标题排序修改为媒体标题的拼音首字母缩写，例如：
```
将电影的标题排序从 "重庆森林" 变更为 "CQSL"。
将电视节目的标题排序从 "怪奇物语" 变更为 "GQWY"。
将艺术家的艺术家排序从 "王菲" 变更为 "WF"。
将合集的标题排序从 "黑客帝国（系列）" 变更为 "HKDG(XL)"。
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
- 安装了必要的第三方库：requests、pypinyin。（可以通过命令 `pip3 install requests pypinyin` 安装）

## 使用方法
1. 将仓库克隆或下载到计算机上的一个目录中。
2. 修改 `start.command (Mac)` 或 `start.bat (Win)` 中的路径，以指向您存放 `plex-localization-zh.py` 脚本的目录。
3. 双击运行 `start.command` 或 `start.bat` 脚本以执行 `plex-localization-zh.py` 脚本。
4. 首次运行时需要您在控制台中输入您的 Plex 服务器地址和 [X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)，这些信息将被保存在与脚本相同目录下的 `config.ini` 文件中，以便将来使用。
5. 脚本将连接到您的 Plex 服务器并自动遍历所有媒体库，将中文标题的标题排序修改为媒体标题的拼音首字母缩写，并根据预定义的标签映射将元数据标签翻译为中文。
6. 在处理过程中，脚本会打印出已变更的元数据，您可以在控制台中查看这些信息。

## 注意事项
- 请确保您提供了正确的 Plex 服务器地址和正确的 [X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)。
- 如果脚本无法连接到 Plex 服务器，请检查您的网络连接，并确保服务器可以访问。
- 请使用服务器管理员账号的 X-Plex-Token 运行脚本，以确保您对 Plex 服务器具有足够的权限。

## 已知问题
部分纯数字或纯英文的媒体标题会在每次运行脚本时被重复更新。

## 感谢
此脚本的原作是 [plex_localization_zhcn](https://github.com/sqkkyzx/plex_localization_zhcn)，我在原作的修改版 [plexpy](https://github.com/anooki-c/plexpy) 的基础上增加了对合集标题的支持，感谢 [timmy0209](https://github.com/timmy0209)、[sqkkyzx](https://github.com/sqkkyzx)、[anooki-c](https://github.com/anooki-c) 贡献的代码。
