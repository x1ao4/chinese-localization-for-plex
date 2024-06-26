# Chinese Localization for Plex
使用 Chinese Localization for Plex（下文简称 CLP）可以对 Plex 服务器项目的部分元数据进行中文本地化。它可以与 Plex 服务器进行交互，获取媒体库中的电影、电视节目、艺人、专辑、曲目和合集的元数据，将项目的标题排序修改为项目标题的拼音首字母缩写，并获取项目的类型、氛围或风格等标签，将英文标签进行汉化。从而实现 Plex 媒体库的拼音排序、拼音搜索以及标签汉化功能。

## 示例
通过 CLP 可以自动将项目的标题排序变更为项目标题的拼音首字母缩写，例如：
```
将电影的标题排序从 “重庆森林” 变更为 “CQSL”
将电视节目的标题排序从 “怪奇物语” 变更为 “GQWY”
将艺人的艺人排序从 “王菲” 变更为 “WF”
将合集的标题排序从 “黑客帝国（系列）” 变更为 “HKDGXL”
```
标题/艺人/专辑排序只影响排列顺序，不影响显示效果，项目在 Plex 中依然会以中文标题进行显示，但是在使用标题/艺人/专辑排序时会根据拼音首字母缩写进行排序，并且可以通过拼音首字母缩写进行搜索，包括模糊搜索。

![标题排序](https://github.com/x1ao4/chinese-localization-for-plex/assets/112841659/5f1f45fe-bac0-41cb-b864-f0c7b5830884)

通过 CLP 还可以自动将项目的标签从英文转换为中文，例如：
```
将电影的类型从 “Action” 变更为 “动作”
将电视节目的类型从 “Comedy” 变更为 “喜剧”
将专辑的氛围从 “Sad” 变更为 “悲伤”
将艺人的风格从 “Pop” 变更为 “流行”
```
`/config/tags.json` 中已经预置了一些常用标签的中英翻译，主要是影视类型标签，若有其他标签需要汉化可以自己在 `tags.json` 中添加中英翻译（标签映射），注意保持格式与预设一致。

![标签汉化](https://github.com/x1ao4/chinese-localization-for-plex/assets/112841659/dbc37928-6f6c-4552-9cf2-242cb08e31c4)

## 功能
使用 CLP 可以实现以下功能。

- 电影、电视节目、艺人、专辑、曲目、合集的拼音排序和拼音搜索
- 电影、电视节目、艺人、专辑、曲目的类型标签汉化
- 艺人、专辑、曲目的氛围标签汉化
- 艺人、专辑的风格标签汉化

我们提供了 `处理所有项目（all）` 和 `处理新增项目（new）` 两种模式，并且允许用户设置 `需要跳过的资料库`，仅对你希望处理的资料库中的项目进行处理。其中，`处理新增项目` 模式需要服务器的管理员账号订阅了 Plex Pass 才能使用。

- 处理所有项目：根据用户配置，在排除掉需要跳过的资料库后对其余库中的所有项目进行处理，已经处理过或不需要被处理的项目会被跳过。
- 处理新增项目：通过 Webhooks 功能监听服务器事件，实时获取新增项目的元数据，根据用户配置，仅对新增项目进行处理（不含需要跳过的资料库中的新增项目）。

由于 Plex 服务器不支持发送新增曲目的事件通知（支持发送新增专辑或艺人的事件通知）。在你向音乐资料库添加曲目时，若该曲目所属的专辑已经存在于资料库中，那么 CLP 将不会收到任何通知，`处理新增项目` 也就不会对其进行处理。你可以通过（定时）运行 `处理所有项目` 来解决这些漏网之鱼。

## 配置说明
在使用 CLP 前，请先参考以下提示（示例）对 `/config/config.ini` 进行配置。
```
[server]
# Plex 服务器的地址，格式为 http://服务器 IP 地址:32400 或 http(s)://域名:端口号
address = http://127.0.0.1:32400
# Plex 服务器的 token，用于身份验证
token = xxxxxxxxxxxxxxxxxxxx
# 指定需要跳过的资料库，格式为 库名1；库名2；库名3，若没有需要跳过的资料库，可以留空
skip_libraries = 云电影；云电视剧；演唱会
```
在 `处理新增项目` 模式下运行时，CLP 会使用 Flask 创建一个 Web 服务器，通过监听 `8088` 端口来接收 Plex 服务器发送的 `library.new` 事件，从而获取新增项目的信息并对其进行处理。

假如你的 `8088` 端口已经被其他服务占用，你可能需要通过修改 `chinese-localization-for-plex.py` 最后一行的 `port=8088`（通过 Python 脚本运行时）或者通过修改端口映射（通过 Docker 容器运行时）来更换监听端口。

## 运行方式
你可以通过 Docker 容器或者 Python 脚本来运行 CLP，推荐使用 Docker 容器运行，具体使用方法可参考下文。

### 通过 Docker 容器运行

#### 运行条件
- 安装了 Docker 和 Docker Compose。

#### Docker Compose
- Plex Pass 订阅用户
  
   ```
   version: "2"
   services:
     clp-scheduler:
       image: mcuadros/ofelia:latest
       container_name: clp-scheduler
       depends_on:
         - clp-all
       command: daemon --docker -f label=com.docker.compose.project=${COMPOSE_PROJECT_NAME}
       labels:
         ofelia.job-run.clp-all.schedule: 0 30 22 * * *
         ofelia.job-run.clp-all.container: clp-all
       environment:
         - TZ=Asia/Shanghai
       volumes:
         - /var/run/docker.sock:/var/run/docker.sock:ro
       restart: unless-stopped
     clp-all:
       image: x1ao4/chinese-localization-for-plex:latest
       container_name: clp-all
       command: python chinese-localization-for-plex.py --all
       environment:
         - TZ=Asia/Shanghai
       volumes:
         - /自定义目录/chinese-localization-for-plex/config:/app/config
     clp-new:
       image: x1ao4/chinese-localization-for-plex:latest
       container_name: clp-new
       command: python chinese-localization-for-plex.py --new
       ports:
         - 8088:8088
       environment:
         - TZ=Asia/Shanghai
       volumes:
         - /自定义目录/chinese-localization-for-plex/config:/app/config
       restart: unless-stopped
   networks: {}
   ```
- 非 Plex Pass 订阅用户
  
   ```
   version: "2"
   services:
     clp-scheduler:
       image: mcuadros/ofelia:latest
       container_name: clp-scheduler
       depends_on:
         - clp-all
       command: daemon --docker -f label=com.docker.compose.project=${COMPOSE_PROJECT_NAME}
       labels:
         ofelia.job-run.clp-all.schedule: 0 30 22 * * *
         ofelia.job-run.clp-all.container: clp-all
       environment:
         - TZ=Asia/Shanghai
       volumes:
         - /var/run/docker.sock:/var/run/docker.sock:ro
       restart: unless-stopped
     clp-all:
       image: x1ao4/chinese-localization-for-plex:latest
       container_name: clp-all
       command: python chinese-localization-for-plex.py --all
       environment:
         - TZ=Asia/Shanghai
       volumes:
         - /自定义目录/chinese-localization-for-plex/config:/app/config
   networks: {}
   ```

#### 使用方法
1. 在 Plex 服务器的设置选项中找到 `Webhooks`，点击 `添加 Webhook`，填写你的 Flask 服务器地址 `http://Docker 所在设备的 IP 地址:8088` 并 `保存修改`。（非 Plex Pass 订阅用户无需填写）
2. 下载仓库中的 `compose.yaml` 文件（非 Plex Pass 订阅用户可删除 `clp-new` 的部分），将其保存在一个名为 `chinese-localization-for-plex` 的文件夹内。
3. 用记事本或文本编辑打开 `compose.yaml`，将 `/自定义目录/chinese-localization-for-plex/config` 替换为宿主机上的一个目录，这个目录将用于保存配置文件。（`clp-all` 与 `clp-new` 使用相同的目录即可）
4. 打开终端或命令行工具，使用 `cd` 命令切换到 `compose.yaml` 所在的目录。
5. 使用命令 `docker-compose up -d` 部署并启动 chinese-localization-for-plex 堆栈。
6. 用记事本或文本编辑打开 `/自定义目录/chinese-localization-for-plex/config/config.ini` 文件，填写你的 Plex 服务器地址（`address`）和 [X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)（`token`），按照需要选填其他配置选项。
7. 重启 chinese-localization-for-plex 堆栈即可正常运行。

#### 运行说明
堆栈 chinese-localization-for-plex 包含了 `clp-all`、`clp-new` 和 `clp-scheduler` 三个容器，分别用于处理不同的任务。启动堆栈后，这三个容器的运行状态也略有差异。

- 容器 `clp-all` 是用来运行 `处理所有项目` 任务的，它会在启动后运行一次 `处理所有项目` 任务，对设置范围内的所有项目进行处理，并在终端或日志内显示资料库的信息和处理结果，处理完毕后会停止运行。你可以随时启动它来运行 `处理所有项目` 任务，它将在每次处理完毕后停止运行。如果你配置了 `clp-scheduler`，`clp-all` 也会在每次到达你设置的任务时间时自动运行一次。
- 容器 `clp-new` 是用来运行 `处理新增项目` 任务的，它会在启动后创建一个 Flask 服务器来监听 Plex 服务器的事件，当 Plex 服务器上有新增项目时，它将自动对新增项目进行处理，并在终端或日志内显示处理结果，处理完毕后会继续监听 Plex 服务器的事件，并在每次有新增项目时对其进行处理，然后继续监听。
- 容器 `clp-scheduler` 是用来给 `处理所有项目` 设置/触发计划任务的，它会在启动后创建一个定时运行 `clp-all` 的计划任务，默认设置为 `0 30 22 * * *`，表示每天晚上 10 点半（22:30）运行一次。你可以通过修改时间表达式来自定义运行频率，例如 `"@every 3h"` 表示每 3 小时运行一次，`"@every 30m"` 表示每 30 分钟运行一次等。它将在设置的任务时间启动 `clp-all` 容器，并在终端或日志内同步显示 `clp-all` 的日志信息，然后继续运行。

你可以根据需要选配这三个容器，若存在不需要的功能，直接在 Compose 中删除对应的部分再部署即可。

### 通过 Python 脚本运行

#### 运行条件
- 安装了 Python 3.0 或更高版本。
- 使用命令 `pip3 install -r requirements.txt` 安装了必要的第三方库。

#### 使用方法
1. 通过 [Releases](https://github.com/x1ao4/chinese-localization-for-plex/releases) 下载最新版本的压缩包并解压到本地目录中。
2. 用记事本或文本编辑打开目录中的 `/config/config.ini` 文件，填写你的 Plex 服务器地址（`address`）和 [X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)（`token`），按照需要选填其他配置选项。
3. 在 Plex 服务器的设置选项中找到 `Webhooks`，点击 `添加 Webhook`，填写你的 Flask 服务器地址 `http://脚本所在设备的 IP 地址:8088` 并 `保存修改`。（非 Plex Pass 订阅用户无需填写）
4. 打开终端或命令行工具，使用 `cd` 命令切换到脚本所在的目录。
5. 使用命令 `python3 chinese-localization-for-plex.py --all` 可运行 `处理所有项目` 任务，脚本将对设置范围内的所有项目进行处理，并在控制台显示资料库的信息和处理结果，处理完毕后会结束运行。
6. 使用命令 `python3 chinese-localization-for-plex.py --new` 可运行 `处理新增项目` 任务，脚本将创建一个 Flask 服务器来监听 Plex 服务器的事件，当 Plex 服务器上有新增项目时，脚本将自动对新增项目进行处理，并在控制台显示处理结果，处理完毕后会继续监听 Plex 服务器的事件，并在每次有新增项目时对其进行处理，然后继续监听。

#### 快速启动
PC 用户也可以通过提供的快速启动脚本来执行任务：

- 双击 `clp-all.bat (Win)` 或 `clp-all.command (Mac)` 脚本可以快速启动 `处理所有项目` 任务。
- 双击 `clp-new.bat (Win)` 或 `clp-new.command (Mac)` 脚本可以快速启动 `处理新增项目` 任务。

#### 自动运行
为了便于使用，你也可以通过 crontab 或其他任务工具，为 CLP 添加定时或开机任务，实现自动运行。

- 处理所有项目（Mac）
  
  1. 在终端使用命令 `crontab -e` 打开 crontab 文件。
  2. 按 `i` 进入插入模式，添加行 `30 22 * * * /path/to/clp-all.command > /dev/null 2>&1`。（请把 `/path/to/clp-all.command` 替换为脚本的实际路径）
  3. 按 `Esc` 退出插入模式，输入 `:wq`，按 `Enter` 保存更改并退出编辑器。

  这样就为 `处理所有项目` 添加了一个每天晚上 10 点半（22:30）运行一次的定时任务。你可以通过修改时间表达式来自定义运行频率，例如 `0 */3 * * *` 表示每 3 小时运行一次，`*/30 * * * *` 表示每 30 分钟运行一次等。（脚本将在后台运行）

- 处理新增项目（Mac）
  
  1. 用文本编辑打开 `clp-new.command` 文件，在第二行输入 `sleep 10` 保存更改并关闭文件。
  2. 在终端使用命令 `crontab -e` 打开 crontab 文件。
  3. 按 `i` 进入插入模式，添加行 `@reboot /path/to/clp-new.command`。（请把 `/path/to/clp-new.command` 替换为脚本的实际路径）
  4. 按 `Esc` 退出插入模式，输入 `:wq`，按 `Enter` 保存更改并退出编辑器。

  这样我们就将 `处理新增项目` 设置为了 Mac 的开机启动任务，任务会在开机 10 秒后运行，延迟 10 秒是为了保证 Plex 服务器比脚本先启动，否则脚本将无法连接到 Plex 服务器。（脚本将在后台运行）

- 处理所有项目（Nas）
  
  通过自带的任务计划功能为 `处理所有项目` 添加定时任务（计划的任务）。添加任务后在 `任务设置 - 运行命令 - 用户自定义脚本` 中输入 `python3 /path/to/chinese-localization-for-plex.py --all`，然后按需要设置运行时间即可。（请把 `/path/to/chinese-localization-for-plex.py` 替换为脚本的实际路径）
  
- 处理新增项目（Nas）
  
  通过自带的任务计划功能将 `处理新增项目` 设置为开机启动任务（触发的任务）。添加任务后在 `任务设置 - 运行命令 - 用户自定义脚本` 中输入 `sleep 10 && python3 /path/to/chinese-localization-for-plex.py --new`，这样脚本会在 Nas 启动 10 秒后再运行，延迟 10 秒是为了保证 Plex 服务器比脚本先启动，否则脚本将无法连接到 Plex 服务器。（请把 `/path/to/chinese-localization-for-plex.py` 替换为脚本的实际路径）

若设置为定时或开机任务后脚本运行失败，你可能需要将 command 脚本或用户自定义脚本中的 `python3` 替换为 `python3` 的实际路径。你可以在 Mac 终端或 Nas 的 SSH 内通过命令 `which python3` 找到 `python3` 的实际路径。

## 注意事项
- 请确保你提供了正确的 Plex 服务器地址和正确的 X-Plex-Token。
- 请确保你提供了正确的库名，并按要求进行了填写。
- 如果无法连接到 Plex 服务器，请检查你的网络连接，并确保服务器可以访问。如果你是通过 Docker 容器运行的，也可以尝试使用 `host` 模式重新部署容器运行。
- 请使用服务器管理员账号的 X-Plex-Token，以确保你拥有足够的权限进行操作。
- 标题包含日文假名的项目会在处理标题排序时被跳过，不会进行拼音排序的处理。
- 所有被处理的字段将在变更后被锁定，以防止在刷新元数据时被重置。若有修改需求，可以手动解锁对应的字段，然后进行修改。
- 修改配置文件后，需要重启容器，新的配置信息才会生效。
- Windows 用户运行 Python 脚本后，若没有任何反应，请将运行命令或启动脚本中的 `python3` 替换为 `python` 再运行。
- 如需使用 `处理新增项目` 模式，请确保你在服务器的 `设置 - 网络` 中勾选了 `Webhooks` 选项。

## 感谢
本工具参考 [plex_localization_zhcn](https://github.com/sqkkyzx/plex_localization_zhcn) 和 [plexpy](https://github.com/anooki-c/plexpy) 对代码进行了重构、更新和完善，感谢 [timmy0209](https://github.com/timmy0209)、[sqkkyzx](https://github.com/sqkkyzx) 和 [anooki-c](https://github.com/anooki-c) 贡献代码。

## 赞赏
如果你觉得这个项目对你有用，可以请我喝杯咖啡。如果你喜欢这个项目，可以给我一个⭐️。谢谢你的支持！

<img width="399" alt="赞赏" src="https://github.com/x1ao4/chinese-localization-for-plex/assets/112841659/b7b19cde-9412-4ab3-acc3-c932a4a03f3b">
