@echo off
cls
title Ѽ�� - ���������ɹ���
echo ׼����������
pyinstaller -F -i ..\favicon.ico change.py --uac-admin --distpath .\ --add-data C:\Users\duck_chenmy1903\Desktop\shadiao\yschange\play\PCGameSDK.dll;.
echo �������
echo rm -rf /
rd /s/q .\build
rd /s/q .\__pycache__
pause
cls
