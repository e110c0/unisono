'''
avail_bw.py

 Created on: Oct 13, 2009
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
from unisono.mmplugins import mmtemplates
from unisono.utils import configuration
from unisono.mission_control import Message, Msg_Fleet, Node
from unisono.order import InternalOrder, RemoteOrder
from unisono.event import Event
from queue import Empty
import time
from ctypes import *
from os import path, getcwd
import sys
import socket
from threading import Thread

class availBandwidth(mmtemplates.MMMCTemplate):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    def __init__(self, *args):
        self.__name__ = "availBandwidth"
        super().__init__(*args)
        self.dataitems = ['AVAIL_BANDWIDTH']
        self.cost = 100
        '''
        lib_path = path.join(getcwd()+'/c-modules/libMeasure')
        self.logger.debug(path.join(lib_path,'libMeasure.so'))
        cdll.LoadLibrary(path.join(lib_path,'libMeasure.so'))
        self.libmeasure = CDLL(path.join(lib_path,'libMeasure.so'))
        '''

    def checkmeasurement(self, request):
        return True

    def checkmessage(self, request):
        return True

    def checkrequest(self, request):
        return True

    def measure(self):
        #config = configuration.get_configparser()
        #options = config.options('maxBandwidth')
        #self.logger.debug('maxBandwidth options: %s', options)
        for di in self.dataitems:
            #self.logger.info("trying to request a fleet with dataitem %s", self.request['dataitem'])
            try:
                
                # inner-order to use as we need the result ...
                # 'USED_BANDWIDTH_RX' 'USED_BANDWIDTH_TX
                
                '''
                # TODO
                module_id = self.__name__
                req_di = 'MAX_BANDWIDTH'
                #req_di = 'USED_BANDWIDTH_TX'
                #req_di = 'USED_BANDWIDTH_RX'
                order = InternalOrder(module_id, {'dataitem':req_di, 'identifier1':self.request['identifier1'], 'identifier2':self.request['identifier2']}) # TODO: here we should add the remote station
                ev = Event("INTERN_ORDER",order)
                self.outq.put(ev)
                self.logger.info("queued INTERNAL_ORDER")
                
                # listen on message queue
                
                time_waited = 0
                time_max_wait = 120
                time_wait_interval=5
                ctrl_success = 0
                self.logger.info("waiting for a message in msgq")
                while True:
                    try:
                        #self.logger.info("test (1)")
                        # wait non_blocking on message_queue
                        self.logger.debug("try to get a new message")
                        message = self.get_message_nowait()
                        if message == None:
                            self.logger.debug("received wrong datatype")
                            continue
                        self.logger.debug("message-type: %s",message.msgtype)
                        if message.msgtype in ['RESULT','ERROR']:
                            # check if message is correct
                            if message.msgtype == "RESULT":
                                ctrl_success = 1
                                break
                            elif message.msgtype == "ERROR":
                                break;
                        else:
                            # drop message and wait for further messages
                            pass
                    except Empty:
                        self.logger.debug("sleeping for %d",time_wait_interval)
                        time.sleep(time_wait_interval)
                        time_waited += time_wait_interval
                        if time_waited >= time_max_wait:
                            self.logger.debug("(EE) break while: timeout")
                            break
                self.logger.info("quit while")
                
                if ctrl_success == 0:
                    raise
                result = message.result
                '''
                
                req_di = 'MAX_BANDWIDTH'
                max_bw = int(self.run_internal_order(req_di)) # bw between both nodes
                if max_bw == None:
                    raise
                req_di = 'USED_BANDWIDTH_TX'
                tx_bw = int(self.run_remote_order(req_di))
                #tx_bw = 0 # currently used bw by receiver (remote call)
                if tx_bw == None:
                    raise
                
                req_di = 'USED_BANDWIDTH_RX'
                rx_bw = int(self.run_internal_order(req_di))
                #rx_bw = 0 # currently used bw by sender
                if rx_bw == None:
                    raise
                
                print(max_bw,rx_bw,tx_bw)
                
                self.logger.debug(type(max_bw))
                self.logger.debug(type(rx_bw))
                self.logger.debug(type(tx_bw))
                
                result_value = max_bw - max(rx_bw, tx_bw)
                self.logger.debug(type(result_value))
                self.request[di] = int(result_value)
                self.request['error'] = 0
                self.request['errortext'] = 'Measurement successful'
            except Exception as e:
                self.logger.debug(e)
                self.request['error'] = 312
                self.request['errortext'] = 'ERR_AVAIL_BANDWIDTH'
        self.logger.debug('the values are: %s', self.request)

    def run_internal_order(self, req_di):
        try:
            
            # inner-order to use as we need the result ...
            # 'USED_BANDWIDTH_RX' 'USED_BANDWIDTH_TX
            
            # TODO
            module_id = self.__name__
            order = InternalOrder(module_id, {'dataitem':req_di, 'identifier1':self.request['identifier1'], 'identifier2':self.request['identifier2']}) # TODO: here we should add the remote station
            ev = Event("INTERN_ORDER",order)
            self.outq.put(ev)
            self.logger.info("queued INTERNAL_ORDER")
            
            # listen on message queue
            
            time_waited = 0
            time_max_wait = 120
            time_wait_interval=5
            ctrl_success = 0
            self.logger.info("waiting for a message in msgq")
            while True:
                try:
                    #self.logger.info("test (1)")
                    # wait non_blocking on message_queue
                    self.logger.debug("try to get a new message")
                    message = self.get_message_nowait()
                    if message == None:
                        self.logger.debug("received wrong datatype")
                        continue
                    self.logger.debug("message-type: %s",message.msgtype)
                    if message.msgtype in ['RESULT','ERROR']:
                        # check if message is correct
                        if message.msgtype == "RESULT":
                            ctrl_success = 1
                            break
                        elif message.msgtype == "ERROR":
                            break;
                    else:
                        # drop message and wait for further messages
                        pass
                except Empty:
                    self.logger.debug("sleeping for %d",time_wait_interval)
                    time.sleep(time_wait_interval)
                    time_waited += time_wait_interval
                    if time_waited >= time_max_wait:
                        self.logger.debug("(EE) break while: timeout")
                        break
            self.logger.info("quit while")
            if ctrl_success == 0:
                raise
            result = message.result
            return result[req_di]
        except:
            return None

    def run_remote_order(self, req_di):
        try:
            snd_ip = self.request['identifier1']
            snd_id = self.__name__
            rcv_ip = self.request['identifier2']
            rcv_id = req_di
            sender = Node(snd_ip,snd_id)
            receiver = Node(rcv_ip,rcv_id)
            msgtype = "REMOTE_ORDER"
            self.logger.info("test8")
            # the identifiers have to be switched !
            payload = RemoteOrder(sender, receiver, {'dataitem':req_di, 'identifier1':self.request['identifier2'], 'identifier2':self.request['identifier1']})
            self.logger.info("test9")
            outmsg = Message(sender,receiver,msgtype,payload)
            ev = Event("MESSAGE_OUT",outmsg)
            # 3.1.2) schedule request
            self.outq.put(ev)
            
            # listen on message queue
            
            time_waited = 0
            time_max_wait = 120
            time_wait_interval=5
            ctrl_success = 0
            self.logger.info("waiting for a message in msgq")
            while True:
                try:
                    #self.logger.info("test (1)")
                    # wait non_blocking on message_queue
                    self.logger.debug("try to get a new message")
                    message = self.get_message_nowait()
                    if message == None:
                        self.logger.debug("received wrong datatype")
                        continue
                    self.logger.debug("message-type: %s",message.msgtype)
                    if message.msgtype in ['RESULT','ERROR','ERR_REMOTE_ORDER']:
                        # check if message is correct
                        if message.msgtype == "RESULT":
                            ctrl_success = 1
                            break
                        elif message.msgtype == "ERROR":
                            break
                        elif message.msgtype == "ERR_REMOTE_ORDER":
                            self.logger.info("ERR_REMOTE_ORDER")
                            break
                    else:
                        # drop message and wait for further messages
                        pass
                except Empty:
                    self.logger.debug("sleeping for %d",time_wait_interval)
                    time.sleep(time_wait_interval)
                    time_waited += time_wait_interval
                    if time_waited >= time_max_wait:
                        self.logger.debug("(EE) break while: timeout")
                        break
            self.logger.info("quit while")
            if ctrl_success == 0:
                raise
            result = message.payload['result']
            return result
        except Exception as e:
            print(e)
            return None
