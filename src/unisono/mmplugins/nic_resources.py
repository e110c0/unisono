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
from os import popen

class NicReader(mmtemplates.MMTemplate):
    '''
    generic template for all M&Ms
    '''
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

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

    def measure(self):
        ipaddress = self.request['identifier1']
        interfacelist = popen('dir /proc/net/dev_snmp6/').read().split()
        self.logger.debug(interfacelist)
        interface = "No interface with this IP"
        intinfo=''
        for i in interfacelist:
            intinfo = popen('ifconfig ' + i).read()
            if ipaddress in intinfo:
                interface = i
                break
            else: 
                self.request['error'] = interface

        
        #TODO broken
        self.request['INTERFACE_TYPE'] = intinfo.split('\n')[0].strip().split()[2].split(':')[1]
        self.request['INTERFACE_CAPACITY_RX'] = "cant find"
        self.request['INTERFACE_CAPACITY_TX'] = "cant find"
        #TODO broken
        self.request['INTERFACE_MAC'] = intinfo.split('\n')[0].strip().split()[4]
        self.request['INTERFACE_MTU'] = intinfo.split('\n')[3].strip().split()[4].split(':')[1]
        
        self.request['USED_BANDWIDTH_RX'] = "cant find"
        self.request['USED_BANDWIDTH_TX'] = "cant find"
        
        
      # wireless
        wlaninfo = popen('iwconfig ' + interface).read()
        if ipaddress in wlaninfo:
            self.request['WLAN_ESSID']          = wlaninfo.split('\n')[0].strip().split()[3].split(':')[1]
            self.request['WLAN_MODE']           = wlaninfo.split('\n')[1].split()[0].split(':')[1]
            self.request['WLAN_AP_MAC']         = wlaninfo.split('\n')[1].split()[5]
            self.request['WLAN_LINK']           = wlaninfo.split('\n')[5].split()[1]
            self.request['WLAN_SIGNAL']         = wlaninfo.split('\n')[5].split()[3].split(':')[1]
            self.request['WLAN_NOISE']          = wlaninfo.split('\n')[5].split()[6].split('=')[1]
            self.request['WLAN_SIGNOISE_RATIO'] = "cant find"
            self.request['WLAN_CHANNEL']        = "cant find"
            self.request['WLAN_FREQUENCY']      = wlaninfo.split('\n')[1].split()[1].split(':')[1]
        else:
            self.request['wireless error'] = "this is not a wireless interface"
        
        
        self.request['error'] = 0
        self.request['errortext'] = 'Measurement successful'

        