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
from os import statvfs
from unisono.dataitem import DataItem
from time import sleep

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
        self.dataitems = [DataItem('CPU_TYPE',0,1000,1000),
                          DataItem('CPU_SPEED',0,1000,1000),
                          DataItem('CPU_CACHE_SIZE',0,1000,1000),
                          DataItem('CPU_CORE_COUNT',0,1000,1000),
                          DataItem('RAM',0,1000,1000),
                          DataItem('RAM_USED',0,0,120),
                          DataItem('RAM_FREE',0,0,120),
                          DataItem('SWAP',0,1000,1000),
                          DataItem('SWAP_USED',0,0,120),
                          DataItem('SWAP_FREE',0,0,120),
                          DataItem('CPU_LOAD',0,0,120),
                          DataItem('CPU_LOAD_SYS',0,0,120),
                          DataItem('CPU_LOAD_USER',0,0,120),
                          DataItem('CPU_LOAD_WIO',0,0,120),
                          DataItem('CPU_LOAD_IDLE',0,0,120),
                          DataItem('HOST_UPTIME',0,0,1000),
                          DataItem('HOST_UPTIME_IDLE',0,0,1000),
                          DataItem('SYSTEM_LOAD_AVG_NOW',0,0,120),
                          DataItem('SYSTEM_LOAD_AVG_5MIN',0,0,300),
                          DataItem('SYSTEM_LOAD_AVG_15MIN',0,0,900),
                          DataItem('PERSISTENT_MEMORY',0,1000,1000),
                          DataItem('PERSISTENT_MEMORY_USED',0,0,120),
                          DataItem('PERSISTENT_MEMORY_FREE',0,0,120),
                          ]
        self.cost = 500

    def checkrequest(self, request):
        return True

    def measure(self):
        
        jiff1 = list(map(int, open("/proc/stat").read().split('\n')[0].split()[1:]))
        cpu = open("/proc/cpuinfo" , "r")
        for cpuinfo in cpu:
            cpuinfo = cpuinfo.rstrip('\n')
            if re.match("(.*)model name(.*)", cpuinfo):
                self.request['CPU_TYPE'] = cpuinfo.split(":")[1].strip()
            if re.match("(.*)cpu MHz(.*)", cpuinfo):
                self.request['CPU_SPEED'] = cpuinfo.split(":")[1].strip()
            if re.match("(.*)cache size(.*)", cpuinfo):
                self.request['CPU_CACHE_SIZE'] = cpuinfo.split(":")[1].strip().split(" ")[0]
            if re.match("(.*)cpu cores(.*)", cpuinfo):
                self.request['CPU_CORE_COUNT'] = cpuinfo.split(":")[1].strip().split(" ")[0]
        ram = open("/proc/meminfo", "r")
        for meminfo in ram:
            meminfo = meminfo.rstrip('\n')
            if re.match("(.*)MemTotal(.*)", meminfo):
                self.request['RAM'] = int(meminfo.split(":")[1].strip().split(" ")[0])
            if re.match("(.*)MemFree(.*)", meminfo):
                self.request['RAM_FREE'] = int(meminfo.split(":")[1].strip().split(" ")[0])
            if re.match("(.*)SwapTotal(.*)", meminfo):
                self.request['SWAP'] = int(meminfo.split(":")[1].strip().split(" ")[0])
            if re.match("(.*)SwapFree(.*)", meminfo):
                self.request['SWAP_FREE'] = int(meminfo.split(":")[1].strip().split(" ")[0])
                self.request['RAM_USED'] = self.request['RAM'] - self.request['RAM_FREE']
                self.request['SWAP_USED'] = self.request['SWAP'] - self.request['SWAP_FREE']

        tmpdata = open('/proc/loadavg').read().split()
        self.request['SYSTEM_LOAD_AVG_NOW'] = float(tmpdata[0])
        self.request['SYSTEM_LOAD_AVG_5MIN'] = float(tmpdata[1])
        self.request['SYSTEM_LOAD_AVG_15MIN'] = float(tmpdata[2])
        
        tmpdata = open("/proc/uptime").read().split()
        self.request['HOST_UPTIME'] = tmpdata[0]
        self.request['HOST_UPTIME_IDLE'] = tmpdata[1]
        
        tmpdata = statvfs("/var/tmp")
        self.request['PERSISTENT_MEMORY'] = int( tmpdata.f_bsize * tmpdata.f_blocks / 1024 )
        self.request['PERSISTENT_MEMORY_USED'] = int( (tmpdata.f_bsize * tmpdata.f_blocks - tmpdata.f_bsize * tmpdata.f_bfree) / 1024 )
        self.request['PERSISTENT_MEMORY_FREE'] = int(tmpdata.f_bsize * tmpdata.f_bavail / 1024)
        
        os = open("/proc/version")
        for kernel in os:
            if re.match("(.*)(.*)", kernel):
                #print(kernel)
                pass
        sleep(1)
        jiff2 = list(map(int, open("/proc/stat").read().split('\n')[0].split()[1:]))
        diff = list(map(lambda x: x[1] - x[0], zip(jiff1, jiff2)))
        duse = diff[0] + diff[1]
        dsys = diff[2] + diff[5] + diff[6]
        didl = diff[3]
        diow = diff[4]
        dstl = diff[7]
        summ = duse + dsys + didl + diow + dstl
        if summ > 0:
            self.request['CPU_LOAD_USER'] = int(100 * duse / summ)
            self.request['CPU_LOAD_SYS'] = int(100 * dsys / summ)
            self.request['CPU_LOAD_IDLE'] = int(100 * didl / summ)
            self.request['CPU_LOAD_WIO'] = int(100 * diow / summ)
            self.request['CPU_LOAD'] = int(100 - self.request['CPU_LOAD_IDLE'])
        else:
            self.request['CPU_LOAD_USER'] = 0
            self.request['CPU_LOAD_SYS'] = 0
            self.request['CPU_LOAD_IDLE'] = 100 
            self.request['CPU_LOAD_WIO'] = 0
            self.request['CPU_LOAD'] = 100 - self.request['CPU_LOAD_IDLE']

        self.request['error'] = 0
        self.request['errortext'] = 'Measurement successful'
