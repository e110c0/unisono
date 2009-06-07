#!/usr/bin/env python3
# encoding: utf-8
'''
PathMTU_tester.py

 Created on: May 11, 2009
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

'''
This script is only for testing purposes. It is used to test the PathMTU M&M
without UNISONO running.
'''
from ctypes import *
from os import path, getcwd
import sys

class Request(Structure):
        _fields_ = [("identifier1", c_char_p),
                    ("identifier2", c_char_p)]

class Result(Structure):
    _fields_ = [("PATHMTU", c_int),
                ('HOPCOUNT', c_int),
                ("error", c_int),
                ('errortext', c_char_p)]

print(path.join(getcwd(),'libPathMTU.so'))
cdll.LoadLibrary(path.join(getcwd(),'libPathMTU.so'))
libmodule = CDLL(path.join(getcwd(),'libPathMTU.so'))
req = Request()
libmodule.measure.restype = Result
req.identifier1 = c_char_p(sys.argv[1])
req.identifier2 = c_char_p(sys.argv[2])
MTUresult = libmodule.measure(req)
print(MTUresult._fields_)
for i in MTUresult._fields_:
	print(getattr(MTUresult,i[0]))
print(MTUresult)
