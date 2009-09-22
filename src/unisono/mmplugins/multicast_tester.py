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
import socket
import threading
from uuid import uuid1

from unisono.mmplugins import mmtemplates
from unisono.utils import configuration

class MulticastTester(mmtemplates.MMTemplate):
    '''
    M&M to find other nodes reachable via IP Multicast. This Plugin requires a 
    MulticastEchoReplier to run at the correspondent nodes.
    
    In order to receive all replies, this Module will provide also the Multicast
    Echo ReplyHandler in a second thread.
    '''
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    def __init__(self, *args):
        '''
        Constructor
        '''
        super().__init__(*args)
        self.dataitems = ['IP_MULTICAST_CONN']
        self.cost = 5000
        self.wait = 5 # waiting time in seconds
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
        self.socket = socket.socket(type = socket.SOCK_DGRAM)
        self.socket.bind(("",self.mcport))
        #self.socket.connect((self.mcip,self.mcport))
        
    def run(self, *args):
        # start receiver thread
        self.recv_thread = threading.Thread(target=self.receive)
        # Exit the server thread when the main thread terminates
        self.recv_thread.setDaemon(True)
        self.recv_thread.setName(self.__class__.__name__ + "EchoReplier")
        self.recv_thread.start()
        # call default run loop of super
        super().run(*args)
        
    def checkrequest(self, request):
        return True

    def measure(self):
        i = 0
        repliers = []
        while i < self.retries:
            # send a packet
            self.sendEchoRequest()
            # wait for replies
            sleep(self.wait)
            if received > 0:
                break
            else:
                i = i + 1
        for r in repliers:
            # prepare a result
            # send it to the dispatcher
            pass

    def sendEchoRequest(self):
        # generate id
        id = uuid1()
        # prepare packet
        # send packet
        pass

    def sendEchoReply(self, echoId):
        # prepare packet
        # send packet
        pass
    
    def receive(self):
        '''
            
        '''
        # if not sender == receiver
            # if request: send reply
            # for all: prepare result
        pass
    
#class MulticastEchoReplier(mmtemplates.MMServiceTemplate):
#    '''
#    Service M&M for the MulticastTester. It replies to UNISONO Multicast Echo
#    Requests with an UNISONO Multicast Echo Reply and returns all results (i.e.
#    collected packets with its sender) to the Dispatcher.
#    '''
#    logger = logging.getLogger(__name__)
#    logger.setLevel(logging.INFO)
#    def __init__(self, *args):
#        '''
#        Constructor
#        '''
#        super().__init__(*args)
#        config = configuration.get_configparser()
#        try:
#            self.mcip = config.get('Multicast Tester', 'groupip')
#        except:
#            pass
#        try:
#            self.mcport = config.getint('Multicast Tester', 'groupport')
#        except:
#            pass
#        try:
#            self.retries = config.getint('Multicast Tester', 'maxretries')
#        except:
#            pass
