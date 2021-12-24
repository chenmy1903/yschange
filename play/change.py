import os
import sys
import wmi
import argparse
import requests
import ctypes
import win32com.client as client
import configparser

from pickleshare import PickleShareDB

__version__ = "1.0"

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
        if value:
            new[key] = value
            self.db[self.file_name] = new

    def read(self, config=None):
        """读文件"""
        if config:
            return self.db[self.file_name][config]
        return self.db[self.file_name]


def createShortCut(filename, lnkname, commands: list = None):
    shortcut = shell.CreateShortCut(lnkname)
    shortcut.TargetPath = filename 
    if commands:
        shortcut.Arguments = " ".join(commands)
    shortcut.WorkingDirectory = os.path.dirname(filename)
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
    disks = [disk.Caption for disk in w.Win32_LogicalDisk(DriveType=3)] if not disks else disks
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

def search_path(file_name: str, path: str = "C:/", assert_file=None):
    print()
    cp = os.walk(path)
    total = 0
    count = 0
    for root, dirs, files in cp:
        root = str(root)
        dirs = str(dirs)
        count += 1
        total += 1
        if file_name in dirs or file_name in files:
            flag = 1
            if assert_file in os.listdir(root) and "$Recycle.Bin" not in os.path.join(root, file_name):
                return os.path.join(root, file_name)
    print("\n")
    print(f"寻找完成，一共{total}个文件")
    return None

def read_argvs():
    parser = argparse.ArgumentParser(get_file().replace('\\', '/').split("/")[-1])
    parser.add_argument("--path", help="重新设置启动器目录", action='store_true')
    parser.add_argument("--bilibili", help="使用bilibili服务器启动", action='store_true')
    parser.add_argument("--mihoyo", help="使用米哈游服务器启动", action='store_true')
    parser.add_argument("--change", help="设置服务器（bilibili：哔哩哔哩，mihoyou：米哈游，不区分大小写） 例： --change bilibili 切换到bilibili服务器")
    parser.add_argument("--link", help="生成所有服务器的快捷方式", action='store_true')
    return parser.parse_args()

config = Setting("base_config")

def set_path():
    print("尝试检测游戏目录")
    ys_launcher = search_dir("launcher.exe", assert_file="7z.exe")
    if not ys_launcher:
        print("启动器不存在")
        pause()
        sys.exit()
    print(ys_launcher)
    print("尝试寻找《原神》游戏")
    ys_game = search_path("YuanShen.exe", os.path.dirname(os.path.abspath(ys_launcher)))
    if not ys_game:
        print("尝试启动备用寻找方案")
        ys_game = search_dir("YuanShen.exe", assert_file="UnityPlayer.dll")
        if not ys_game:
            print("未找到游戏")
            pause()
            sys.exit()
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
    if link:
        create_links("bilibili")

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

def get_file():
    if os.path.isfile(__file__):
        return __file__
    else:
        return __file__.replace('.py', '.exe')

def command_mode(game_path, launcher_path):
    commands_dict = {"1": lambda: change_bilibili(game_path, link=True), 
            "2": lambda: change_mihoyo(game_path, link=True), 
            "3": lambda: os.system("\"" + launcher_path + "\""),
            "4": create_links, 
            "5": sys.exit
            }
    print("指令：")
    print("1. 切换到Bilibili服务器")
    print("2. 切换到miHoYo服务器")
    print("3. 启动游戏")
    print("4. 创建快捷方式（全部渠道服）")
    print("5. 退出")
    while True:
        res = input("请输入功能序号：")
        if res not in commands_dict:
            print("\r输入错误")
        else:
            break
    commands_dict[res]()

def create_links(mode="all"):
    if mode == "all":
        createShortCut(get_file(), f"{os.path.expanduser('~')}/Desktop/原神 [BiliBili世界树].lnk", ["--bilibili"])
        createShortCut(get_file(), f"{os.path.expanduser('~')}/Desktop/原神 [miHoYo天空岛].lnk", ["--mihoyo"])
    elif mode == "mihoyo":
        createShortCut(get_file(), f"{os.path.expanduser('~')}/Desktop/原神 [miHoYo天空岛].lnk", ["--mihoyo"])
    elif mode == 'bilibili':
        createShortCut(get_file(), f"{os.path.expanduser('~')}/Desktop/原神 [BiliBili世界树].lnk", ["--bilibili"])
    print("快捷方式创建成功")
        

def main():
    title("鸭皇·游戏")
    print("《原神》游戏管理工具")
    print(f"版本：{__version__}")
    print("by 鸭皇游戏")
    if "launcher_path" not in config.read() and "game_path" not in config.read():
        set_path()

    launcher_path = config.read("launcher_path")
    game_path = config.read("game_path")
    print(f"启动器: {launcher_path}\n游戏: {game_path}")

    argv = read_argvs()
    if argv.mihoyo:
        change_mihoyo(game_path)
        os.system(f"\"{launcher_path}\"")
    elif argv.bilibili:
        print("准备启动")
        change_bilibili(game_path)
        os.system(f"\"{launcher_path}\"")
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
        create_links()
    else:
        command_mode(game_path, launcher_path)
        pause()

if __name__ == "__main__":
    main()

