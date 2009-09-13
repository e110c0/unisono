'''
max_bw.py

 Created on: Aug 26, 2009
 Authors: rb
 
 $LastChangedBy: zxmzr67 $
 $LastChangedDate: 2009-08-12 12:12:13 +0200 (Mi, 12. Aug 2009) $
 $Revision: 1679 $
 
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
from os import path, getcwd
import socket
from queue import Empty
from ctypes import *
import time
import threading

from unisono.mmplugins import mmtemplates
from unisono.utils import configuration
from unisono.mission_control import Message, Node
from unisono.event import Event

class timeval(Structure):
  _fields_ = [("tv_sec", c_ulong), ("tv_usec", c_ulong)]

class MsgTrainPayload():
    def __init__(self, trainlength, trainid, packetsize, udpsocket, spacing, target):
        self.trainlength = trainlength
        self.trainid = trainid
        self.packetsize = packetsize
        self.udpsocket = udpsocket
        self.spacing = spacing
        self.target = target

    def equals(self, f):
        if self.count == f.count and self.size == f.size and self.target.equals(f.target):
            return True
        else:
            return False

class ADR(mmtemplates.MMMCTemplate):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    def __init__(self, *args):
        self.__name__ = "ADR"
        super().__init__(*args)
        self.dataitems = ['ADR']
        self.cost = 10000
        self.trainlength = 50
        self.libmeasure = CDLL(path.join(path.dirname(__file__), 'libMeasure.so'))

    def checkmeasurement(self, request):
        return True

    def checkmessage(self, request):
        return True

    def checkrequest(self, request):
        return True

    def measure(self):
        # request from sender: max packet size, min sender delay
        # send max packet size
        # get adr
        # calculate result
        result = self.measureADR()
        if result != None:
            self.request["ADR"] = result
            self.request['error'] = 0
            self.request['errortext'] = 'Measurement successful'
        else:
            self.request['error'] = 312
            self.request['errortext'] = 'error receiving a packet train'
        self.logger.debug('the values are: %s', self.request)

    def receiveTrain(self, exp_train_id, trainlength):
        # start listener
        size = 1024
        udp_port = 43212
        sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_udp.bind(("", udp_port))

        TimeStamps = timeval * trainlength
        ts = TimeStamps()
        result = c_int()
        r_thread = threading.Thread(target=self.libmeasure.recv_train, args=(trainlength, exp_train_id, size, sock_udp.fileno(), ts, byref(result)))
        # Exit the server thread when the main thread terminates
        r_thread.setDaemon(True)
        r_thread.start()

        # send train request
        client_ip = self.request['identifier1']
        client_id = self.__name__
        server_ip = self.request['identifier2']
        server_id = "PacketSender"
        client = Node(client_ip, client_id)
        server = Node(server_ip, server_id)
        payload = MsgTrainPayload(self.trainlength, 0, size, udp_port, 0, client_ip)
        outmsg = Message(client, server, "TRAIN", payload)
        self.outq.put(Event("MESSAGE_OUT", outmsg))
        # wait for ack
        message = self.msgq.get()
        if message.msgtype != "TRAIN_ACK":
            # clean up and stop measurement with error
            self.logger.debug("got the wrong message: %s", message.msgtype)
            pass
        # wait for ackfin
        self.logger.debug("got a message: %s", message.msgtype)
        message = self.msgq.get()
        if message.msgtype != "TRAIN_ACK_FINISHED":
            # clean up and stop measurement with error
            self.logger.debug("got the wrong message: %s", message.msgtype)
            pass
        else:
            # stop receiver thread
            r_thread.join(1.0)
            self.logger.debug("return code : %i", result.value)
            # get results
            self.logger.debug("got a message: %s", message.msgtype)
        return (result.value, ts)
    
    def measureADR(self):
        maxtrain = 5
        maxtrainlength = 50
        retry = 0
        badtrain = True
        trainlength = 0
        exptrainid = 0
        bw = 0.0
        while retry < maxtrain and badtrain:
            if trainlength == 5:
                trainlength = 3
            else:
                trainlength = maxtrainlength - retry * 15
            result = self.receiveTrain(exptrainid, trainlength);
            # Compute dispersion and bandwidth measurement
            if result[0] == 0:
                #check_intr_coalescence
                ts = []
                self.logger.debug(result[1])
                for i in result[1]:
                    if i.tv_sec > 0:
                        ts.append(i.tv_sec * 1000000 + i.tv_usec)
                count = len(ts)
                delta = ts[count -1 ] - ts[0]
                bw = 1000000 * (28 + 1024) * 8 * count /delta
                break;
            else:
                #request a new train.
                retry = retry + 1
                pass
        return bw

class PacketSender(mmtemplates.MMServiceTemplate):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    def __init__(self, *args):
        self.__name__ = "PacketSender"
        super().__init__(*args)
        self.cost = 100
        self.libmeasure = CDLL(path.join(path.dirname(__file__), 'libMeasure.so'))

    def run(self):
        self.logger.info('running')
        while (True):
            # wait for event
            self.logger.info(' waiting for an message')
            message = self.msgq.get()
            self.logger.debug('got request %s', message.msgtype)
            # read values
            self.logger.debug(' got an message')
            if (message.msgtype == "TRAIN"):
                self.sendTrain(message)
            else:
                # stop here and send back error
                pass
            self.logger.debug('run again')

    def checkrequest(self, request):
        return True

    def sendTrain(self, message):
        error = 0
        if(type(message.payload) == MsgTrainPayload):
            if message.sender.ip != message.payload.target:
                # stop here and send back error
                error = 123
            else:
                # ack train
                ack = (message.payload.trainid)
                ackmsg = Message(message.receiver, message.sender, "TRAIN_ACK", ack)
                ev = Event("MESSAGE_OUT", ackmsg)
                self.outq.put(ev)
                # start sending
                sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock_udp.bind(("", 0))
                sock_udp.connect(("127.0.0.1", message.payload.udpsocket))
                error = self.libmeasure.send_train(message.payload.trainlength,
                                           message.payload.trainid,
                                           message.payload.packetsize,
                                           sock_udp.fileno(),
                                           message.payload.spacing)
        else:
            error = 123
        # ack train finish
        ack = (message.payload.trainid, error)
        ackmsg = Message(message.receiver, message.sender, "TRAIN_ACK_FINISHED", ack)
        ev = Event("MESSAGE_OUT", ackmsg)
        self.outq.put(ev)
            