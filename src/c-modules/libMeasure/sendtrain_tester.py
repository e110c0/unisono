#!/usr/bin/env python3
# encoding: utf-8
'''
sendtrain_tester.py

 Created on: May 11, 2009
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

'''
This script is only for testing purposes. It is used to test the PathMTU M&M
without UNISONO running.
'''
from ctypes import *
from os import path, getcwd
import sys
import socket


print(path.join(getcwd(),'libMeasure.so'))
cdll.LoadLibrary(path.join(getcwd(),'libMeasure.so'))
libmeasure = CDLL(path.join(getcwd(),'libMeasure.so'))
#int send_train(int train_length, int train_id, int packet_size, int sock_udp, int spacing);

sock_udp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock_udp.bind(("",0))
sock_udp.connect(("127.0.0.1",43212))
'''
result = libmeasure.send_train(45,0,1000,sock_udp.fileno(),0)
print(result)

result = libmeasure.send_train(45,1,1000,sock_udp.fileno(),0)
print(result)
'''

result = libmeasure.send_fleet(10,50,1000,sock_udp.fileno(),0)
print(result)
