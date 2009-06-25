'''
nic_resources.py

 Created on: May 14, 2009
 Authors: dh, cilku
 
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
                          ]
        self.cost = 500

    def checkrequest(self, request):
        return True

    def get_interfaces_for_ip(self, ip):
        """
        Returns a list of all network interfaces present, such as [eth0, eth1, lo]
        """
        proc_net_dev = open("/proc/net/dev")
        lines = proc_net_dev.readlines()
        proc_net_dev.seek(0)
        iflist = [ l[:l.find(":")].strip() for l in lines if ":" in l ]
        for i in iflist:
            # TODO: get rid of this popen!
            intinfo = popen('ifconfig ' + i).read()
            if ip in intinfo:
                return i
        return None

    def measure(self):
        interface = self.get_interfaces_for_ip(self.request['identifier1'])
        if interface == None:
            self.request["error"] = 404
            self.request["errortext"] = 'No interface found with this ip'
            return
        # TODO: get rid of this popen!
        intinfo = popen('ifconfig ' + interface).read()
        
        ## Properties Information:
        
        # Interface Type:        
        type = re.search("Link encap:(.*)", intinfo)
        if type != None:
            type = type.group()
            self.request['INTERFACE_TYPE'] = type.split()[1].split(':')[1]

#        # find information on Receive Rate
#        intcaprx = re.search("++++++:(.*)", intinfo)
#        if intcaprx != None:
#            intcaprx = intcaprx.group()
#            self.request['INTERFACE_CAPACITY_RX'] = intcaprx
#
#        # find information Transmission Rate
#        intcaptx = re.search("++++++:(.*)", intinfo)
#        if intcaptx != None:
#            intcaptx = intcaptx.group()
#            self.request['INTERFACE_CAPACITY_TX'] = intcaptx

        # MAC Address: 
        mac = re.search("HWaddr(.*)", intinfo)
        if mac != None:
            mac = mac.group()
            self.request['INTERFACE_MAC'] = mac.split()[1] 

        # MTU
        mtu = re.search("MTU:(.*)", intinfo)
        if mtu != None:
            mtu = mtu.group()
            self.request['INTERFACE_MTU'] = mtu.split()[0].split(':')[1]
        self.request["error"] = 0
        self.request["errortext"] = 'Everything went fine.'

        #Interface Information for the debugger
        self.logger.debug('The result is: %s', self.request)

class BandwidthUsage(mmtemplates.MMTemplate):
    def __init__(self, *args):
        super().__init__(*args)
        self.dataitems = [
                          'USED_BANDWIDTH_RX',
                          'USED_BANDWIDTH_TX'
                          ]
        self.cost = 2000

    def checkrequest(self, request):
        return True


    def measure(self):
        self.request["error"] = 0
        self.request["errortext"] = 'Everything went fine.'


class WifiReader(mmtemplates.MMTemplate):
    def __init__(self, *args):
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
                self.request['error'] = 404   
                self.request['errortext'] = "no wireless interface with this ip"

        wlaninfo = popen('iwconfig ' + interface).read()
        if len(wlaninfo) != 0:
            
            essid = re.search('ESSID:([^ ]+)', wlaninfo)
            if essid != None:
                essid = essid.group()
                self.request['WLAN_ESSID'] = essid.split(":")[1]
            
            mode = re.search('Mode:([^ ]+)', wlaninfo)
            if mode != None:
                mode = mode.group()
                self.request['WLAN_MODE'] = mode.split(':')[1]

            # Access Point MAC Address:
            apmac = re.search('Access Point: ([^ ]+)', wlaninfo)
            if apmac != None:
                apmac = apmac.group()
                self.request['WLAN_AP_MAC'] = apmac.split()[2]

            # Link quality:
            link = re.search('Link Quality=([^ ]+)', wlaninfo)
            if link != None:
                link = link.group()
                self.request['WLAN_LINK'] = link.split()[1].split("=")[1]

            # Signal Level:
            signal = re.search('Signal level:([^ ]+)', wlaninfo)
            if signal != None:
                signal = signal.group()
                self.request['WLAN_SIGNAL'] = signal.split(':')[1]

            # Noise Level:
            noise = re.search('Noise level=([^ ]+)', wlaninfo)
            if noise != None:
                noise = noise.group()
                self.request['WLAN_NOISE'] = noise.split('=')[1]

            # given in dB by Ratio = 10*lg(Signal/Noise)
            self.request['WLAN_SIGNOISE_RATIO'] = 10 * math.log10((int(self.request['WLAN_SIGNAL']) / int(self.request['WLAN_NOISE'])))         
            
            
            # Used Wireless Channel:
            chaninfo = popen("iwlist " + interface + " channel | grep Frequency").read()
            channel = re.search('Channel ([^ ]+)', wlaninfo)
            if channel != None:
                channel = channel.group()
                self.request['WLAN_CHANNEL'] = channel.split()[1]

            # Wireless Frequency:
            freq = re.search('Frequency=([^ ]+)', wlaninfo)
            if freq != None:
                freq = freq.group()
                self.request['WLAN_FREQUENCY'] = freq.split('=')[1]


#        #Wireless information for the debugger
        self.logger.debug('The result is: %s', self.request)

        self.request['error'] = 0
        self.request['errortext'] = 'Measurement successful'
        