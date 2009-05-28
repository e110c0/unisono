'''
Delays_tester.py

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

'''
This script is only for testing purposes. It is used to test the PathMTU M&M
without UNISONO running.
'''
from ctypes import *
from os import path, getcwd

class DelaysRequest(Structure):
    '''
    Request structure for the Delays module
    '''
    _fields_ = [('identifier1', c_char_p),
                ('identifier2', c_char_p)]

class DelaysResult(Structure):
    '''
    Result structure for the Delays module
    '''
    _fields_ = [('HOPCOUNT', c_int),
                ('RTT', c_int),
                ('RTT_MIN', c_int),
                ('RTT_MAX', c_int),
                ('RTT_DEVIATION', c_int),
                ('RTT_JITTER', c_int),
                ('OWD', c_int),
                ('OWD_MIN', c_int),
                ('OWD_MAX', c_int),
                ('OWD_DEVIATION', c_int),
                ('OWD_JITTER', c_int),
                ('LOSSRATE', c_int),
                ('error', c_int),
                ('errortext', c_char_p)]

print(path.join(getcwd(),'libDelays.so'))
cdll.LoadLibrary(path.join(getcwd(),'libDelays.so'))
libmodule = CDLL(path.join(getcwd(),'libDelays.so'))
req = DelaysRequest()
libmodule.measure.restype = DelaysResult
req.identifier1 = c_char_p("127.0.0.1")
#req.identifier2 = c_char_p("127.0.0.1")
req.identifier2 = c_char_p("192.168.178.24")
#req.identifier2 = c_char_p("134.2.172.174")
#req.identifier2 = c_char_p("216.239.59.104")
result = libmodule.measure(req)
for i in result._fields_:
    print(i[0], getattr(result,i[0]))

