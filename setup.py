from cx_Freeze import setup, Executable
import sys

main_script = 'main.py'
icon_path = 'icon.ico'
includefiles = ['icon.ico']

build_exe_options = {
    'packages': [], 
    'excludes': [],
    'include_files': includefiles,
}

executable = Executable(
    script=main_script,
    base='Win32GUI' if sys.platform == 'win32' else None,
    target_name='FocalAnalysis.exe',
    icon=icon_path
)

setup(
    name='FocalAnalysis',
    version='1.0',
    description='Utility for analyzing focal length and lens usage',
    options={'build_exe': build_exe_options},
    executables=[executable]
)