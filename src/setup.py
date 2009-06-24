#!/usr/bin/env python3
'''
setup.py

 Created on: May 25, 2009
 Authors: dh

 $LastChangedBy$
 $LastChangedDate$
 $Revision$

 (C) 2008-2009 by Computer Networks and Internet, University of Tuebingen

 This file is part of UNISONO Unified Information Service for Overlay
 Network Optimization.

 UNISONO is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 2 of the License, or
 (at your option) any later version.

 UNISONO is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with UNISONO.  If not, see <http://www.gnu.org/licenses/>.

'''
from distutils.core import setup, Extension

setup(name='UNISONO',
      version='0.1',
      description='Unified Information Service for Overlay Network Organization',
      author='Computer Networks and Internet, University of Tuebingen',
      author_email='spovnet@ri.uni-tuebingen.de',
      url='http://projects.net.in.tum.de/projects/unisono/',
      packages=['unisono', 'unisono.mmplugins', 'unisono.utils'],
      scripts=['unisono-startup'],
      ext_modules=[Extension('unisono.mmplugins.libPathMTU',
                             ['c-modules/PathMTU/networkfunctions.c',
                              'c-modules/PathMTU/PathMTU.c',
                              ]),
                   Extension('unisono.mmplugins.libDelays',
                             ['c-modules/Delays/mathfunctions.c',
                              'c-modules/Delays/networkfunctions.c',
                              'c-modules/Delays/Delays.c',
                              ],
                              extra_compile_args=['-std=gnu99'])
                   ],
      data_files=[('/etc/unisono',['../etc/unisono.cfg'])]
     )
