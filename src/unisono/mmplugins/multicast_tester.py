'''
multicast_tester.py

 Created on: Sep 18, 2009
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

class MulticastTester(mmtemplates.MMTemplate):
    '''
    M&M to find other nodes reachable via IP Multicast. This Plugin requires a 
    MulticastEchoReplier to run at the correspondent nodes.
    '''
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    def __init__(self, *args):
        '''
        Constructor
        '''
        super().__init__(*args)
        self.dataitems = ['IP_MULTICAST_CONN']
        self.cost = 1000
        config = configuration.get_configparser()
        try:
            self.mcip = config.get('Multicast Tester', 'groupip')
        except:
            pass
        try:
            self.mcport = config.getint('Multicast Tester', 'groupport')
        except:
            pass
        try:
            self.retries = config.getint('Multicast Tester', 'maxretries')
        except:
            pass

    def checkrequest(self, request):
        return True

    def measure(self):
        i = 0
        repliers = []
        while i < self.retries:
            # send a packet
            # wait for replies
            if received > 0:
                break
            else:
                i = i + 1
        for r in repliers:
            # prepare a result
            # send it to the dispatcher
            pass

        
class MulticastEchoReplier(mmtemplates.MMServiceTemplate):
    '''
    Service M&M for the MulticastTester. It replies to UNISONO Multicast Echo
    Requests with an UNISONO Multicast Echo Reply and returns all results (i.e.
    collected packets with its sender) to the Dispatcher.
    '''
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    def __init__(self, *args):
        '''
        Constructor
        '''
        super().__init__(*args)
        config = configuration.get_configparser()
        try:
            self.mcip = config.get('Multicast Tester', 'groupip')
        except:
            pass
        try:
            self.mcport = config.getint('Multicast Tester', 'groupport')
        except:
            pass
        try:
            self.retries = config.getint('Multicast Tester', 'maxretries')
        except:
            pass
        # prepare socket
    
    def run(self):
        while True:
            # listen to socket
                # if received request
                # send reply
            # save result
            pass