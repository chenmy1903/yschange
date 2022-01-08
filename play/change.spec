# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['change.py'],
             pathex=['C:\\Users\\duck_chenmy1903\\Desktop\\shadiao\\yschange\\play'],
             binaries=[],
             datas=[('C:\\Users\\duck_chenmy1903\\Desktop\\shadiao\\yschange\\play\\PCGameSDK.dll', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='change',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True , uac_admin=True, icon='..\\favicon.ico')
