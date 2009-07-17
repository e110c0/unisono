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

import threading, logging, re, string, sys, fcntl, socket, time, math
from unisono.mmplugins import mmtemplates
from unisono.utils import configuration
from os import popen

def get_interfaces_for_ip(ip):
    
    try:
    # Returns the interface with the given IP, such as eth0, eth1, wlan1, etc.
        proc_net_dev = open("/proc/net/dev")
        lines = proc_net_dev.readlines()
        proc_net_dev.seek(0)
        iflist = [ l[:l.find(":")].strip() for l in lines if ":" in l ]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for iface in iflist:
            try:
                ifr = (iface + '\0'*32)[:32]
                ipinfo = fcntl.ioctl(s.fileno(), 0x8915, ifr)
                ipadd = socket.inet_ntoa(ipinfo[20:24])
                if ipadd in ip:
                    return iface
            except IOError:
                pass
    except IOError:
        pass
    
    # Get IP address for Interface
def get_ip_for_interface(iface):
    try:
        ifr = iface + '\0'*(32-len(iface))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ipinfo = fcntl.ioctl(s.fileno(), 0x8915, ifr)
        ip = socket.inet_ntoa(ipinfo[20:24])
        return ip
    except IOError:
        self.request['error'] = 501
        self.request['errortext'] = 'no Interface for given IP'
        pass


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
        
        self.request['errortext'] = ''
        
        try:
            interface = get_interfaces_for_ip(self.request['identifier1'])
            if interface != None:
                interface = interface.strip()
            else:
                self.request['error'] = 500
                self.request['errortext'] = 'could not find interface with IP, aborting measurement'
                return
        except IOError:
            return
            raise IOError
                          
        # Opening measurement socket
        try:
            tsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except IOError:
            pass
        #--------------------NEW-------------------------
        
        # MAC Address: 
        iface = interface + '\0'*(32-len(interface))
        try:
            info = fcntl.ioctl(tsoc.fileno(), 0x8927, iface)
            mac = (':'.join(map(lambda n: "%02x" % n, info[18:24])))
        except IOError:
            self.request['error'] = 502
            self.request['errortext'] = 'could not get MAC address'
        self.request['INTERFACE_MAC'] = mac
        
        # Interface Type:
        try:
            type = interface
            if ('eth' in type): self.request['INTERFACE_TYPE'] = "Ethernet interface"
            else: 
                if (('wla' or 'ath') in type): self.request['INTERFACE_TYPE'] = "Wireless interface"
                else: 
                    if ('ppp' in type): self.request['INTERFACE_TYPE'] = "Dial-up interface"
                    else: 
                        if ('tun' in type): self.request['INTERFACE_TYPE'] = "Routed IP tunnel"
                        else: 
                            if ('sit' in type): self.request['INTERFACE_TYPE'] = "IPv6 tunnel"
                            else: 
                                if ('tap' in type): self.request['INTERFACE_TYPE'] = "VPN tunnel"
                                else: 
                                    if ('lo' in type): self.request['INTERFACE_TYPE'] = "Loopback interface"
                                    else:
                                        self.request['INTERFACE_TYPE'] = "Unspecified interface"
        except IOError:
            self.request['error'] = 503
            self.request['errortext'] = 'unknown interface type'
            IOError

        
        
        
        #--------------------OLD-------------------------
        
        
        
        # TODO: get rid of this popen! ONLY MTU is dependingself.request[' on this
        intinfo = popen('ifconfig ' + interface).read()
        
        
        ## Properties Information:
        
        # find information on Receive Rate Old:
#        try:
#            intcaprx = re.search("++++++:(.*)", intinfo)
#            if intcaprx != None:
#                intcaprx = intcaprx.group()
#                self.request['INTERFACE_CAPACITY_RX'] = intcaprx
#        except IOError:
#            self.request['error'] = 999
#            self.request['errortext'] = 'no IP for given Interface'
#            pass
#
#
#        # find information Transmission Rate Old:
#        try:
#            intcaptx = re.search("++++++:(.*)", intinfo)
#            if intcaptx != None:
#                intcaptx = intcaptx.group()
#                self.request['INTERFACE_CAPACITY_TX'] = intcaptx
#        except IOError:
#            self.request['error'] = 999
#            self.request['errortext'] = 'no IP for given Interface'
#            pass


        # MTU Old:
        try:
            mtu = re.search("MTU:(.*)", intinfo)
            if mtu != None:
                mtu = mtu.group()
                self.request['INTERFACE_MTU'] = mtu.split()[0].split(':')[1]
        except IOError:
            self.request['error'] = 504
            self.request['errortext'] = 'could not measure MTU'
            pass




        
        self.request["error"] = 0
        if self.request['errortext'] == '':
            self.request['errortext'] = 'Measurement successful'

        #Interface Information for the debugger
        self.logger.debug('The result is: %s', self.request)

class BandwidthUsage(mmtemplates.MMTemplate):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
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
        self.request["errortext"] = ''
        
        try:
            interface = get_interfaces_for_ip(self.request['identifier1'])
            if interface != None:
                interface = interface.strip()
            else:
                self.request['error'] = 500
                self.request['errortext'] = 'could not find interface with IP, aborting measurement'
                return        
        except IOError:
            self.request['error'] = 500
            self.request['errortext'] = 'could not find interface with IP, aborting measurement'
            raise IOError
            return
            
        
        try:
            
            bw_in = None
            bw_out = None
        
            proc_net_dev = open("/proc/net/dev")
            lines = proc_net_dev.readlines()
            proc_net_dev.seek(0)
            
            if interface != None:        
                keys_dyn_data = ["bytes_in", "packets_in", "bytes_out", "packets_out" ]
                delim = "%s:" % (interface)
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
                
                self.request["error"] = 0
                if self.request['errortext'] == '':
                    self.request['errortext'] = 'Measurement successful'
                
                try:
                    self.request['USED_BANDWIDTH_RX'] = bw_in2 - bw_in
                    self.request['USED_BANDWIDTH_TX'] = bw_out2 - bw_out
                except UnboundLocalError:
                    self.request['error'] = 510
                    self.request['errortext'] = 'could not calculate current RT and TX'
                    raise UnboundLocalError
                    return            

        except IOError:
            self.request['error'] = 510
            self.request['errortext'] = 'could not calculate current RT and TX'
            raise UnboundLocalError            
            pass
        # Debugger

        self.logger.debug('Current RX is: %s', bw_in)
        self.logger.debug('Current TX is: %s', bw_out)

        self.logger.debug('The result is: %s', self.request)
        

class WifiReader(mmtemplates.MMTemplate):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
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
 
        self.request['errortext'] = ''
 
        try:
            interface = get_interfaces_for_ip(self.request['identifier1'])
            if interface != None:
                interface = interface.strip()
            else:
                self.request['error'] = 500
                self.request['errortext'] = 'could not find interface with IP, aborting measurement'
                return        
        except IOError:
            self.request['error'] = 500
            self.request['errortext'] = 'could not find interface with IP, aborting measurement'
            raise IOError
            return

            
        wlaninfo = ''

        if interface != None:
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
            except IOError:
                self.request['error'] = 520
                self.request['errortext'] = 'could not get wireless mode'
                pass
                    
            # Access Point MAC Address:
            try:
                apmac = re.search('Access Point: ([^ ]+)', wlaninfo)
                if apmac != None:
                    apmac = apmac.group()
                    self.request['WLAN_AP_MAC'] = apmac.split()[2]
            except IOError:
                self.request['error'] = 521
                self.request['errortext'] = 'could not get AP_MAC address'
                pass        
            

            # Link quality:
            try:
                link = re.search('Link Quality=([^ ]+)', wlaninfo)
                if link != None:
                    link = link.group()
                    self.request['WLAN_LINK'] = link.split()[1].split("=")[1]
            except IOError:
                self.request['error'] = 522
                self.request['errortext'] = 'Could not get Link Quality'
                pass

            # Signal Level:
            try:
                signal = re.search('Signal level:([^ ]+)', wlaninfo)
                if signal != None:
                    signal = signal.group()
                    self.request['WLAN_SIGNAL'] = signal.split(':')[1]
            except IOError:
                self.request['error'] = 523
                self.request['errortext'] = 'could not get Signal Level'
                pass

            # Noise Level:
            try:
                noise = re.search('Noise level=([^ ]+)', wlaninfo)
                if noise != None:
                    noise = noise.group()
                    self.request['WLAN_NOISE'] = noise.split('=')[1]
            except IOError:
                self.request['error'] = 524
                self.request['errortext'] = 'could not get Noise Level'
                pass

            # given in dB by Ratio = 10*lg(Signal/Noise)
            try:
                self.request['WLAN_SIGNOISE_RATIO'] = 10 * math.log10((int(self.request['WLAN_SIGNAL']) / int(self.request['WLAN_NOISE'])))         
            except IOError:
                self.request['error'] = 525
                self.request['errortext'] = 'could not get S/N Ratio'
                pass
            
            # Used Wireless Channel:
            try:
                chaninfo = popen("iwlist " + interface + " channel").read()
                channel = re.search('Current Frequency=', chaninfo)
                if channel != None:
                    channel = channel.group()
                    self.request['WLAN_CHANNEL'] = channel.split()[1]
            except IOError:
                self.request['error'] = 526
                self.request['errortext'] = 'could not get wireless channel'
                pass


            # Wireless Frequency:
            try:
                freq = re.search('Frequency=([^ ]+)', wlaninfo)
                if freq != None:
                    freq = freq.group()
                    self.request['WLAN_FREQUENCY'] = freq.split('=')[1]
            except IOError:
                self.request['error'] = 527
                self.request['errortext'] = 'could not get frequency'
                pass
            
            self.request['error'] = 0
            if self.request['errortext'] == '':
                self.request['errortext'] = 'Measurement successful'

            
            
        else:
            self.request['error'] = 530
            self.request['errortext'] = 'This is not a Wireless Interface'

            

            # Wireless information for the debugger
        self.logger.debug('The result is: %s', self.request)

        