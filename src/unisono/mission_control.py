'''
mission_control.py

 Created on: May 19, 2009
 Authors: dh, rb(zxmzr67)
 
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
import pickle
import queue
import socket
import sys
import time
from socketserver import TCPServer, StreamRequestHandler
from threading import Lock
from threading import Thread
from unisono.utils import configuration
from unisono.event import Event

class Node():
    def __init__(self,t_ip,t_id):
        self.ip=t_ip
        self.port=-1
        self.id=t_id

    def equals(self,t):
        if self.ip == t.ip and self.port == t.port:
            return True
        else:
            return False

class Msg_Fleet():
    def __init__(self, n, m, k, node=None):
        self.target = node
        self.train_count = n
        self.train_length = m
        self.packet_size = k

    def equals(self,f):
        if self.train_count == f.train_count and self.train_length == f.train_length and self.packet_size == f.packet_size and self.target.equals(f.target):
            return True
        else:
            return False

class Message():

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    def __init__(self,sender,receiver,msgtype,payload):
        '''
        to service modules
        - SEND_FLEET: send n packets with size bytes to destination:port over udp

        to mm_mc_module
        - ACK_SEND_FLEET

        [orders
        - MAX_BW: send a fleet
        - USED_BW: get current bw used by target
        ]
        '''
        self.msgtype=msgtype # which cmd shall be executed
        self.sender = sender
        self.receiver = receiver
        self.payload = payload
        self.dataitems = ['MC_REQUEST']
        self.tomsgqueue = 1

class MissionControlRequestHandler(StreamRequestHandler):

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    def handle(self):
        try:
            print("... handling ...")
            data_in = self.request.recv(1024)
            data = pickle.loads(data_in)

            if not data:
                msgtype = "ERR_"+data.msgtype
                outmsg = Message(data.receiver,data.sender,msgtype,data)
                data_out = pickle.dumps(outmsg)
                self.request.send(data_out)

            elif type(data) != Message:
                self.logger.debug("wrong data type")
                msgtype = "ERR_"+data.msgtype
                outmsg = Message(data.receiver,data.sender,msgtype,data)
                data_out = pickle.dumps(outmsg)
                self.request.send(data_out)

            else:
                receiverID = data.receiver.id
                # check if receiver is registered

                if self.server.isRegistered(receiverID):
                    # send event to dispatcher
                    eventmsg = Message(data.sender,data.receiver,data.msgtype,data.payload)
                    ev = Event("MESSAGE",eventmsg)
                    self.server.putEvent(ev)
                    # send ack to mission control
                    msgtype = "200 OK"
                    payload = ""
                    responsemsg = Message(data.sender,data.receiver,msgtype,payload)
                    self.request.send(pickle.dumps(responsemsg))

                else:
                    # create err_respone to requesting remote module
                    self.logger.debug("receiver not available")
                    msgtype = "ERR_"+data.msgtype
                    outmsg = Message(data.receiver,data.sender,msgtype,data)
                    data_out = pickle.dumps(outmsg)
                    self.request.send(data_out)
        except socket.error:
            self.logger.debug("socket error during handling")

class MissionControl(TCPServer):

    '''
    MissionControl provides a global coordinator for modules that need to
    communicate with a correspondent measurement node to coordinate a measurement.
    '''

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    __modules_dict__ = {}

    def __init__(self, outq):
        '''
        Constructor
        '''
        self.config = configuration.get_configparser()
        self.__port = self.config.getint('MissionControl', 'port');

        host = ""
        super().__init__((host,self.__port),MissionControlRequestHandler,False)
        self.allow_reuse_address = True
        self.server_bind()
        self.server_activate()
        self.__send_queue = queue.Queue() # outqueue filled by the dispatcher
        self.__receive_queue = outq # eventqueue of the dispatcher
        self.lock = Lock()
        self.do_quit = False
        self.trigger_wait_time = 3 # time the trigger threads wait, after rescanning a queue
        t_triggerSendQueue = Thread(target = self.triggerSendQueue, args = ())
        t_triggerSendQueue.daemon = True
        t_triggerSendQueue.start()
        t_Recv = Thread(target = self.receive, args = ())
        t_Recv.daemon = True
        t_Recv.start()

    def isRegistered(self, mod):
        if mod in self.__modules_dict__:
            return True
        else:
            return False

    def putEvent(self, ev):
        self.__receive_queue.put(ev)

    def stop(self):
        self.do_quit = True

    def register(self, sender):
        self.logger.debug("MissionControl: register "+sender)
        #with self.lock:
        if sender not in self.__modules_dict__:
            self.__modules_dict__.setdefault(sender) # this may have a value ?!
        else:
            self.logger.debug(sender + " is already registered")
        #self.logger.debug ("done reg")

    def put(self, message):
        #self.logger.debug ("put",sender,receiver,message)
        #with self.lock:
        if type(message) != Message:
            self.logger.debug('put(): wrong data type')
            return -1
        # check if sender is registered
        if message.sender.id in self.__modules_dict__:
            self.logger.info('queue outmsg')
            self.__send_queue.put(message)
        else:
            self.logger.info('sender %s not known',message.sender.id)
            # create local error message
            msgtype = "ERR_"+message.msgtype
            err_msg = Message(message.receiver,message.sender,msgtype,message)
            ev = Event("MESSAGE",err_msg)
            self.__receive_queue.put(ev)

    def get(self, receiverID):
        #self.logger.debug ("get an item for",receiver)
        #with self.lock:
        # check if sender is registered
        if receiverID in self.__modules_dict__:
            # queue (sender, receiver, message)
            cqueue = self.__modules_dict__.get(receiverID)
            #self.logger.debug ("getting a mailbox item ...",receiver)
            try:
                c_item = cqueue.get_nowait()
                senderID = c_item[0]
                message = c_item[1]
                fromIP = c_item[2]
                fromPort = c_item[3]
                #self.logger.debug ("getting (sender,message):",c_item)
                #self.logger.debug ("done get")
                return  (senderID, message,fromIP,fromPort)
            except queue.Empty:
                self.logger.debug ("no message available for",receiverID)
                return ("","","","")

    def triggerSendQueue(self):
        while True:
            if self.do_quit:
                break
            #self.logger.debug("triggerSendQueue")
            #with self.lock:
            # check if new message should be sent
            try:
                message = self.__send_queue.get_nowait()
                self.send(message.sender.id, message.receiver.id, message.receiver.ip, message.receiver.port, message)
            except queue.Empty:
                time.sleep(self.trigger_wait_time)
            #self.logger.debug ("done tsq")

    def triggerReceiveQueue(self):
        while True:
            if self.do_quit:
                break
            #self.logger.debug("triggerReceiveQueue")
            # check if new message arrived
            try:
                pass
                #event = self.__receive_queue.get_nowait()
                #self.logger.debug("trq: handling",current)
                # push message to modules mailbox
                '''
                senderID = current[0]
                receiverID = current[1]
                fromIP = current[2]
                fromPort = current[3]
                message = current[4]
                with self.lock:
                    if receiverID in self.__modules_dict__:
                        cqueue = self.__modules_dict__.pop(receiverID)
                        #self.logger.debug ("storing into mailbox",receiver,cqueue)
                        cqueue.put((senderID,message,fromIP,fromPort))
                        self.__modules_dict__.setdefault(receiverID, cqueue)
                    #self.logger.debug ("stored",receiver,cqueue,"into mailbox of",receiver)
                    else: # reply with an error message
                        self.logger.debug ("(EE)",receiver,"has no mailbox")
                '''
                #self.outq.put(event)
            except queue.Empty:
                time.sleep(self.trigger_wait_time)
            #self.logger.debug ("done trq")

    def send(self, senderID, receiverID, destIP, destPort, message):
        '''
        send() tries several different methods to deliver a message to the receiver:
        * try a connection via a connector. hopefully, the connector correspondent 
        to the current request allows this.
        * try connecting directly. This requires the correspondent node to be
         * reachable (no firewall, no NATs inbetween)
         * listening on the UNISONO mission control port
        * the UNISONO DHT (yet to be implemented)
        '''

        # open a socket connection to receiver
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if destPort == -1:
            destPort = self.__port

        try:
            '''
            the sender and receiver should also be sent!
            maybe add identifiers for the modules and the mission control
            '''
            #s_out = '' + sender + reveicer + message
            #print ("sending:",s_out)
            s.connect((destIP, destPort))
            print("(send) sending data")
            s.send(pickle.dumps(message))
            #s.send(message)
            # TODO error handling
            print("(send) try to read data")
            data_in = s.recv(1024)
            data = pickle.loads(data_in)
            # check if response contains an error
            if(data.msgtype=="200 OK"):
                # everything is fine
                pass
            elif "ERR_" in data.msgtype:
                ev = Event("MESSAGE",data)
                self.__receive_queue.put(ev)
            else:
                # there is a problem: queue msg with an error
                data.msgtype = "ERR_"+data.msgtype
                # create a local event
                ev = Event("MESSAGE",data)
                self.__receive_queue.put(ev)
        except socket.error:
              # error-cases:
              # network unreachable
              # connection refused
              # connection timed out
              self.logger.info("send(): error with socket")
        finally:
            s.close()
        # wait for an response and close connection after an timeout

    def receive(self):
        '''
        #new code
        '''
        try:
            print("server.serve_forever ...")
            self.serve_forever()
        finally:
            #TODO: won't be called
            self.shutdown()
        '''
        #old code
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("", self.__port)) 
            s.listen(1)
        except socket.error:
            self.logger.debug("Socket Error - stopping server")
            self.stop()
            return
#        s.setsockopt(1, socket.SO_CLOEXEC1, 1)
        try: 
            while True:
                print ("accepting a new connection ...")
                try:
                    komm, addr = s.accept()
                except KeyboardInterrupt:
                    print ("KeyboardInterrupt - stopping server")
                    self.stop()
                    break
                print (addr, "connected")
#                while True:
                data = pickle.loads(komm.recv(1024))
                if not data:
                    komm.close()
                    continue
                receiverID = data.receiver.id
                # check if receiver is registered
                if receiverID in self.__modules_dict__:
                    # send event to dispatcher
                    eventmsg = Message(data.sender,data.receiver,data.msgtype,data.payload)
                    ev = Event("MESSAGE",eventmsg)
                    self.__receive_queue.put(ev)
                    # send ack to mission control
                    msgtype = "200 OK"
                    payload = ""
                    responsemsg = Message(data.sender,data.receiver,msgtype,payload)
                    komm.send(pickle.dumps(responsemsg))
                else:
                    # create err_respone to requesting remote module
                    self.logger.debug("receiver not available")
                    msgtype = "ERR_"+data.msgtype
                    outmsg = Message(data.receiver,data.sender,msgtype,data)
                    komm.send(pickle.dumps(outmsg))
                komm.close()
        finally:
            s.close()
        '''
