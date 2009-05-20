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
                          'RAM_USED',
                          'RAM_FREE',
                          'SWAP',
                          'SWAP_USED',
                          'SWAP_FREE',
                          'PERSISTENT_MEMORY',
                          'FREE_PERSISTENT_MEMORY'
                          'CPU_LOAD_SYS'
                          'CPU_LOAD_USER'
                          'CPU_LOAD_WIO'
                          'CPU_LOAD_IDLE'
                          'HOST_UPTIME'
                          'HOST_UPTIME_IDLE'
                          'SYTEM_LOAD_AVG_NOW'
                          'SYSTEM_LOAD_AVG_5MIN'
                          'SYSTEM_LOAD_AVG_15MIN'
                          'PERSISTENT_MEMORY'
                          'PERSISTENT_MEMORY_MOUNT'
                          'PERSISTENT_MEMORY_USED'
                          'PERSISTENT_MEMORY_FREE'
]
        self.cost = 500

    def checkrequest(self, request):
        return True

    def measure(self):
        cpu = open("/proc/cpuinfo" , "r")

        for cpuinfo in cpu:
            cpuinfo = cpuinfo.rstrip('\n')
            if re.match("(.*)model name(.*)", cpuinfo):
                self.request['CPU_TYPE'] = cpuinfo.split(":")[1].strip()
#                print(cpuinfo)
            if re.match("(.*)cpu MHz(.*)", cpuinfo):
                self.request['CPU_SPEED'] = cpuinfo.split(":")[1].strip()
#                print(cpuinfo)
            if re.match("(.*)cache size(.*)", cpuinfo):
                self.request['CPU_CACHE_SIZE'] = cpuinfo.split(":")[1].strip().split(" ")[0]
 #               print(cpuinfo)
            if re.match("(.*)cpu cores(.*)", cpuinfo):
                self.request['CPU_CORE_COUNT'] = cpuinfo.split(":")[1].strip().split(" ")[0]
#                print(cpuinfo)
#                print('\n')
        ram = open("/proc/meminfo", "r")
        for meminfo in ram:
            meminfo = meminfo.rstrip('\n')
            if re.match("(.*)MemTotal(.*)", meminfo):
                self.request['RAM'] = meminfo
#                print(meminfo)
            if re.match("(.*)MemFree(.*)", meminfo):
                self.request['RAM_FREE'] = meminfo.split(":")[1].strip().split(" ")[0]
#                print(meminfo)
            if re.match("(.*)SwapTotal(.*)", meminfo):
                self.request['SWAP'] = meminfo.split(":")[1].strip().split(" ")[0]
#                print(meminfo)
            if re.match("(.*)SwapFree(.*)", meminfo):
                self.request['SWAP_FREE'] = meminfo.split(":")[1].strip().split(" ")[0]
#                print(meminfo)
#                print('\n')
                self.request['RAM_USED'] = self.request['RAM'] - self.request['RAM_FREE']
                self.request['SWAP_USED'] = self.request['SWAP'] - self.request['SWAP_FREE']
        
        self.request['CPU_LOAD_USER'] = os.popen('vmstat').read().split('\n')[2].strip().split()[12]
        self.request['CPU_LOAD_SYS'] = os.popen('vmstat').read().split('\n')[2].strip().split()[13]
        self.request['CPU_LOAD_IDLE'] = os.popen('vmstat').read().split('\n')[2].strip().split()[14]
        self.request['CPU_LOAD_WIO'] = os.popen('vmstat').read().split('\n')[2].strip().split()[15]
        
        self.request['SYTEM_LOAD_AVG_NOW'] =  os.popen('uptime').read().split(",",2)[2].strip().split(":")[1].strip().split(", ")[0]
        self.request['SYSTEM_LOAD_AVG_5MIN'] = os.popen('uptime').read().split(",",2)[2].strip().split(":")[1].strip().split(", ")[1]
        self.request['SYSTEM_LOAD_AVG_15MIN'] =  os.popen('uptime').read().split(",",2)[2].strip().split(":")[1].strip().split(", ")[2]
        
        self.request['HOST_UPTIME'] = open("/proc/uptime").read().split()[0]
        self.request['HOST_UPTIME_IDLE'] = open("/proc/uptime").read().split()[1]
        
        self.request['PERSISTENT_MEMORY_MOUNT'] = os.popen('df').read().split("\n")[1].split()[0]
        self.request['PERSISTENT_MEMORY'] = os.popen('df').read().split("\n")[1].split()[1]
        self.request['PERSISTENT_MEMORY_USED'] = os.popen('df').read().split("\n")[1].split()[2]
        self.request['PERSISTENT_MEMORY_FREE'] = os.popen('df').read().split("\n")[1].split()[3]
        
        os = open("/proc/version")
        for kernel in os:
            if re.match("(.*)(.*)", kernel):
                print(kernel)
        self.request['error'] = 0
        self.request['errortext'] = 'Measurement successful'
