#!/usr/bin/env python3
'''
iftester.py

 Created on: Jul 20, 2009
 Authors: dh
 
 $LastChangedBy: haage $
 $LastChangedDate: 2009-07-16 15:55:22 +0200 (Thu, 16 Jul 2009) $
 $Revision: 1525 $
 
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


import xmlrpc.client
from sys import stdin
from time import sleep
from itertools import count

counter = 0
myID = ""

if __name__ == '__main__':
    s = xmlrpc.client.ServerProxy('http://localhost:45678')
    # Print list of available methods
    print("we do some stuff")
    print(s.system.listMethods())
    print(s.system.methodHelp('getDB'))
    dump = s.getDB()
    print('Database: \n\n ' + dump + '\n\n')

    print('-------------------------------------------------------')

    print(s.system.methodHelp('getLog'))
    log = s.getLog()
    print('Log: \n\n ' + log + '\n\n')

    print('-------------------------------------------------------')

    print(s.system.methodHelp('getStats'))
    stats = s.getStats()
    print('Stats: \n\n ')
    for i in stats.keys():
        print(i + ':' + stats[i])

    print('FINISHED!!!')
