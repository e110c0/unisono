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

import threading, logging, re, string, sys, fcntl, socket, time
#from unisono.mmplugins import mmtemplates
#from unisono.utils import configuration
from os import popen

def get_interfaces_for_ip(self, ip):
    
    try:
    # Returns the interface with the given IP, such as eth0, eth1, wlan1, etc.
        proc_net_dev = open("/proc/net/dev")
        lines = proc_net_dev.readlines()
        proc_net_dev.seek(0)
        iflist = [ l[:l.find(":")].strip() for l in lines if ":" in l ]
        for i in iflist:
            intip = get_ip_for_interface(self, i)
            if intip.strip() == ip.strip():
                return i
            else: return None
    except IOError:
        self.request['error'] = 999
        self.request['errortext'] = 'no Interface for given IP'
        raise IOError
    
    # Get IP address for Interface
def get_ip_for_interface(self, iface):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ipinfo = fcntl.ioctl(s.fileno(), 0x8915, ifr)
        ip = socket.inet_ntoa(result[20:24])
        return ip
    except IOError:
        self.request['error'] = 999
        self.request['errortext'] = 'no IP for given Interface'
        raise IOError


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



    def measure(self):
        
        try:
            interface = get_interfaces_for_ip(self.request['identifier1'])
            interface = interface.strip()
        except Error:
            raise Error
        
        # I've added a new Entry in the dictionary so i don't have to check
        # each time which interface i have to use 
                   
        # Opening measurment socket
        try:
            tsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Error:
            Error
        #--------------------NEW-------------------------
        
        # MAC Address: 
        iface = interface + '\0'*(32-len(iface))
        try:
            info = fcntl.ioctl(tsoc.fileno(), 0x8927, iface)
            mac = (':'.join(map(lambda n: "%02x" % n, info[18:24])))
        except IOError:
            self.request['error'] = 999
            self.request['errortext'] = 'could not get MAC address'
        self.request['INTERFACE_MAC'] = mac
        
        # Interface Type:
        try:
            type = interface
            if ('eth' in type): self.request['INTERFACE_TYPE'] = "Ethernet interface"
            if ('wlan' in type): self.request['INTERFACE_TYPE'] = "Wireless interface"
            if ('ppp' in type): self.request['INTERFACE_TYPE'] = "Dial-up interface"
            if ('tun' in type): self.request['INTERFACE_TYPE'] = "Routed IP tunnel"
            if ('sit' in type): self.request['INTERFACE_TYPE'] = "IPv6 tunnel"
            if ('tap' in type): self.request['INTERFACE_TYPE'] = "VPN tunnel"
            if ('lo' in type): self.request['INTERFACE_TYPE'] = "Loopback interface"
            else:
                self.request['INTERFACE_TYPE'] = "Unspecified interface"
        except Error:
            self.request['error'] = 999
            self.request['errortext'] = 'unknown interface type'
            Error
        
        
        
        #--------------------OLD-------------------------
        
        
        
        # TODO: get rid of this popen! ONLY MTU is dependingself.request[' on this
        intinfo = popen('ifconfig ' + interface).read()
        
        
        ## Properties Information:
        
        # find information on Receive Rate Old:
        try:
            intcaprx = re.search("++++++:(.*)", intinfo)
            if intcaprx != None:
                intcaprx = intcaprx.group()
                self.request['INTERFACE_CAPACITY_RX'] = intcaprx
        except Error:
            self.request['error'] = 999
            self.request['errortext'] = 'no IP for given Interface'
            raise Error


        # find information Transmission Rate Old:
        try:
            intcaptx = re.search("++++++:(.*)", intinfo)
            if intcaptx != None:
                intcaptx = intcaptx.group()
                self.request['INTERFACE_CAPACITY_TX'] = intcaptx
        except Error:
            self.request['error'] = 999
            self.request['errortext'] = 'no IP for given Interface'
            raise Error


        # MTU Old:
        try:
            mtu = re.search("MTU:(.*)", intinfo)
            if mtu != None:
                mtu = mtu.group()
                self.request['INTERFACE_MTU'] = mtu.split()[0].split(':')[1]
        except Error:
            self.request['error'] = 999
            self.request['errortext'] = 'no IP for given Interface'
            raise Error




        
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
        
        # Gives the current Bandwidth usage RX and TX in bytes/s
        try:
        
            proc_net_dev = open("/proc/net/dev")
            lines = proc_net_dev.readlines()
            proc_net_dev.seek(0)
        
            iface = get_ip_for_interface(self.request['identifier1'])
        
            keys_dyn_data = ["bytes_in", "packets_in", "bytes_out", "packets_out" ]
            delim = "%s:" % (iface)
            if_numbers =  [ l.strip().strip(delim) for l in lines if delim in l ][0]
            iface_data = dict(zip(keys_dyn_data, [ int(if_numbers.split()[index]) for index in (0, 1, 8, 9)]))
            bw_in  = iface_data["bytes_in"]
            bw_out = iface_data["bytes_out"]

            time.sleep(1)

            proc_net_dev = open("/proc/net/dev")
            lines = proc_net_dev.readlines()
            
            if_numbers =  [ l.strip().strip(delim) for l in lines if delim in l ][0]
            iface_data = dict(zip(keys_dyn_data, [ int(if_numbers.split()[index]) for index in (0, 1, 8, 9)]))
            bw_in2  = iface_data["bytes_in"]
            bw_out2 = iface_data["bytes_out"]
            
            self.request['USED_BANDWIDTH_RX'] = bw_in2 - bw_in
            self.request['USED_BANDWIDTH_TX'] = bw_out2 - bw_out
        
        except Error:
            self.request['error'] = 999
            self.request['errortext'] = 'could not calculate current RT and TX'            
            raise Error
        # Debugger

        self.logger.debug('Got this Interface Data: %s', iface_data)
        self.logger.debug('Current RX is: %s', bw_in)
        self.logger.debug('Current TX is: %s', bw_out)

        self.logger.debug('The result is: %s', self.request)
        
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
        
        interface = get_ip_for_interface(self.request['identifier1'])

        wlaninfo = popen('iwconfig ' + interface).read()
        if len(wlaninfo) != 0:
            
            essid = re.search('ESSID:([^ ]+)', wlaninfo)
            if essid != None:
                essid = essid.group()
                self.request['WLAN_ESSID'] = essid.split(":")[1]

            # Wireless Mode:
            try: 
                mode = re.search('Mode:([^ ]+)', wlaninfo)
                if mode != None:
                    mode = mode.group()
                    self.request['WLAN_MODE'] = mode.split(':')[1]
            except Error:
                self.request['error'] = 999
                self.request['errortext'] = 'could not get wireless mode'
                raise Error
                    
            # Access Point MAC Address:
            try:
                apmac = re.search('Access Point: ([^ ]+)', wlaninfo)
                if apmac != None:
                    apmac = apmac.group()
                    self.request['WLAN_AP_MAC'] = apmac.split()[2]
            except Error:
                self.request['error'] = 999
                self.request['errortext'] = 'could not get AP_MAC address'
                raise Error        
            

            # Link quality:
            try:
                link = re.search('Link Quality=([^ ]+)', wlaninfo)
                if link != None:
                    link = link.group()
                    self.request['WLAN_LINK'] = link.split()[1].split("=")[1]
            except Error:
                self.request['error'] = 999
                self.request['errortext'] = 'Could not get Link Quality'
                raise Error

            # Signal Level:
            try:
                signal = re.search('Signal level:([^ ]+)', wlaninfo)
                if signal != None:
                    signal = signal.group()
                    self.request['WLAN_SIGNAL'] = signal.split(':')[1]
            except Error:
                self.request['error'] = 999
                self.request['errortext'] = 'could not get Signal Level'
                raise Error

            # Noise Level:
            try:
                noise = re.search('Noise level=([^ ]+)', wlaninfo)
                if noise != None:
                    noise = noise.group()
                    self.request['WLAN_NOISE'] = noise.split('=')[1]
            except Error:
                self.request['error'] = 999
                self.request['errortext'] = 'could not get Noise Level'
                raise Error

            # given in dB by Ratio = 10*lg(Signal/Noise)
            try:
                self.request['WLAN_SIGNOISE_RATIO'] = 10 * math.log10((int(self.request['WLAN_SIGNAL']) / int(self.request['WLAN_NOISE'])))         
            except Error:
                self.request['error'] = 999
                self.request['errortext'] = 'could not get S/N Ratio'
                raise Error
            
            # Used Wireless Channel:
            try:
                chaninfo = popen("iwlist " + interface + " channel").read()
                channel = re.search('Channel ([^ ]+)', chaninfo)
                if channel != None:
                    channel = channel.group()
                    self.request['WLAN_CHANNEL'] = channel.split()[1]
            except Error:
                self.request['error'] = 999
                self.request['errortext'] = 'could not get wireless channel'
                raise Error


            # Wireless Frequency:
            try:
                freq = re.search('Frequency=([^ ]+)', wlaninfo)
                if freq != None:
                    freq = freq.group()
                    self.request['WLAN_FREQUENCY'] = freq.split('=')[1]
            except Error:
                self.request['error'] = 999
                self.request['errortext'] = '**************'
                raise Error

            # Wireless information for the debugger
        self.logger.debug('The result is: %s', self.request)

        self.request['error'] = 0
        self.request['errortext'] = 'Measurement successful'
        