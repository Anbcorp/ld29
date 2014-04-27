from distutils.core import setup
from glob import glob
import py2exe
import sys
import os

origIsSystemDLL = py2exe.build_exe.isSystemDLL
def isSystemDLL(pathname):
        if os.path.basename(pathname).lower() in ( 'libogg-0.dll' , 'sdl_ttf.dll'):
                return 0
        return origIsSystemDLL(pathname)
py2exe.build_exe.isSystemDLL = isSystemDLL

setup(  name='Yaadig',
        version='0.1',
        description='LD29 compo entry',
        author='Benoit \'Anb\' Depail',
        author_email='benoit@anbcorp.net',
        url='http://github.com/Anbcorp/ld29',
        data_files = [  ('res', glob('res/*.*')) , ('.', ['resources.yaml']) ],
        windows=['game.py'],
        options={
            'py2exe': {
                'includes':[ 'yaml', 'numpy', 'pygame']
            }
        }
    )
