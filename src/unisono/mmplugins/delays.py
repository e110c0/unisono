'''
delays.py

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
                ('error', c_int),
                ('errortext', c_char_p)]

class Delays(mmtemplates.MMcTemplate):
    '''
    Wrapper class for the Delays module
    '''
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    def __init__(self, *args):
        '''
        Constructor
        '''
        super().__init__(*args)
        self.libfile = '/home/dh/svn/dev_spovnet/src/unisono/trunk/src/unisono/mmplugins/libDelays.so'
        self.cost = 10000
        self.cresstruct = DelaysResult()
        self.dataitems = ['HOPCOUNT',
                          'RTT',
                          'RTT_MIN',
                          'RTT_MAX',
                          'RTT_DEVIATION',
                          'RTT_JITTER',
                          'OWD',
                          'OWD_MIN',
                          'OWD_MAX',
                          'OWD_DEVIATION',
                          'OWD_JITTER']

    def checkrequest(self, request):
        return True

    def prepare_request(self, req):
        creqstruct = DelaysRequest()
        if 'identifier1' in req.keys():
            creqstruct.identifier1 = c_char_p(req['identifier1'])
        else:
            creqstruct.identifier1 = ''
        if 'identifier2' in req.keys():
            creqstruct.identifier2 = c_char_p(req['identifier2'])
        else:
            creqstruct.identifier2 = ''
        return creqstruct
