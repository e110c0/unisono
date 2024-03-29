'''
pathmtu.py

 Created on: May 14, 2009
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
import logging
from unisono.mmplugins import mmtemplates
from ctypes import *
from os import path
from unisono.dataitem import DataItem

class PathMTUResult(Structure):
    '''
    Result structure for the PathMTU module
    '''
    _fields_ = [('PATHMTU', c_int),
                ('HOPCOUNT', c_int),
                ('error', c_int),
                ('errortext', c_char_p)]

class PathMTU(mmtemplates.MMcTemplate):
    '''
    Wrapper class for the PathMTU module
    '''
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    def __init__(self, *args):
        '''
        Constructor
        '''
        super().__init__(*args)
        self.libfile = path.join(path.dirname(__file__), 'libPathMTU.so')
        self.cresstruct = PathMTUResult()
        self.cost = 10000
        self.dataitems = [DataItem('PATHMTU',2,600,1200),
                          DataItem('HOPCOUNT',2,600,1200)]
        self.load_library()

    def checkrequest(self, request):
        return True

