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
import unittest
from unisono.mmplugins.nic_resources import NicReader
from unisono.mmplugins.nic_resources import BandwidthUsage
from unisono.mmplugins.nic_resources import WifiReader



class NicTest(unittest.TestCase):                            
    
    ### TESTING MODULES FOR RUN ERRORS
    # Case where the input IP doesn't match with any Interface.
    def NoInterfaceNICReader(self):                           
        nicreader = NicReader(None, None)
        nicreader.request = {'identifier1':'Nonsense bla bla'}
        nicreader.measure()
        pass

    def NoInterfaceBWReader(self):                           
        bwreader = BandwidthUsage(None, None)
        bwreader.request = {'identifier1':'Nonsense bla bla'}
        bwreader.measure()
        pass

    def NoInterfaceWIFIReader(self):                           
        wifireader = WifiReader(None, None)
        wifireader.request = {'identifier1':'Nonsense bla bla'}
        wifireader.measure()
        pass

    # Case where the input IP matches with Loopback Interface.
    def loInterfaceNICReader(self):                           
        nicreader = NicReader(None, None)
        nicreader.request = {'identifier1':'127.0.0.1'}
        nicreader.measure()
        pass

    def loInterfaceBWReader(self):                           
        bwreader = BandwidthUsage(None, None)
        bwreader.request = {'identifier1':'127.0.0.1'}
        bwreader.measure()
        pass

    def loInterfaceWIFIReader(self):                           
        wifireader = WifiReader(None, None)
        wifireader.request = {'identifier1':'127.0.0.1'}
        wifireader.measure()
        pass

    
    
    
    ### TESTING MODULES FOR CORRECT MEASUREMENTS
    
    # Case when we have a common network interface
    def ethdevice(self):
        pass
        #TODO:

    # Case when we have a wireless network interface
    def wlandevice(self):
        pass
        #TODO



def suite():
    suite = unittest.TestSuite()
    suite.addTest(NicTest("nonexistingnic"))
    suite.addTest(NicTest("loopdevice"))
    suite.addTest(NicTest("ethdevice"))
    suite.addTest(NicTest("wlandevice"))

    return suite
