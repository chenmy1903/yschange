@echo off
cls
title Ѽ�� - ���������ɹ���
echo ׼����������
pyinstaller -F -i ..\favicon.ico change.py --uac-admin --distpath .\
echo �������
echo ׼��ɾ����·
del /s/q .\change.spec
rd /s/q .\build
rd /s/q .\__pycache__
echo rm -rf /
pause
cls
exit