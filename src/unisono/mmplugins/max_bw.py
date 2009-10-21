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
from unisono.mmplugins import mmtemplates
from unisono.utils import configuration
from unisono.mission_control import Message, Msg_Fleet, Node
from unisono.event import Event
from queue import Empty
import time
from ctypes import *
from os import path, getcwd
import sys
import socket
from threading import Thread

class timeval(Structure):
  _fields_ = [("tv_sec", c_ulong),("tv_usec", c_ulong)]


class maxBandwidth(mmtemplates.MMMCTemplate):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    def __init__(self, *args):
        self.__name__ = "maxBandwidth"
        super().__init__(*args)
        self.dataitems = ['MAX_BANDWIDTH']
        self.cost = 100

        lib_path = path.join(getcwd()+'/c-modules/libMeasure')
        self.logger.debug(path.join(lib_path,'libMeasure.so'))
        cdll.LoadLibrary(path.join(lib_path,'libMeasure.so'))
        self.libmeasure = CDLL(path.join(lib_path,'libMeasure.so'))

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

                # steps inspired by pathrate

                # 1) get rtt / latency
                # 2) maximum train length?
                # 3.1) request fleet
                # 3.1.1) create request message
                snd_ip = self.request['identifier1']
                snd_id = self.__name__
                rcv_ip = self.request['identifier2']
                rcv_id = "Fleet"
                sender = Node(snd_ip,snd_id)
                receiver = Node(rcv_ip,rcv_id)
                msgtype = "FLEET"
                #93303,7 kbits/sec
                #48213,3 kbits/sec
                train_count = 10 # number ob trains sent
                train_length = 50 # packet count
                packet_size = 1460
                fl_rcv = sender
                payload = Msg_Fleet(train_count,train_length,packet_size,fl_rcv)
                outmsg = Message(sender,receiver,msgtype,payload)
                ev = Event("MESSAGE_OUT",outmsg)
                # 3.1.2) schedule request
                self.outq.put(ev)
                # 3.2) receive fleet
                # 3.2.1) needed vars / params

                sock_udp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                sock_udp.bind(("",43212))
                TimeStamps = timeval * train_length
                ts= TimeStamps()
                ts2= TimeStamps()
                ATimeStamps = TimeStamps * train_count
                tts = ATimeStamps()
                # 3.2.2) receive fleet
                
                t_Recv_Fleet = Thread(target = self.libmeasure.recv_fleet, args = (train_count,train_length,packet_size,sock_udp.fileno(),tts))
                t_Recv_Fleet.daemon = True
                t_Recv_Fleet.start()
                
                # 3.2.3) receive control message
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
                        if message.msgtype in ['ACK_FLEET','ERR_FLEET']:
                            # check if message is correct
                            if message.msgtype == "ACK_FLEET":
                                ctrl_success = 1
                                break
                            elif message.msgtype == "ERR_FLEET":
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
                    # no response received
                    # error: timeout on input or wrong input
                    self.logger.info("send fleet failed")
                    raise
                else:
                    # handle ACK_FLEET message
                    self.logger.info("send fleet seems to be successful")
                    if type(message.payload) != Msg_Fleet:
                        self.logger.info("send fleet failed with invalid response")
                        raise
                    if outmsg.payload.equals(message.payload):
                        # it seems to be correct
                        self.logger.info("send fleet should be successful")
                        pass
                    else:
                        self.logger.info("send fleet failed with invalid response")
                        raise

                # 3.3) check results
                
                c_count = 0
                vals = {}
                count_errors = 0
                for j in tts:
                    for i in j:
                        #print(i.tv_sec,i.tv_usec)
                        #print(i.tv_sec * 1000000 + i.tv_usec)
                        vals[c_count] = i.tv_sec * 1000000 + i.tv_usec
                        if i.tv_sec == 0 and i.tv_usec == 0:
                            print("(EE) at ",i)
                            count_errors = count_errors + 1
                        c_count = c_count + 1
                
                max_count = c_count-1
                
                # new computation
                c_count = 0
                err_count = 0
                sum_diffs = 0
                new_other_diff = 0
                vec_diffs = []
                while c_count < train_count:
                    first_val = vals[train_length * c_count]
                    last_val = vals[train_length * (c_count + 1) - 1]
                    other_diff = (last_val - first_val) #/ (train_length - 1)
                    other_diff = (last_val - first_val) / 1000000.0
                    print("other_diff",other_diff,"bw: ",((28+packet_size) << 3) * (train_length - 1) / other_diff / 1000 // 1000)
                    if other_diff < 0:
                        other_diff = 0
                    vec_diffs.append(other_diff)
                    c_count = c_count + 1
                sorted_list = sorted(vec_diffs)
                # compute median

                vec_len = len(sorted_list)
                print(sorted_list)
                if vec_len % 2 == 0:
                    new_other_diff = (sorted_list[int((vec_len / 2) - 1)] + sorted_list[int(vec_len / 2)]) / 2.0
                else:
                    new_other_diff = vec_diffs[int((vec_len + 1) / 2)]
                new_other_bw = ((28+packet_size) << 3) * train_length / new_other_diff
                print("new other_diff", new_other_diff, "bw: ", new_other_bw,"bps")
                #
                '''
                first_val = vals[0]
                last_val = vals[max_count]
                other_diff = (last_val - first_val) / (train_length - 1)
                print("other_diff",other_diff,"usec"," bw: ",((28+packet_size) << 3) * (train_length - 1) / other_diff,"bps")
                print("timestamp errors",count_errors)
                '''
                
                '''
                c_count = 0
                min_diff = -1
                max_diff = -1
                # calculate differences
                diffs = {}
                a = 0
                b = 0
                sum = 0
                while c_count < max_count:
                    a = vals[c_count]
                    b = vals[c_count + 1]
                    diff = b - a
                    diffs[c_count] = diff
                    sum = sum + diff
                    if min_diff == -1:
                        min_diff = diff
                    else:
                        if diff < min_diff:
                            min_diff = diff
                    if max_diff == -1:
                        max_diff = diff
                    else:
                        if diff > max_diff:
                            max_diff = diff
                    c_count = c_count + 1
                # end pathrate-steps
                mean_diff = sum / max_count
                mean_bw = ((28+packet_size) << 3) * max_count / mean_diff
                print(packet_size)
                print("min_diff",min_diff,"usec"," bw: ",((28+packet_size) << 3) * max_count / min_diff,"bps")
                print("max_diff",max_diff,"usec"," bw: ",((28+packet_size) << 3) * max_count / max_diff,"bps")
                print("mean_diff",mean_diff,"usec"," bw: ",((28+packet_size) << 3) * max_count / mean_diff,"bps")
                '''
                
                #self.request[di] = str((mean_bw / 1024) // 1024) + " MBit/s"
                self.request[di] = str((new_other_bw / 1000) // 1000) + " MBit/s"
                self.request['error'] = 0
                self.request['errortext'] = 'Measurement successful'
            except:
                self.request['error'] = 312
                self.request['errortext'] = 'ERR_FLEET'
        self.logger.debug('the values are: %s', self.request)
