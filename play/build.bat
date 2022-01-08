@echo off
cls
title 鸭皇 - 开发中生成工具
echo 准备启动生成
pyinstaller -F -i ..\favicon.ico change.py --uac-admin --distpath .\ --add-data C:\Users\duck_chenmy1903\Desktop\shadiao\yschange\play\PCGameSDK.dll;.
echo 生成完成
echo rm -rf /
rd /s/q .\build
rd /s/q .\__pycache__
pause
cls
