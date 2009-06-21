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


        
        ## Properties Information:
        
        # Interface Type:        
        type = re.search("Link encap:(.*)", intinfo)
        if type != None:
            type = type.group()
            self.request['INTERFACE_TYPE'] = type.split()[1].split(':')[1]
        else:
            self.request['INTERFACE_TYPE'] = "Information not Available"
        
        
        #TODO find information on Receive Rate
        intcaprx = re.search("++++++:(.*)", intinfo)
        if intcaprx != None:
            intcaprx = intcaprx.group()
            self.request['INTERFACE_CAPACITY_RX'] = intcaprx
        else:
            self.request['INTERFACE_CAPACITY_RX'] = "Information not Available"


        #TODO find information Transmission Rate
        intcaptx = re.search("++++++:(.*)", intinfo)
        if intcaptx != None:
            intcaptx = intcaptx.group()
            self.request['INTERFACE_CAPACITY_TX'] = intcaptx
        else:
            self.request['INTERFACE_CAPACITY_TX'] = "Information not Available"
        
        # MAC Address: 
        mac = re.search("HWaddr(.*)", intinfo)
        if mac != None:
            mac = mac.group()
            self.request['INTERFACE_MAC'] = mac.split()[1] 
        else:
            self.request['INTERFACE_MAC'] = "Information not Available"
        
        # MTU
        mtu = re.search("MTU:(.*)", intinfo)
        if mtu != None:
            mtu = mtu.group()
            self.request['INTERFACE_MTU'] = mtu.split()[0].split(':')[1]
        else:
            self.request['INTERFACE_MTU'] = "Information not Available"

        
        # Received bytes
        usbandrx = re.search('RX bytes:([^ ]+)', intinfo)
        if usbandrx != None:
            usbandrx = usbandrx.group()
            self.request['USED_BANDWIDTH_RX'] = usbandrx.split(':')[1]
        else:
            self.request['USED_BANDWIDTH_RX'] = "Information not Available"
            
        # Transmitted bytes
        usbandtx = re.search('TX bytes:([^ ]+)', intinfo)
        if usbandtx != None:
            usbandtx = usbandtx.group()
            self.request['USED_BANDWIDTH_TX'] = usbandtx.split(':')[1]
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

        
        #Wireless interfaces
        wlaninfo = popen('iwconfig ' + interface).read()
        # if we have a wirelss interface -> 1
        # else -> 2
        if len(wlaninfo) != 0:
            # -> 1 each field will be initialized
            
            # ESSID of the Wireless connection:
            essid = re.search('ESSID:([^ ]+)', wlaninfo)
            if essid != None:
                essid = essid.group()
                self.request['WLAN_ESSID'] = essid.split(":")[1]
            else:
                self.request['WLAN_ESSID'] = "Information not available"

            # Connection mode:
            mode = re.search('Mode:([^ ]+)', wlaninfo)
            if mode != None:
                mode = mode.group()
                self.request['WLAN_MODE'] = mode.split(':')[1]
            else:
                self.request['WLAN_MODE'] = "Information not available"

            # Access Point MAC Address:
            apmac = re.search('Access Point: ([^ ]+)', wlaninfo)
            if apmac != None:
                apmac = apmac.group()
                self.request['WLAN_AP_MAC'] = apmac.split()[2]
            else:
                self.request['WLAN_AP_MAC'] = "Information not available"
                        
            # Link quality:
            link = re.search('Link Quality=([^ ]+)', wlaninfo)
            if link != None:
                link = link.group()
                self.request['WLAN_LINK'] = link.split()[1].split("=")[1]
            else:
                self.request['WLAN_LINK'] = "Information not available"

            # Signal Level:
            signal = re.search('Signal level:([^ ]+)', wlaninfo)
            if signal != None:
                signal = signal.group()
                self.request['WLAN_SIGNAL'] = signal.split(':')[1]
            else:
                self.request['WLAN_SIGNAL'] = "Information not available"
            
            # Noise Level:
            noise = re.search('Noise level=([^ ]+)', wlaninfo)
            if noise != None:
                noise = noise.group()
                self.request['WLAN_NOISE'] = noise.split('=')[1]
            else:
                self.request['WLAN_NOISE'] = "Information not available"            
            
            # given in dB by Ratio = 10*lg(Signal/Noise) 
            # we have to assure that Signal and Noise are available
            if "Information not available" not in self.request['WLAN_SIGNAL'] and "Information not available" not in self.request['WLAN_NOISE']: 
                self.request['WLAN_SIGNOISE_RATIO'] = 10 * math.log10((int(self.request['WLAN_SIGNAL']) / int(self.request['WLAN_NOISE'])))         
            else:
                self.request['WLAN_SIGNOISE_RATIO'] = "Information not available" 
            
            
            # Used Wireless Channel:
            chaninfo = popen("iwlist " + interface + " channel | grep Frequency").read()
            channel = re.search('Channel ([^ ]+)', wlaninfo)
            if channel != None:
                channel = channel.group()
                self.request['WLAN_CHANNEL'] = channel.split()[1]
            else:
                self.request['WLAN_CHANNEL'] = "Information not available"
            
            # Wireless Frequency:
            freq = re.search('Frequency=([^ ]+)', wlaninfo)
            if freq != None:
                freq = freq.group()
                self.request['WLAN_FREQUENCY'] = freq.split('=')[1]
            else:
                self.request['WLAN_FREQUENCY'] = "Information not available"
    
        else:
            # -> 2 each field will be initialized with
            # "this is not a wireless interface" 
            
            # Case when we have no wireless device:
            self.request['WLAN_ESSID']          = "this is not a wireless interface"
            self.request['WLAN_MODE']           = "this is not a wireless interface"
            self.request['WLAN_AP_MAC']         = "this is not a wireless interface"
            self.request['WLAN_LINK']           = "this is not a wireless interface"
            self.request['WLAN_SIGNAL']         = "this is not a wireless interface"
            self.request['WLAN_NOISE']          = "this is not a wireless interface"
            self.request['WLAN_SIGNOISE_RATIO'] = "this is not a wireless interface"
            self.request['WLAN_CHANNEL']        = "this is not a wireless interface"
            self.request['WLAN_FREQUENCY']      = "this is not a wireless interface"
#            self.request['wireless error']      = "this is not a wireless interface"



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



class NicTest(unittest.TestCase):                            
    
    # Case where the input IP doesn't match with any Interface.
    def nonexistingnic(self, NicReader):                           
        #identifier1 has to be an IP address                                          
        NicReader.measure(self.request['identifier1' : "Nonsense"])
        self.assertEqual(NicReader.dataitems['error'], "No interface with this IP")

    # Case when we have a loopback Interface
    def lopdevice(self, NicReader):
        #identifier1 has to be 127.0.0.1
        NicReader.measure(self.request['identifier1' : "Nonsense"])
        # This is neither a common interface nor a wireless interface
        # the difference from the common nic is that "lo" doesn't have
        # MAC address so:
        self.assertEqual(NicReader.dataitems['INTERFACE_MAC'], "Information not Available")
        self.assertEqual(NicReader.dataitems['WLAN_ESSID'], "this is not a wireless interface")
        self.assertEqual(NicReader.dataitems['WLAN_MODE'], "this is not a wireless interface")
        self.assertEqual(NicReader.dataitems['WLAN_AP_MAC'], "this is not a wireless interface")

    # Case when we have a common network interface
    def ethdevice(self, NicReader):
        PASS
        #TODO:

    # Case when we have a wireless network interface
    def wlandevive(self, NicReader):
        PASS
        #TODO



#WifiReader is implemented.
#def WifiReader(mmtemplate):
#
#    '''
#    generic template for all M&Ms
#    '''
#    logger = logging.getLogger(__name__)
#    logger.setLevel(logging.DEBUG)
#
#    def __init__(self, *args):
#        '''
#        init the M&M and start the thread
#        '''
#        super().__init__(*args)
#        self.dataitems = [
#                          'WLAN_ESSID',
#                          'WLAN_MODE',
#                          'WLAN_AP_MAC',
#                          'WLAN_LINK',
#                          'WLAN_SIGNAL',
#                          'WLAN_NOISE',            
#                          'WLAN_SIGNOISE_RATIO',
#                          'WLAN_CHANNEL',
#                          'WLAN_FREQUENCY'
#                          ]
#        self.cost = 500
#
#    def checkrequest(self, request):
#        return True
#
#
#    def measure(self):
#        
#        ipaddress = self.request['identifier1']
#        interfacelist = popen('dir /proc/net/dev_snmp6/').read().split()
#        self.logger.debug(interfacelist)
#        interface = "No wireless interface with this IP"
#        intinfo=''
#        for i in interfacelist:
#            intinfo = popen('iwconfig ' + i).read()
#            if ipaddress in intinfo:
#                interface = i
#                break
#            else: 
#                self.request['error'] = interface   
#        
#       
#        # In this part the programs 
#        
#        
#                wlaninfo = popen('iwconfig ' + interface).read()
#        if len(wlaninfo) != 0:
#            
#            essid = re.search('ESSID:([^ ]+)', wlaninfo)
#            if essid != None:
#                essid = essid.group()
#                self.request['WLAN_ESSID'] = essid.split(":")[1]
#            else:
#                self.request['WLAN_ESSID'] = "Information not available"
#            
#            
#            mode = re.search('Mode:([^ ]+)', wlaninfo)
#            if mode != None:
#                mode = mode.group()
#                self.request['WLAN_MODE'] = mode.split(':')[1]
#            else:
#                self.request['WLAN_MODE'] = "Information not available"
#            
#            # Access Point MAC Address:
#            apmac = re.search('Access Point: ([^ ]+)', wlaninfo)
#            if apmac != None:
#                apmac = apmac.group()
#                self.request['WLAN_AP_MAC'] = apmac.split()[2]
#            else:
#                self.request['WLAN_AP_MAC'] = "Information not available"
#            
#            # Link quality:
#            link = re.search('Link Quality=([^ ]+)', wlaninfo)
#            if link != None:
#                link = link.group()
#                self.request['WLAN_LINK'] = link.split()[1].split("=")[1]
#            else:
#                self.request['WLAN_LINK'] = "Information not available"
#        
#            # Signal Level:
#            signal = re.search('Signal level:([^ ]+)', wlaninfo)
#            if signal != None:
#                signal = signal.group()
#                self.request['WLAN_SIGNAL'] = signal.split(':')[1]
#            else:
#                self.request['WLAN_SIGNAL'] = "Information not available"
#                
#            # Noise Level:
#            noise = re.search('Noise level=([^ ]+)', wlaninfo)
#            if noise != None:
#                noise = noise.group()
#                self.request['WLAN_NOISE'] = noise.split('=')[1]
#            else:
#                self.request['WLAN_NOISE'] = "Information not available"
#            
#            
#            # given in dB by Ratio = 10*lg(Signal/Noise)
#            self.request['WLAN_SIGNOISE_RATIO'] = 10 * math.log10((int(self.request['WLAN_SIGNAL']) / int(self.request['WLAN_NOISE'])))         
#            
#            
#            # Used Wireless Channel:
#            chaninfo = popen("iwlist " + interface + " channel | grep Frequency").read()
#            channel = re.search('Channel ([^ ]+)', wlaninfo)
#            if channel != None:
#                channel = channel.group()
#                self.request['WLAN_CHANNEL'] = channel.split()[1]
#            else:
#                self.request['WLAN_CHANNEL'] = "Information not available"
#            
#            # Wireless Frequency:
#            freq = re.search('Frequency=([^ ]+)', wlaninfo)
#            if freq != None:
#                freq = freq.group()
#                self.request['WLAN_FREQUENCY'] = freq.split('=')[1]
#            else:
#                self.request['WLAN_FREQUENCY'] = "Information not available"
#            
#        else:
#            # Case when we have no wireless device:
#            self.request['WLAN_ESSID']          = "this is not a wireless interface"
#            self.request['WLAN_MODE']           = "this is not a wireless interface"
#            self.request['WLAN_AP_MAC']         = "this is not a wireless interface"
#            self.request['WLAN_LINK']           = "this is not a wireless interface"
#            self.request['WLAN_SIGNAL']         = "this is not a wireless interface"
#            self.request['WLAN_NOISE']          = "this is not a wireless interface"
#            self.request['WLAN_SIGNOISE_RATIO'] = "this is not a wireless interface"
#            self.request['WLAN_CHANNEL']        = "this is not a wireless interface"
#            self.request['WLAN_FREQUENCY']      = "this is not a wireless interface"
#            
#
#
#        #Wireless information for the debugger
#        self.logger.debug('The result is: %s', self.request['WLAN_ESSID'])
#        self.logger.debug('The result is: %s', self.request['WLAN_MODE'])
#        self.logger.debug('The result is: %s', self.request['WLAN_AP_MAC'])
#        self.logger.debug('The result is: %s', self.request['WLAN_LINK'])
#        self.logger.debug('The result is: %s', self.request['WLAN_SIGNAL'])
#        self.logger.debug('The result is: %s', self.request['WLAN_NOISE'])
#        self.logger.debug('The result is: %s', self.request['WLAN_ESSID'])
#        self.logger.debug('The result is: %s', self.request['WLAN_FREQUENCY'])
#
#        

#        self.request['error'] = 0
#        self.request['errortext'] = 'Measurement successful'
        