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


        
        self.request['INTERFACE_TYPE'] = popen("ifconfig " + interface + " | grep encap | perl -ple '($_) = /encap:([^ ]+)/'").read()
        print("Interface Type: ****************************************" + self.request['INTERFACE_TYPE'])
        
        
        #TODO im system monitor sourcecode die quelle herausfinden
        self.request['INTERFACE_CAPACITY_RX'] = "cant find"
        print("Interface Capacity RX: " + self.request['INTERFACE_CAPACITY_RX'])
        #TODO im system monitor sourcecode die quelle herausfinden
        self.request['INTERFACE_CAPACITY_TX'] = "cant find"
        print("Interface Capacity TX: " + self.request['INTERFACE_CAPACITY_TX'])
        
        
        self.request['INTERFACE_MAC'] = popen("ifconfig " + interface + " | grep HWaddr | perl -ple '($_) = /HWaddr\s(.+)\s/'").read()
        print("Interface Mac: **************************************** " + self.request['INTERFACE_MAC'])
        
        self.request['INTERFACE_MTU'] = popen("ifconfig " + interface + " | grep MTU | perl -ple '($_) = /MTU:([^ ]+)/'").read()
        print("Interface MTU: " + self.request['INTERFACE_MTU'])
        
        #TODO im system monitor sourcecode die quelle herausfinden
        self.request['USED_BANDWIDTH_RX'] = "cant find"
        print("Interface Bandwidth RX: " + self.request['USED_BANDWIDTH_RX'])
        #TODO im system monitor sourcecode die quelle herausfinden
        self.request['USED_BANDWIDTH_TX'] = "cant find"
        print("Interface Bandwidth TX: " + self.request['USED_BANDWIDTH_TX'])
        
        # in diesem bereich wird was wlan behandelt 
        # im fall das es ein wlan ist dann werden 
        # die einzelnen felder der dictionary mit 
        # der ausgabe von iwconfig aufgefült
        wlaninfo = popen('iwconfig ' + interface).read()
        if "no wireless extensions" not in wlaninfo:
            self.request['WLAN_ESSID']          = popen("iwconfig " + interface + " | grep ESSID | perl -ple '($_) = /ESSID:([^ ]+)/'").read()
            # nur zur fehler kontrolle
            print("Wlan Essid ****************************************:" + self.request['WLAN_ESSID'])
            
            self.request['WLAN_MODE']           = popen("iwconfig " + interface + " | grep Mode | perl -ple '($_) = /Mode:([^ ]+)/'").read()
            print("Wlan Mode ****************************************: " + self.request['WLAN_MODE'])
            
            self.request['WLAN_AP_MAC']         = popen("iwconfig " + interface + " | grep Point | perl -ple '($_) = /Point:\s([^ ]+)/'").read()
            print("Wlan AP Mac ****************************************: " + self.request['WLAN_AP_MAC'])
            
            self.request['WLAN_LINK']           = popen("iwconfig " + interface + " | grep Quality | perl -ple '($_) = /Quality=([^ ]+)/'").read()
            print("Wlan Link ****************************************: " + self.request['WLAN_LINK'])
            
            self.request['WLAN_SIGNAL']         = popen("iwconfig " + interface + " | grep Signal | perl -ple '($_) = /Signal level:([^ ]+)/'").read()
            print("Wlan Signal ****************************************: " + self.request['WLAN_SIGNAL'])
            
            self.request['WLAN_NOISE']          = popen("iwconfig " + interface + " | grep Noise | perl -ple '($_) = /Noise level=([^ ]+)/'").read()
            print("Wlan Noise ****************************************: " + self.request['WLAN_NOISE'])
            
            #muss die noch richtig ausgerechnet werden
            #self.request['WLAN_SIGNOISE_RATIO'] = (self.request['WLAN_SIGNAL'] / self.request['WLAN_NOISE'])
            #print("Wlan Essid: " + self.request['WLAN_ESSID'])
            
            self.request['WLAN_CHANNEL']        = popen("iwlist " + interface + " channel | grep Frequency | perl -ple '($_) = /Channel\s([^ ]+)/'").read()
            print("Wlan Channel ****************************************: " + self.request['WLAN_CHANNEL'])
            
            self.request['WLAN_FREQUENCY']      = popen("iwconfig " + interface + " | grep Frequency | perl -ple '($_) = /Frequency:([^ ]+)/'").read()
            print("Wlan Frequenz ****************************************: " + self.request['WLAN_FREQUENCY'])
        else:
            # im es sich nicht um ein wlan handel dan 
            # werden die felder mit "this is not a wireless
            #interface" aufgefült
            self.request['WLAN_ESSID']          = "this is not a wireless interface"
            self.request['WLAN_MODE']           = "this is not a wireless interface"
            self.request['WLAN_AP_MAC']         = "this is not a wireless interface"
            self.request['WLAN_LINK']           = "this is not a wireless interface"
            self.request['WLAN_SIGNAL']         = "this is not a wireless interface"
            self.request['WLAN_NOISE']          = "this is not a wireless interface"
            self.request['WLAN_SIGNOISE_RATIO'] = "this is not a wireless interface"
            self.request['WLAN_CHANNEL']        = "this is not a wireless interface"
            self.request['WLAN_FREQUENCY']      = "this is not a wireless interface"
            self.request['wireless error']      = "this is not a wireless interface"
    
        
        self.request['error'] = 0
        self.request['errortext'] = 'Measurement successful'

def WifiReader(mmtemplate):
    pass
        