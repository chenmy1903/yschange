@echo off
cls
title 鸭皇 - 开发中生成工具
echo 准备启动生成
pyinstaller -F -i ..\favicon.ico change.py --uac-admin --distpath .\
echo 清除缓存
rd /s/q .\change.spec
rd /s/q .\build
rd /s/q .\__pycache__
echo Done
pause
exit