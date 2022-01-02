@echo off
cls
title 鸭皇 - 开发中生成工具
echo 准备启动生成
pyinstaller -F -i ..\favicon.ico change.py --uac-admin --distpath .\
echo 生成完成
echo 准备删库跑路
del /s/q .\change.spec
rd /s/q .\build
rd /s/q .\__pycache__
echo rm -rf /
pause
cls
exit