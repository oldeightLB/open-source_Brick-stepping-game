import PyInstaller.__main__

PyInstaller.__main__.run([
    '我的游戏.py',
    '--add-data=images;images',
    '--add-data=maps;maps',
    '--add-data=sounds;sounds',
    '-n=踩砖块',
    '-w',
    '-i=images/player.ico',
    '-y'
])
