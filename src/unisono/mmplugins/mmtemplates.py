'''
mmtemplates.py

 Created on: Apr 23, 2009
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
from queue import Queue
from unisono.event import Event
from ctypes import *

class MMTemplate:
    '''
    generic template for all M&Ms
    '''
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    def __init__(self, inq, outq):
        '''
        init the M&M and start the thread
        '''
        self.cost = 0
        self.dataitems = []
        self.inq = inq
        self.outq = outq
        self.logger.info("started " + self.__class__.__name__ + "!")

    def run(self):
        while (True):
            # wait for event
            self.logger.debug('waiting for an order')
            self.request = self.inq.get()
            # read values
            self.logger.debug('got an order')
            # check the request
            if self.checkrequest(self.request):
                # do the measurement
                self.logger.debug('request is valid, starting measurement')
                self.measure()
            else:
                # set result to nul and set errorcode
                self.result['errorcode'] = 42
                self.result['errortext'] = 'Order invalid'
            self.logger.debug('The result is: %s', self.request)
            self.outq.put(Event('RESULT', [self.__class__.__name__, self.request]))
            # send event with result

    def measure(self):
        raise NotImplementedError("Your M&M lacks a measure() method!")

    def checkrequest(self, request):
        raise NotImplementedError('Your M&M lacks a check_request() method!')

    def availableDataItems(self):
        return self.dataitems

    def getCost(self):
        return self.cost

class CRequest(Structure):
    '''
    Generic request structure for M&Ms using 2 identifiers
    '''
    _fields_ = [('identifier1', c_char_p),
                ('identifier2', c_char_p)]


class MMcTemplate(MMTemplate):
    '''
    Template for M&Ms written in C. Such a plugin must implement its own measure
    function, which will be called with a module dependent request struct and
    returns a result struct.
    The c binding is fully encapsulated in this class.
    '''
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    def __init__(self, *args):
        super().__init__(*args)
        self.libfile = ''

    def load_library(self):
        ''' load the so file
        '''
        cdll.LoadLibrary(self.libfile)
        self.libmodule = CDLL(self.libfile)

    def measure(self):
        # create struct for request
        creqstruct = self.prepare_request(self.request)
        # call c measurement function
        self.libmodule.measure.restype = self.cresstruct.__class__
        self.cresstruct = self.libmodule.measure(creqstruct)
        # put result into self.request
        for i in self.cresstruct._fields_:
            self.request[i[0]] = getattr(self.cresstruct,i[0])
        pass

    def prepare_request(self, request):
        '''
        Generic implementation of the prepare_request() method. Only useful if 
        the M&M requires 2 identifiers. If it requires something else, the 
        wrapper class must implement its own.
        '''
        creqstruct = CRequest()
        if 'identifier1' in request.keys():
            creqstruct.identifier1 = c_char_p(request['identifier1'])
        else:
            creqstruct.identifier1 = ''
        if 'identifier2' in request.keys():
            creqstruct.identifier2 = c_char_p(request['identifier2'])
        else:
            creqstruct.identifier2 = ''
        return creqstruct
