'''
file_name

 Created on: May 14, 2009
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
import threading, logging, re, string, sys

class resourcereader:
    '''
    generic template for all M&Ms
    '''
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    name = "wlanreader"
    
    def __init__(self,name):
        '''
        init the M&M and start the thread
        '''
        self.name = name
        mm_thread = threading.Thread(target=self.run)
        # Exit the server thread when the main thread terminates
        mm_thread.setDaemon(True)
        mm_thread.start()
        self.logger.info("M&M %s loop running in thread: %s", self.name, mm_thread.name)
        
    def measure(self):
            cpu = open("/proc/cpuinfo" , "r")
            info = {}
            for cpuinfo in cpu:
                cpuinfo = cpuinfo.rstrip('\n')
                if re.match("(.*)model name(.*)", cpuinfo):
                    
                    print(cpuinfo)
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
                    
    def provideDataItems(self):
        pass
    def provideMMname(self):
        pass