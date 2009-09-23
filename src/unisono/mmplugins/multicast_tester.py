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
from time import time

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
        # dict for receiver: ip:timestamp
        self.receiver = {}
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
        any = "0.0.0.0"
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 
                                    socket.IPPROTO_UDP)
        self.socket.bind((any, self.mcport))
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 7)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.IPPROTO_IP,
                               socket.IP_ADD_MEMBERSHIP, 
                               socket.inet_aton(self.mcip) + 
                               socket.inet_aton(any))
        
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

    def prepareResult(self, address, result):
        self.request['IP_MULTICAST_CONN'] = result
        self.request['error'] = 0
        self.request['errortext'] = 'Measurement successful'

    def measure(self):
        i = 0
        id = uuid1()
        while i < self.retries:
            # check for data in receiver dict
            if request['identifier2'] in self.receiver.keys():
                self.prepareResult(request['identifier2'], True)
                return
            # send a packet
            self.sendEchoRequest(id, i)
            i = i + 1
            # wait for replies
            sleep(self.wait)
        # no reply received: prepare negative result
        self.prepareResult(request['identifier2'], False)

    def sendEchoRequest(self, id, count):
        # prepare packet
        payload = id.bytes + bytes(i) + bytes("MULTICAST_ECHO_REQST", "ascii")
        # send packet
        self.socket.sendto(payload, (self.mcip, self.mcport))
        pass

    def sendEchoReply(self, id, count):
        # prepare packet
        payload = id.bytes + bytes(i) + bytes("MULTICAST_ECHO_REPLY", "ascii")
        # send packet
        self.socket.sendto(payload, (self.mcip, self.mcport))
        pass
    
    def receive(self):
        '''
            
        '''
        while True:
            data, addr = self.socket.recvfrom(1500)
            # if not sender == receiver
            # for all: prepare result
            self.receiver[addr] = time()
            # TODO each received packet should be put into the global cache.
            # may require some restructuring in the dispatcher
            #self.prepareResult(addr)
            id = uuid.UUID(bytes = data[:16])
            counter = int(data[16:17])
            msg =  data[17:]
            # if request: send reply
            if msg == "MULTICAST_ECHO_REQST":
                self.sendEchoReply(id, counter)

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
