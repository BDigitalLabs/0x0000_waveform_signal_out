import PyInstaller.__main__
import sys

separator = ';' if sys.platform.startswith('win') else ':'

PyInstaller.__main__.run([
    './main.py',
    '--onedir',
    '--windowed',
    # '--icon=logo.ico',
    f'--add-data=assets{separator}assets', 
    f'--add-data=main_window.qss{separator}.', 
    '--name=0x0000_waveform_signal_out',
])
