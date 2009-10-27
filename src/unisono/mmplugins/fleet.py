'''
fleet.py

 Created on: Apr 23, 2009
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
from unisono.mmplugins import mmtemplates
from unisono.utils import configuration
from unisono.mission_control import Message, Msg_Fleet
from unisono.event import Event
from ctypes import *
from os import path, getcwd
import sys
import socket

class Fleet(mmtemplates.MMServiceTemplate):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    def __init__(self, *args):
        super().__init__(*args)
        self.dataitems = [] # TODO maybe remove that
        self.cost = 100

        lib_path = path.join(getcwd()+'/c-modules/libMeasure')
        self.logger.debug(path.join(lib_path,'libMeasure.so'))
        cdll.LoadLibrary(path.join(lib_path,'libMeasure.so'))
        self.libmeasure = CDLL(path.join(lib_path,'libMeasure.so'))

    def run(self):
        self.logger.info('running')
        while (True):
            # wait for event
            self.logger.info(self.__class__.__name__+' waiting for an message')
            self.request = self.get_message()
            if self.request != None:
                if (self.checkrequest(self.request)):
                    # do the measurement
                    self.logger.info('got request %s',self.request.msgtype)
                    # read values
                    self.logger.info(self.__class__.__name__+' got an message')
                    self.logger.info('request is valid, starting message handling')
                    self.on_message()
                    #self.request['time'] = time()
                else:
                    pass
            else:
                pass
            self.logger.info('run again')

    def checkrequest(self, request):
        return True

    def on_message(self):
        self.logger.info('execute on_message')
        #config = configuration.get_configparser()
        #options = config.options('Fleet')
        #self.logger.debug('Fleet options: %s', options)
        try:
            # 1) check the request
            if self.request.sender.ip == self.request.payload.target.ip:
                self.logger.debug("target is valid")
            else:
                self.logger.debug("target invalid")
            sender = self.request.receiver
            receiver = self.request.sender
            msgtype = "ACK_FLEET"
            train_count = self.request.payload.train_count
            train_length = self.request.payload.train_length
            packet_size = self.request.payload.packet_size
            target = self.request.payload.target

            # 2) start the fleet
            sock_udp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            sock_udp.bind(("",0))
            sock_udp.connect((target.ip,43212))
            self.logger.info("sending fleet...")
            result = self.libmeasure.send_fleet(train_count,train_length,packet_size,sock_udp.fileno(),0)
            self.logger.info("fleet error-code: %d",result)
            # 3) send ctrl-message
            payload = Msg_Fleet(train_count,train_length,packet_size,target)
            outmsg = Message(sender,receiver,msgtype,payload)
            # queues response in dispatcher queue
            ev = Event("MESSAGE_OUT",outmsg)
            self.outq.put(ev)
            self.logger.info('event queued')
        except:
            self.logger.debug("exception in on_message")
        self.logger.debug('the values are: %s', self.request)
