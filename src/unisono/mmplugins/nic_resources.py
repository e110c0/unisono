'''
nic_resources.py

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
                          'INTERFACE',
                          'INTERFACE_TYPE',
                          'INTERFACE_CAPACITY_RX',
                          'INTERFACE_CAPACITY_TX',    
                          'INTERFACE_MAC',
                          'INTERFACE_MTU',

                          'USED_BANDWIDTH_RX', 
                          'USED_BANDWIDTH_TX',
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

        ## Properties Information:
        
        type = re.search("Mode:(.*)", intinfo)
        if type != None:
            type = type.group()
            self.request['INTERFACE_TYPE'] = type
        else:
            self.request['INTERFACE_TYPE'] = "Information not Available"
        
        
        #TODO find information source in Systemmonitor
        intcaprx = re.search("++++++:(.*)", intinfo)
        if intcaprx != None:
            intcaprx = intcaprx.group()
            self.request['INTERFACE_CAPACITY_RX'] = intcaprx
        else:
            self.request['INTERFACE_CAPACITY_RX'] = "Information not Available"
        
        #TODO find information source in Systemmonitor
        intcaptx = re.search("++++++:(.*)", intinfo)
        if intcaptx != None:
            intcaptx = intcaptx.group()
            self.request['INTERFACE_CAPACITY_TX'] = "cant find"
        else:
            self.request['INTERFACE_CAPACITY_TX'] = "Information not Available"
        
        mac = re.search("HWaddr(.*)", intinfo)
        if mac != None:
            mac = mac.group()
            self.request['INTERFACE_MAC'] = mac     
        else:
            self.request['INTERFACE_MAC'] = "Information not Available"

    
        mtu = re.search("MTU:(.*)", intinfo)
        if mtu != None:
            mtu = mtu.group()
            self.request['INTERFACE_MTU'] = mtu
        else:
            self.request['INTERFACE_MTU'] = "Information not Available"
        
        
        #TODO find information source in Systemmonitor
        usbandrx = re.search("++++++:(.*)", intinfo)
        if usbandrx != None:
            usbandrx = usbandrx.group()
            self.request['USED_BANDWIDTH_RX'] = usbandrx
        else:
            self.request['USED_BANDWIDTH_RX'] = "Information not Available"
        
        
        #TODO find information source in Systemmonitor
        usbandtx = re.search("++++++:(.*)", intinfo)
        if usbandtx != None:
            usbandtx = usbandtx.group()
            self.request['USED_BANDWIDTH_TX'] = "cant find"
        else:
            self.request['USED_BANDWIDTH_TX'] = "Information not Available"

        #Interface Information for the debugger
        self.logger.debug('The result is: %s', self.request['INTERFACE_TYPE'])
        self.logger.debug('The result is: %s', self.request['INTERFACE_CAPACITY_RX'])
        self.logger.debug('The result is: %s', self.request['INTERFACE_CAPACITY_TX'])
        self.logger.debug('The result is: %s', self.request['INTERFACE_MAC'])
        self.logger.debug('The result is: %s', self.request['INTERFACE_MTU'])
        self.logger.debug('The result is: %s', self.request['USED_BANDWIDTH_RX'])
        self.logger.debug('The result is: %s', self.request['USED_BANDWIDTH_TX'])
            
        self.request['error'] = 0
        self.request['errortext'] = 'Measurement successful'

def WifiReader(mmtemplate):

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
        interface = "No wireless interface with this IP"
        intinfo=''
        for i in interfacelist:
            intinfo = popen('iwconfig ' + i).read()
            if ipaddress in intinfo:
                interface = i
                break
            else: 
                self.request['error'] = interface   
        
       
        # In this part the programs 
        
        
        
        wlaninfo = popen('iwconfig ' + interface).read()
        if len(wlaninfo) != 0:
            
            
            essid = re.search("ESSID:(.*)", wlaninfo)
            if essid != None:
                essid = essid.group()
                self.request['WLAN_ESSID'] = essid
            else:
                self.request['WLAN_ESSID'] = "Information not available"
            
            
            mode = re.search("Mode:(.*)", wlaninfo)
            if mode != None:
                mode = mode.group()
                self.request['WLAN_MODE'] = mode
            else:
                self.request['WLAN_MODE'] = "Information not available"
            
            apmac = re.search("Access Point:(.*)", wlaninfo)
            if apmac != None:
                apmac = apmac.group()
                self.request['WLAN_AP_MAC'] = apmac
            else:
                self.request['WLAN_AP_MAC'] = "Information not available"
            
            link = re.search("Mode(.*)", wlaninfo)
            if link != None:
                link = link.group()
                self.request['WLAN_LINK'] = link
            else:
                self.request['WLAN_LINK'] = "Information not available"
        
            signal = re.search("Signal level:(.*)", wlaninfo)
            if signal != None:
                signal = signal.group()
                self.request['WLAN_SIGNAL'] = signal 
            else:
                self.request['WLAN_SIGNAL'] = "Information not available"
        
            noise = re.search("Noise level=(.*)", wlaninfo)
            if noise != None:
                noise = noise.group()
                self.request['WLAN_NOISE'] = noise
            else:
                self.request['WLAN_NOISE'] = "Information not available"
            
#            TODO add correct calculation 
#            signoirat = re.search("Mode(.*)", wlaninfo)
#            if essid != None:
#                essid.group()
#            self.request['WLAN_SIGNOISE_RATIO'] = (self.request['WLAN_SIGNAL'] / self.request['WLAN_NOISE'])         
#            
#            channel = re.search("Mode(.*)", wlaninfo).group()
#            self.request['WLAN_CHANNEL']        = popen("iwlist " + interface + " channel | grep Frequency | perl -ple '($_) = /Channel\s([^ ]+)/'").read()
#            

            freq = re.search("Frequency:(.*)", wlaninfo)
            if freq != None:
                freq = freq.group()
                self.request['WLAN_FREQUENCY'] = freq
            else:
                self.request['WLAN_FREQUENCY'] = "Information not available"
            
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
            


        #Wireless information for the debugger
        self.logger.debug('The result is: %s', self.request['WLAN_ESSID'])
        self.logger.debug('The result is: %s', self.request['WLAN_MODE'])
        self.logger.debug('The result is: %s', self.request['WLAN_AP_MAC'])
        self.logger.debug('The result is: %s', self.request['WLAN_LINK'])
        self.logger.debug('The result is: %s', self.request['WLAN_SIGNAL'])
        self.logger.debug('The result is: %s', self.request['WLAN_NOISE'])
        self.logger.debug('The result is: %s', self.request['WLAN_ESSID'])
        self.logger.debug('The result is: %s', self.request['WLAN_FREQUENCY'])

        self.request['error'] = 0
        self.request['errortext'] = 'Measurement successful'



        