from cx_Freeze import setup, Executable
import sys

main_script = 'main.py'
icon_path = 'icon.icns'
target_name = 'FocalAnalysis'
includefiles = ['icon.icns']
base = None
if sys.platform == 'win32':
    icon_path = 'icon.ico'
    includefiles = ['icon.ico']
    target_name = 'FocalAnalysis.exe'
    base = 'Win32GUI'

build_exe_options = {
    'packages': [], 
    'excludes': [],
    'include_files': includefiles,
}

executable = Executable(
    script=main_script,
    base=base,
    target_name=target_name,
    icon=icon_path
)

setup(
    name='FocalAnalysis',
    version='1.0',
    description='Utility for analyzing focal length and lens usage',
    options={'build_exe': build_exe_options},
    executables=[executable]
)