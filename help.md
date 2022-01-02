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

### 2021/1/1更新

1. 修复不会进入uac提示页面的bug
