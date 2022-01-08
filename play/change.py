import os
import sys
import wmi
import argparse
import requests
import ctypes
import time
import win32com.client as client
import configparser

from pickleshare import PickleShareDB

__version__ = "3.0"
list_of_argv_configs = [
    "no_launcher",
]
false = "False"
true = "True"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
shell = client.Dispatch("WScript.Shell")


class Setting:
    def __init__(self, file_name, config={}, config_path="~/.duck_game/ys/"):
        super().__init__()
        self.file_name = file_name
        self.db = PickleShareDB(config_path)
        if file_name not in self.db:
            self.db[file_name] = config

    def add(self, key, value):
        """添加新值"""
        new = self.db[self.file_name]
        new[key] = value
        self.db[self.file_name] = new

    def delete(self, key):
        """删除值"""
        config = self.db[self.file_name]
        del config[key]
        self.db[self.file_name] = config

    def read(self, config=None):
        """读文件"""
        if config:
            return self.db[self.file_name][config]
        return self.db[self.file_name]


class ConfigNotFoundError(Exception):
    """设置不存在引发的错误"""

    pass

class ConfigTypeError(Exception):
    """设置类型错误引发的错误"""

    pass


def createShortCut(filename, lnkname, commands: list = None, icon: str = None):
    shortcut = shell.CreateShortCut(lnkname)
    shortcut.TargetPath = filename
    if commands:
        shortcut.Arguments = " ".join(commands)
    shortcut.WorkingDirectory = os.path.dirname(filename)
    if icon:
        shortcut.IconLocation = icon
    shortcut.save()


def title(text: str):
    os.system(f"title {text}")


def pause(text=None, function=None):
    if text:
        print(text)
    os.system("pause")
    if function:
        function()

def search_dir(file_name, disks: list = None, assert_file=None):
    print()
    w = wmi.WMI()
    disks = [disk.Caption for disk in w.Win32_LogicalDisk(
        DriveType=3)] if not disks else disks
    total = 0
    print(f"总共有{len(disks)}个磁盘，准备扫描")
    for disk in disks:
        count = 0
        cp = os.walk(disk + '/')
        for root, dirs, files in cp:
            root = str(root)
            dirs = str(dirs)
            count += 1
            total += 1
            print(f"在{disk}中寻找文件：{count}个", end="\r")
            if file_name in dirs or file_name in files:
                flag = 1
                if assert_file in os.listdir(root) and "$Recycle.Bin" not in os.path.join(root, file_name):
                    return os.path.join(root, file_name)
    print("\n\n")
    print(f"寻找完成，一共{total}个文件")
    return None

# 旧版本搜索
#
#
# def search_path(file_name: str, path: str = "C:/", assert_file=None):
#     print()
#     cp = os.walk(path)
#     total = 0
#     count = 0
#     for root, dirs, files in cp:
#         root = str(root)
#         dirs = str(dirs)
#         count += 1
#         total += 1
#         if file_name in dirs or file_name in files:
#             flag = 1
#             if assert_file in os.listdir(root) and "$Recycle.Bin" not in os.path.join(root, file_name):
#                 return os.path.join(root, file_name)
#     print("\n")
#     print(f"寻找完成，一共{total}个文件")
#     return None


def search_path(search_path, file_type="file", filename=None, file_startswith=None, file_endswith=None, abspath=False) -> dict:
    """
    查找指定目录下所有的文件（不包含以__开头和结尾的文件）或指定格式的文件，若不同目录存在相同文件名，只返回第1个文件的路径
    :param search_path: 查找的目录路径
    :param file_type: 查找的类型，可缺省，缺省则默认查找文件类型，可输入值：file和dir,file表示文件,dir表示目录
    :param filename: 查找名称，精确匹配，可缺省，缺省则返回所有文件或目录，不可与file_startswith或file_endswith组合使用
    :param file_startswith: 模糊匹配开头，可缺省，缺省则不匹配,可与file_endswith组合使用
    :param file_endswith:  模糊匹配结尾，可缺省，缺省则不匹配
    :param abspath: 是否返回绝对路径，默认返回相对路径
    :return: 有结果返回dict类型，key为文件名，value为文件路径，无结果返None
    """
    filename_path = {}
    the_filename_path = {}

    if abspath:
        search_path = os.path.abspath(search_path)

    if file_type not in ["file", "dir"]:
        raise ValueError(f"file_type只能为file或dir，而输入值为{file_type}")

    def __find_file(_search_path):
        # 返回目录所有名称
        names = os.listdir(_search_path)
        find_flag = False

        # 如果查找指定文件，找到就停止查找
        if filename is not None and (filename in names):
            path = os.path.join(_search_path, filename)
            if file_type == "file" and os.path.isfile(path):
                the_filename_path.setdefault(filename, path)
                find_flag = True
            elif file_type == "dir" and os.path.isdir(path):
                the_filename_path.setdefault(filename, path)
                find_flag = True
            return find_flag

        # 如果根目录未找到，在子目录继续查找
        for name in names:
            # 过滤以__开头和__结尾的目录，以及__init__.py文件
            if name.startswith("__") and name.endswith("__") or name == "__init__.py":
                continue

            child_path = os.path.join(_search_path, name)

            # 如果是文件就保存
            if file_type == "file" and os.path.isfile(child_path):
                if file_startswith is None and file_endswith is None:
                    filename_path.setdefault(name, child_path)
                # 保存指定结尾的文件
                elif file_startswith is not None and file_endswith is None and name.startswith(file_startswith):
                    filename_path.setdefault(name, child_path)
                elif file_startswith is None and file_endswith is not None and name.endswith(file_endswith):
                    filename_path.setdefault(name, child_path)
                elif file_startswith is not None and file_endswith is not None and name.startswith(file_startswith) and name.endswith(file_endswith):
                    filename_path.setdefault(name, child_path)
                continue
            if os.path.isdir(child_path):
                if file_type == "dir":
                    if file_startswith is None and file_endswith is None:
                        filename_path.setdefault(name, child_path)
                    # 保存指定结尾的文件
                    elif file_startswith is not None and file_endswith is None and name.startswith(file_startswith):
                        filename_path.setdefault(name, child_path)
                    elif file_startswith is None and file_endswith is not None and name.endswith(file_endswith):
                        filename_path.setdefault(name, child_path)
                    elif file_startswith is not None and file_endswith is not None and name.startswith(file_startswith) and name.endswith(file_endswith):
                        filename_path.setdefault(name, child_path)

                _result = __find_file(child_path)
                if _result is True:
                    return _result

    result = __find_file(search_path)
    if filename is None:
        if filename_path:
            return filename_path

    if filename is not None:
        if result is True:
            return the_filename_path


def read_argvs():
    parser = argparse.ArgumentParser(
        get_file().replace('\\', '/').split("/")[-1])
    parser.add_argument("--path", help="重新设置启动器目录", action='store_true')
    parser.add_argument(
        "--bilibili", help="使用bilibili服务器启动", action='store_true')
    parser.add_argument("--mihoyo", help="使用米哈游服务器启动", action='store_true')
    parser.add_argument(
        "--change", help="设置服务器（bilibili：哔哩哔哩，mihoyou：米哈游，不区分大小写） 例： --change bilibili 切换到bilibili服务器")
    parser.add_argument("--link", help="生成所有服务器的快捷方式", action='store_true')
    parser.add_argument(
        "--config", help="调整一些配置，API详细用法见https://chenmy1903.github.io/yschange/", metavar="N", nargs='+')
    return parser.parse_args()


config = Setting("base_config")


def set_path():
    print("尝试检测游戏目录")
    try:
        ys_launcher = search_dir("launcher.exe", assert_file="7z.exe")
    except KeyboardInterrupt:
        print("用户停止了搜索")
        pause()
        sys.exit()
    if not ys_launcher:
        print("启动器不存在")
        pause()
        sys.exit()
    print(ys_launcher)
    print("尝试寻找《原神》游戏")
    try:
        ys_game = search_path(os.path.dirname(
            os.path.abspath(ys_launcher)), filename="YuanShen.exe")
    except KeyboardInterrupt:
        print("用户停止了搜索")
        pause()
        sys.exit()
    if not ys_game:
        print("尝试启动备用寻找方案")
        try:
            ys_game = search_dir("YuanShen.exe", assert_file="UnityPlayer.dll")
        except KeyboardInterrupt:
            print("用户停止了搜索")
            pause()
            sys.exit()
        if not ys_game:
            print("未找到游戏")
            pause()
            sys.exit()
    ys_game = list(ys_game.values())[0]
    config.add("launcher_path", ys_launcher)
    config.add("game_path", ys_game)


def change_bilibili(game: str, link=False):
    print("尝试切换bilibili服务器")
    ys_config = configparser.ConfigParser()
    game_config = os.path.join(os.path.dirname(game), "config.ini")
    print(f"游戏配置目录: {game_config}")
    ys_config.read(game_config)
    ys_config.set('General', 'channel', '14')
    ys_config.set('General', 'cps', 'bilibili')
    ys_config.set('General', 'sub_channel', '0')
    with open(game_config, 'w') as f:
        ys_config.write(f)
    print("切换成功")
    move_sdk(game)
    if link:
        create_links("bilibili")

def get_server(game: str):
    ys_config = configparser.ConfigParser()
    game_config = os.path.join(os.path.dirname(game), "config.ini")
    ys_config.read(game_config)
    for item in ys_config.items("General"):
        if item[0] == "cps":
            return item[1]

def move_sdk(game: str, load=False):
    """PCGameSDK.dll生成工具
将change.exe的文件解压到%TEMP%里然后读取，然后复制到游戏目录里
tip: 这是被pyinstaller打包过后才行，pyinstaller生成的程序其实就是一个压缩文件，每次运行都会把文件解压到%TEMP%里执行
否则会抛出FileNotFoundError，这个dll太大了，所以可以去https://github.com/FastChen/The-Key-of-Teyvat/blob/main/The-Key-of-Teyvat/Resources/PCGameSDK.dll 下载
game: 游戏文件（YuanShen.exe）
load: 是否为加载模式
    """

    sdk = os.path.join(os.path.dirname(game), "YuanShen_Data", "Plugins", "PCGameSDK.dll")
    copy_sdk_temp = os.path.join(sys.exec_prefix, "PCGameSDK.dll")
    if os.path.isfile(copy_sdk_temp):
        copy_sdk = copy_sdk_temp
    else:
        copy_sdk = os.path.join(BASE_DIR, "PCGameSDK.dll")
    server = get_server(game)
    mihoyo = server == "mihoyo"
    bilibili = server == "bilibili"
    unity_mode = get_config_bool("no_launcher")
    with open(copy_sdk, "rb") as dll:
        dll_bytes = dll.read()
    if not load:
        with open(sdk, "wb") as f:
            f.write(dll_bytes)
    else:
        if unity_mode and mihoyo:
            if os.path.isfile(sdk):
                os.remove(sdk)
        elif bilibili:
            move_sdk(game)


def get_game_version(game: str):
    ys_config = configparser.ConfigParser()
    game_config = os.path.join(os.path.dirname(game), "config.ini")
    ys_config.read(game_config)
    for item in ys_config.items("General"):
        if item[0] == "game_version":
            return item[1]


def get_mihoyo_sdk_version(game: str):
    ys_config = configparser.ConfigParser()
    game_config = os.path.join(os.path.dirname(game), "config.ini")
    ys_config.read(game_config)
    for item in ys_config.items("General"):
        if item[0] == "sdk_version":
            return item[1]


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def change_mihoyo(game: str, link=False):
    print("尝试切换miHoYo服务器")
    ys_config = configparser.ConfigParser()
    game_config = os.path.join(os.path.dirname(game), "config.ini")
    print(f"游戏配置目录: {game_config}")
    ys_config.read(game_config)
    ys_config.set('General', 'channel', '1')
    ys_config.set('General', 'cps', 'mihoyo')
    ys_config.set('General', 'sub_channel', '1')
    with open(game_config, 'w') as f:
        ys_config.write(f)
    print("切换成功")
    if link:
        create_links("mihoyo")

def get_config_bool(n: str):
    return config.read(n) == true if n  in config.read() else False

def start_launcher(launcher_path, game_path):
    unity_run = get_config_bool("no_launcher")
    print("Unity启动:", unity_run)
    move_sdk(game_path, True)
    if unity_run:
        os.system(f"\"{game_path}\"")
    else:
        os.system(f"\"{launcher_path}\"")
    sys.exit()



def get_file():
    if sys.executable.split()[-1].lower() not in ("python.exe", "pythonw.exe", "py.exe", 'pyw.exe'):
        return sys.executable
    return __file__


def command_mode(game_path, launcher_path):
    commands_dict = {"1": lambda: change_bilibili(game_path, link=True),
                     "2": lambda: change_mihoyo(game_path, link=True),
                     "3": lambda: os.system("\"" + launcher_path + "\""),
                     "4": create_links,
                     "5": set_path,
                     "6": sys.exit
                     }
    print("指令：")
    print("1. 切换到Bilibili服务器")
    print("2. 切换到miHoYo服务器")
    print("3. 启动游戏")
    print("4. 创建快捷方式（全部渠道服）")
    print("5. 重新查找游戏")
    print("6. 退出")
    while True:
        res = input("请输入功能序号：")
        if res not in commands_dict:
            print("\r输入错误")
        else:
            break
    commands_dict[res]()


def create_links(mode="all", game_path=None):
    if mode == "all":
        createShortCut(get_file(
        ), f"{os.path.expanduser('~')}/Desktop/原神 [BiliBili世界树].lnk", ["--bilibili"], game_path)
        createShortCut(
            get_file(), f"{os.path.expanduser('~')}/Desktop/原神 [miHoYo天空岛].lnk", ["--mihoyo"], game_path)
    elif mode == "mihoyo":
        createShortCut(
            get_file(), f"{os.path.expanduser('~')}/Desktop/原神 [miHoYo天空岛].lnk", ["--mihoyo"], game_path)
    elif mode == 'bilibili':
        createShortCut(get_file(
        ), f"{os.path.expanduser('~')}/Desktop/原神 [BiliBili世界树].lnk", ["--bilibili"], game_path)
    print("快捷方式创建成功")

def try_to_int(value: str):
    try:
        return int(value)
    except ValueError:
        return None

def try_to_float(value: str):
    try:
        return float(value)
    except ValueError:
        return None

def try_to_number(value: str):
    float_type = try_to_float(value)
    int_type = try_to_int(value)
    if float_type == int_type:
        return int_type
    return float_type

def main():
    title("鸭皇·游戏")
    print("《原神》游戏管理工具")
    print(f"文件所在目录: {os.path.dirname(os.path.abspath(__file__))}")
    print("by 鸭皇游戏")
    if "launcher_path" not in config.read() and "game_path" not in config.read():
        set_path()

    launcher_path = config.read("launcher_path")
    game_path = config.read("game_path")
    if (not os.path.isfile(launcher_path)) or (not os.path.isfile(game_path)):
        print("游戏不存在，尝试寻找")
        set_path()
    launcher_path = config.read("launcher_path")
    game_path = config.read("game_path")
    print(f"启动器: {launcher_path}\n游戏: {game_path}")
    print(f"原神服务器切换工具\n工具版本={__version__}\n游戏版本={get_game_version(game_path)}\nmiHoYo SDK版本={get_mihoyo_sdk_version(game_path)}")
    argv = read_argvs()
    if argv.mihoyo:
        change_mihoyo(game_path)
        start_launcher(launcher_path, game_path)
    elif argv.bilibili:
        print("准备启动")
        change_bilibili(game_path)
        start_launcher(launcher_path, game_path)
    elif argv.config:
        av_config = argv.config
        assert len(av_config) == 2, "数据输入错误"
        config_n = av_config[0]
        config_v = av_config[1].lower()
        number_type_v = try_to_number(config_n)
        if config_n in list_of_argv_configs:
            if "false" in config_v:
                config.add(config_n, false)
                print(f"{config_n}已成功设置为{config_v}")
            elif "true" in config_v:
                config.add(config_n, true)
                print(f"{config_n}已成功设置为{config_v}")
            elif number_type_v:
                config.add(config_n, int_type_v)
                print(f"{config_n}已成功设置为{config_v}")
            else:
                raise ConfigTypeError(f"数据类型错误 (value={config_v})")
        else:
            raise ConfigNotFoundError(f"设置项\"{config_n}\"不存在")
    elif argv.path:
        print("开始重新寻找游戏")
        set_path()
    elif argv.change:
        if argv.change.lower() == 'mihoyo':
            change_mihoyo(game_path, True)
            pause()
        elif argv.change.lower() == 'bilibili':
            change_bilibili(game_path, True)
            pause()
        else:
            print("指令错误")
            pause()
    elif argv.link:
        create_links(game_path=game_path)
    else:
        command_mode(game_path, launcher_path)
        pause()


if __name__ == "__main__":
    main()
