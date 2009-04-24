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
import threading
import logging
from queue import Queue

class mmtemplate:
    '''
    generic template for all M&Ms
    '''
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    name = ""
    def __init__(self, inq, outq):
        '''
        init the M&M and start the thread
        '''
        self.logger.info("started " + self.__class__.__name__ +"!")
        self.dataitems = []
        self.inq = inq
        self.outq = outq
        mm_thread = threading.Thread(target=self.run)
        # Exit the server thread when the main thread terminates
        mm_thread.setDaemon(True)
        mm_thread.start()
        self.logger.info("M&M %s loop running in thread: %s", self.name, mm_thread.name)
    def run(self):
        while (True):
            # wait for event
            
            # read values
            
            # so the measurement
            result = self.measure()
            # send event with result
            
    def measure(self):
        raise NotImplementedError("Your M&M lacks a measure() method!")
