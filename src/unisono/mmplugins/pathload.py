'''
max_bw.py

 Created on: Aug 26, 2009
 Authors: rb
 
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
from unisono.dataitem import DataItem

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
    logger.setLevel(logging.INFO)

    def __init__(self, *args):
        self.__name__ = "ADR"
        super().__init__(*args)
        self.dataitems = [DataItem('ADR',2,120,240)]
        self.cost = 10000
        self.trainlength = 50
        # get max packet size
        self.rmaxpacketsize = 1
        self.size = 1024
        self.udp_port = 43212
        self.libmeasure = CDLL(path.join(path.dirname(__file__), 'libMeasure.so'))

    def checkmeasurement(self, request):
        return True

    def checkmessage(self, request):
        return True

    def checkrequest(self, request):
        return True

    def measure(self):
        # setup udp port

        self.sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_udp.bind(("", self.udp_port))
        self.logger.debug("got my socket")
        # setup MC structures
        client_ip = self.request['identifier1']
        client_id = self.__name__
        server_ip = self.request['identifier2']
        server_id = "PacketSender"
        self.client = Node(client_ip, client_id)
        self.server = Node(server_ip, server_id)
        # request from sender: max packet size, min sender delay
        outmsg = Message(self.client, self.server, "GET_SEND_LATENCY", None)
        self.outq.put(Event("MESSAGE_OUT", outmsg))
        outmsg = Message(self.client, self.server, "GET_MAX_PACKETSIZE", None)
        self.outq.put(Event("MESSAGE_OUT", outmsg))
        # get receive delay
        rlat = self.libmeasure.recv_latency(self.sock_udp.fileno(), self.udp_port)
        i = 0
        slat = None
        smaxpacketsize = None
        while i < 60:
            i = i+1
            try:
                message = self.msgq.get(1)
            except Empty:
                if i == 60:
                    #TODO set correct error code
                    self.endMeasurement(13)
                    return
            if message.msgtype == "SEND_LATENCY":
                slat = message.payload
                self.logger.debug("Sender latency: %i", slat)
            elif message.msgtype == "MAX_PACKETSIZE":
                smaxpacketsize = message.payload
                self.logger.debug("Sender maxpacket: %i", smaxpacketsize)
            elif message.msgtype.startswith("ERR_"):
                self.logger.debug("There is no receiver available on the other side: %s", message.msgtype)
                self.endMeasurement(13) # TODO error code!!
                return
            else:
                self.logger.debug("unknown message: %s.",message.msgtype) 
                pass
            if slat != None and smaxpacketsize != None:
                break
        if slat == None or smaxpacketsize == None:
            self.endMeasurement(13) # TODO error code!!
            return
        # get adr
        self.logger.debug("starting ADR measurement...")
        result = self.measureADR()
        self.logger.debug("starting ADR measurement... done!")
        # calculate result
        if result not in (None,0.0):
            self.request["ADR"] = result
            self.request['error'] = 0
            self.request['errortext'] = 'Measurement successful'
        else:
            self.request['error'] = 312
            self.request['errortext'] = 'error receiving a packet train'
        self.logger.debug('the values are: %s', self.request)

    def receiveTrain(self, exp_train_id, trainlength, size):
        TimeStamps = timeval * trainlength
        ts = TimeStamps()
        result = c_int()
        r_thread = threading.Thread(target=self.libmeasure.recv_train, args=(trainlength, exp_train_id, size, self.sock_udp.fileno(), ts, byref(result)))
        # Exit the server thread when the main thread terminates
        r_thread.setDaemon(True)
        r_thread.start()

        # send train request
        payload = MsgTrainPayload(self.trainlength, 0, size, self.udp_port, 0, self.client.ip)
        outmsg = Message(self.client, self.server, "TRAIN", payload)
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

            result = self.receiveTrain(exptrainid, trainlength, self.size);
            # Compute dispersion and bandwidth measurement
            if result[0] == 0:
                #check_intr_coalescence
                ts = []
                self.logger.debug(result[1])
                for i in result[1]:
                    if i.tv_sec > 0:
                        ts.append(i.tv_sec * 1000000 + i.tv_usec)
                count = len(ts)
                if count > 0:
                    delta = ts[count - 1 ] - ts[0]
                    bw = int(1000000 * (28 + 1024) * 8 * count / delta)
                    break;
                else:
                    self.logger.debug("did not receive any data, let's try again!")
                    retry = retry + 1
            else:
                #request a new train.
                self.logger.debug("received a bad train, let's try again!")
                retry = retry + 1
                pass
        return bw
    
    def endMeasurement(self, error):
        self.request["error"] = error
        self.request["errortext"] = ""

class PacketSender(mmtemplates.MMServiceTemplate):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    def __init__(self, *args):
        self.__name__ = "PacketSender"
        super().__init__(*args)
        self.cost = 100
        self.libmeasure = CDLL(path.join(path.dirname(__file__), 'libMeasure.so'))
        self.send_latency = self.libmeasure.send_latency()
        self.maxpacketsize = 1400
        
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
            elif (message.msgtype == "GET_SEND_LATENCY"):
                self.outq.put(
                    Event("MESSAGE_OUT", 
                          Message(message.receiver, 
                                  message.sender, 
                                  "SEND_LATENCY", 
                                  self.send_latency)))
            elif (message.msgtype == "GET_MAX_PACKETSIZE"):
                self.outq.put(
                    Event("MESSAGE_OUT", 
                           Message(message.receiver, 
                                   message.sender, 
                                   "MAX_PACKETSIZE", 
                                   self.maxpacketsize)))
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
                sock_udp.connect((message.payload.target, message.payload.udpsocket))
                error = self.libmeasure.send_train(message.payload.trainlength,
                                           message.payload.trainid,
                                           message.payload.packetsize,
                                           sock_udp.fileno(),
                                           message.payload.spacing)
                sock_udp.close()
        else:
            error = 123
        # ack train finish
        ack = (message.payload.trainid, error)
        ackmsg = Message(message.receiver, message.sender, "TRAIN_ACK_FINISHED", ack)
        ev = Event("MESSAGE_OUT", ackmsg)
        self.outq.put(ev)
            
