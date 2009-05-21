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
from unisono.mmplugins import mmtemplates
from unisono.utils import configuration


class NicReader(mmtemplates.MMTemplate):
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
        self.dataitems = [
                          'INTERFACE_TYPE',
                          'INTERFACE_CAPACITY_RX',
                          'INTERFACE_CAPACITY_TX',    
                          'INTERFACE_MAC',
                          'INTERFACE_MTU',

                          'USED_BANDWIDTH_RX', 
                          'USED_BANDWIDTH_TX',
                          # wireless
                          'WLAN_ESSID',
                          'WLAN_MODE',
                          'WLAN_AP_MAC',
                          'WLAN_LINK',
                          'WLAN_SIGNAL',
                          'WLAN_NOISE',            
                          'WLAN_SIGNOISE_RATIO',
                          'WLAN_CHANNEL',
                          'WLAN_FREQUENCY'
                          ]
        self.cost = 500

    def checkrequest(self, request):
        return True

    def measure(self, ipaddress):
        interfacelist = os.popen('dir /proc/net/dev_snmp6/').read().split()
        interface = "No interface with this IP"
        i=0;
        while i <= interfacelist.itemsize:
            i = i+1
            if ipaddress in os.popen('ifconfig '+ interfacelist[i]).read():
                interface = interfacelist[i]
            else: 
                self.request['error'] = interface
                break
        
        intinfo = os.popen('infonfig' + interface).read()
        
        self.request['INTERFACE_TYPE'] = intinfo.split('\n')[0].strip().split()[2].split(':')[1]
        self.request['INTERFACE_CAPACITY_RX'] = "cant find"
        self.request['INTERFACE_CAPACITY_TX'] = "cant find"
        self.request['INTERFACE_MAC'] = intinfo.split('\n')[0].strip().split()[4]
        self.request['INTERFACE_MTU'] = intinfo.split('\n')[3].strip().split()[4].split(':')[1]
        
        
            
        
        
        

        