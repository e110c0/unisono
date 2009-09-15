# -*- coding: utf-8 -*-
# haage@net.in.tum.de

from distutils.core import setup, Extension
setup(name="pyiw", version="0.4.0",
      ext_modules=[Extension("pyiw", ["pyiw.c"])])
