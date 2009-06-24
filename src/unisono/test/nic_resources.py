'''
nic_resources.py

 Created on: Jun 24, 2009
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
class NicTest(unittest.TestCase):                            
    
    # Case where the input IP doesn't match with any Interface.
    def nonexistingnic(self, NicReader):                           
        #identifier1 has to be an IP address                                          
        NicReader.measure(self.request['identifier1' : "Nonsense"])
        self.assertEqual(NicReader.dataitems['error'], "No interface with this IP")

    # Case when we have a loopback Interface
    def loopdevice(self, NicReader):
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
