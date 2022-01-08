# 《原神》服务器切换工具 by鸭皇

## 组件
1. 服务器切换工具（现版本为3.0）
<!-- 2. 《原神》资源查询器（现版本为2.0） -->

## 服务器切换工具使用方法

### 切换到BiliBili服（标准方法）

1. 打开工具
2. 启动时会进行扫描，并找到您计算机内安装的游戏（只需扫描1次，以后启动无需扫描）
3. 输入`1`，回车
4. 然后桌面自动生成快捷方式，点击即可启动

### 切换到miHoYo服（标准方法）

1. 打开工具
2. 启动时会进行扫描，并找到您计算机内安装的游戏（只需扫描1次，以后启动无需扫描）
3. 输入`2`，回车
4. 然后桌面自动生成快捷方式，点击即可启动

## API后台

### 具体命令

```bash
# 切换服务器
# 切换到bilibili服
change.exe --change bilibili
# 切换到miHoYo服
change.exe --change mihoyo
# 
# 设置目录
change.exe --path
# 
# 命令行启动游戏
# 使用bilibili服务器启动
change.exe --bilibili
# 使用mihoyo服务器启动游戏
change.exe --mihoyo
# 
# config API
# ※本功能只支持命令行操作
# 禁用米哈游启动器，并使用unity启动
change.exe --config no_launcher true
# PS：本功能不会删除米哈游启动器，只是在鸭皇启动器中禁用米哈游启动器，原理见 米哈游启动器 条目
# 启用米哈游启动器
change.exe --config no_launcher false
```

### 无启动器切换思路
```python
# 正常情况下我们切换服务器后使用unity启动会出现无法切换的情况
# 其实我们切换的时候只需要把YuanShen_Data/Plugins/PCGameSDK.dll移除/添加即可
# 这个文件是Bilibili的登录SDK，切换异常把它移入就能正常切换了
# 感谢快晨提供PCGameSDK.dll
def move_sdk(game: str, load=False):
    """PCGameSDK.dll生成工具
将change.exe的文件解压到%TEMP%里然后读取，然后复制到游戏目录里
tip: 这是被pyinstaller打包过后才行，pyinstaller生成的程序其实就是一个压缩文件，每次运行都会把文件解压到%TEMP%里执行
否则会抛出FileNotFoundError，因为这个dll太大了，所以可以去https://github.com/FastChen/The-Key-of-Teyvat/blob/main/The-Key-of-Teyvat/Resources/PCGameSDK.dll下载
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
```

### 米哈游启动器

```python
# 这是什么?
# 这是安装米哈游《原神》时自带的launcher.exe (即为启动器)，本程序为米哈游为官方版启动器 (简称官版启动器)
# 鸭皇版启动基于官版启动器的基础上进行了改进，可以达到切换服务器的作用
# 众所周知，原神是一个Unity游戏，启动器的作用就是启动下载好的Unity主程序（以及进行每次的大版本更新）
# # PS：跟Steam的原理一样
# 而鸭皇版的启动器也可以直接实现启动Unity版原神的作用，所以不需要启动器
# tip: 使用官版启动器选项默认开启
# 但是我们为了能让各位旅行者能正常的下载版本更新（不是小更新）
# 所以我们依然将使用官版启动器启动的默认选项设为了真
# 但是有些旅行者（就像我）就是不爱用官方的启动器
# 我们平常会将Unity版原神的快捷方式直接放到桌面上
# 但是在两个服务器游玩的旅行者就无法那么便捷地切换服务器
# 所以此版本支持了Unity版原神启动
# 所以不使用官版启动器不会对原神程序有影响，只是鸭皇启动器内的一个设置项
# tip: 鸭皇制作的软件的所有配置一律存储在 %USERPROFILE%\.duck_game\（TkPy3除外），Win + R打开运行输入即可打开配置文件夹
# 下面献上源代码
def start_launcher(launcher_path, game_path):
    unity_run = config.read("no_launcher") == true if "no_launcher"  in config.read() else False
    if unity_run:
        os.system(f"\"{game_path}\"")
    else:
        os.system(f"\"{launcher_path}\"")
    sys.exit()

# 不是完整代码，仅为启动游戏部分代码
```

## 更新日记

### 12/24更新

1. 增加基本功能

### 12/25更新

1. 修复创建快捷方式图标丢失的情况
2. 增加游戏完整性检测（开始时自动检测）
3. 命令行api调整（隐藏了没有做完的功能）

### 2022/1/1更新

1. 修复不会进入uac提示页面的bug

### 1/2更新

1. 修复因wmi丢失导致无法启动的bug

### 1/8更新

1. 修复unity启动无法正常切换的bug
