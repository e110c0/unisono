'''
cvalues.py

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
from unisono.mmplugins import mmtemplates
from unisono.utils import configuration

class cValues(mmtemplates.MMTemplate):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    '''
    This class provides user-definde (==configured) values for the applications
    each value will be found in the cvalue section of unisono.cfg
    If a value is not available, the result will be NUL and an error code is
    returned
    '''
    def __init__(self, *args):
        super().__init__(*args)
        self.dataitems = ['SHARED_BANDWIDTH_RX', 'SHARED_BANDWIDTH_TX']
        self.cost = 100

    def checkrequest(self, request):
        return True

    def measure(self):
        config = configuration.get_configparser()
        options = config.options('cValues')
        self.logger.debug('cValues options: %s', options)
        try:
            di = self.request['dataitem']
            self.request[di] = config.get('cValues', di)
            self.logger.debug('the values are: %s', self.request)
            self.request['errorcode'] = 0
            self.request['errortext'] = 'Measurement successful'
        except:
            self.request['errorcode'] = 312
            self.request['errortext'] = 'No value configured'

