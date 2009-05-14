'''
node_ressources.py

 Created on: May 14, 2009
 Authors: zxmqn07, dh
 
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
import threading, logging, re, string, sys
from unisono.mmplugins import mmtemplates
from unisono.utils import configuration


class ResourceReader(mmtemplates.MMTemplate):
    '''
    generic template for all M&Ms
    '''
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    def __init__(self, *args):
        '''
        init the M&M and start the thread
        '''
        super().__init__(*args)
        self.dataitems = ['CPU_TYPE',
                          'CPU_SPEED',
                          'CPU_CACHE_SIZE',
                          'CPU_CORE_COUNT',
                          'CPU_LOAD',
                          'HOST_UPTIME',
                          'RAM',
                          'RAM_FREE',
                          'SWAP',
                          'SWAP_FREE',
                          'PERSISTENT_MEMORY',
                          'FREE_PERSISTENT_MEMORY']
        self.cost = 500

    def checkrequest(self, request):
        return True

    def measure(self):
        cpu = open("/proc/cpuinfo" , "r")

        for cpuinfo in cpu:
            cpuinfo = cpuinfo.rstrip('\n')
            if re.match("(.*)model name(.*)", cpuinfo):
                self.request['CPU_TYPE'] = cpuinfo
#                    print(cpuinfo)
            if re.match("(.*)cpu MHz(.*)", cpuinfo):
                print(cpuinfo)
            if re.match("(.*)cache size(.*)", cpuinfo):
                print(cpuinfo)
            if re.match("(.*)cpu cores(.*)", cpuinfo):
                print(cpuinfo)
                print('\n')
        ram = open("/proc/meminfo", "r")
        for meminfo in ram:
            meminfo = meminfo.rstrip('\n')
            if re.match("(.*)MemTotal(.*)", meminfo):
                print(meminfo)
            if re.match("(.*)MemFree(.*)", meminfo):
                print(meminfo)
            if re.match("(.*)SwapTotal(.*)", meminfo):
                print(meminfo)
            if re.match("(.*)SwapFree(.*)", meminfo):
                print(meminfo)
                print('\n')
        os = open("/proc/version")
        for kernel in os:
            if re.match("(.*)(.*)", kernel):
                print(kernel)
        self.request['errorcode'] = 0
        self.request['errortext'] = 'Measurement successful'
