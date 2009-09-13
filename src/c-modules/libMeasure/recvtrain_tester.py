#!/usr/bin/env python3
# encoding: utf-8
'''
sendtrain_tester.py

 Created on: May 11, 2009
 Authors: dh
 
 $LastChangedBy: haage $
 $LastChangedDate: 2009-07-16 15:56:35 +0200 (Thu, 16 Jul 2009) $
 $Revision: 1526 $
 
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

'''
This script is only for testing purposes. It is used to test the PathMTU M&M
without UNISONO running.
'''
from ctypes import *
from os import path, getcwd
import sys
import socket

class timeval(Structure):
  _fields_ = [("tv_sec", c_ulong),("tv_usec", c_ulong)]

print(path.join(getcwd(),'libMeasure.so'))
#cdll.LoadLibrary(path.join(getcwd(),'libMeasure.so'))
libmeasure = CDLL(path.join(getcwd(),'libMeasure.so'))
#int send_train(int train_length, int train_id, int packet_size, int sock_udp, int spacing);

sock_udp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock_udp.bind(("",43212))
train_length = 50
train_id = 0
packet_size = 1000

TimeStamps = timeval * train_length
ts= TimeStamps()
result = c_int(0)
libmeasure.recv_train(train_length,train_id,packet_size,sock_udp.fileno(),ts, byref(result))
print(result)
tsp = []
for i in ts:
  if i.tv_sec > 0:
    tsp.append(i.tv_sec * 1000000 + i.tv_usec)
  print(i.tv_sec,i.tv_usec)
  print(i.tv_sec * 1000000 + i.tv_usec)