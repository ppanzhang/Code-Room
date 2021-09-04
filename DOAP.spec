# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['tools\\DOAP\\DOAP', 'PC', 'Tools\\LMT_tool.ico', 'DOAP_tools.py'],
             pathex=['C:\\Users\\CNPAZHA6\\Projects\\LMT_HART\\Tools\\AM4 tools\\DOAP\\DOAP PC Tools'],
             binaries=[],
             datas=[],
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
          name='DOAP',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='C:\\Users\\CNPAZHA6\\Projects\\LMT_HART\\Tools\\AM4')
