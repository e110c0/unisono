'''
file_name

 Created on: May 11, 2009
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
from queue import Queue
from unisono import connector_interface

## connector map
class TestConnectorMap(unittest.TestCase):
    ''' Test the connector map '''
    def setUp(self):
        self.q = Queue()

    def testInitInvalidQueue(self):
        ''' The connector map needs to have a queue to issue events. 
            Check what happens for an invalid queue'''
#        self.assertRaises(connector_interface.InvalidTypeError,
#                          connector_interface.ConnectorMap(),None,None)
        pass

    def testInitValidQueue(self):
        ''' The connector map needs to have a queue to issue events. 
            Check what happens for an valid queue'''
        #self.assertRaises(connector_interface.InvalidTypeError,connector_interface.ConnectorMap(),None,None)
        pass

    def testRegisterConnectorInvalidPort(self):
        '''
        The connector map stores connectors by its ip and port.
        Check for invalid port input
        '''
        conmap = connector_interface.ConnectorMap(self.q)
        self.assertRaises(connector_interface.OutOfRangeError, 
                          conmap.register_connector, "127.0.0.1", 65536)
        self.assertRaises(connector_interface.OutOfRangeError, 
                          conmap.register_connector, "127.0.0.1", 0)
        self.assertRaises(connector_interface.OutOfRangeError, 
                          conmap.register_connector, "127.0.0.1", -1)
        self.assertRaises(connector_interface.InvalidTypeError, 
                          conmap.register_connector, "127.0.0.1", 42.42)
        pass

    def testRegisterConnectorInvalidIP(self):
        '''
        The connector map stores connectors by its ip and port.
        Check for invalid IP input
        '''
        conmap = connector_interface.ConnectorMap(self.q)
        self.assertRaises(connector_interface.InvalidTypeError, 
                          conmap.register_connector, "somestuff", 42000)
        self.assertRaises(connector_interface.InvalidTypeError, 
                          conmap.register_connector, "123.345.789.012", 42000)
        pass

    def testRegisterConnectorValidPort(self):
        '''
        The connector map stores connectors by its ip and port.
        Check for Valid port input
        '''
        pass

    def testRegisterConnectorValidIP(self):
        '''
        The connector map stores connectors by its ip and port.
        Check for valid IP input (v4 and v6)
        '''
        pass
    
    def testUnregisterConnectorInvalidID(self):
        '''
        The connector map creates UUIDs for the connectors.
        Check for invalid ID input
        '''
        pass

    def testUnregisterConnectorValidID(self):
        '''
        The connector map creates UUIDs for the connectors.
        Check for valid ID input
        '''
        pass

    def testRegisterConnectorReturn(self):
        '''
        The connector map creates UUIDs for the connectors.
        Check for valid return type
        '''
        pass
    
    def testRegisterConnectorMultipleRegistrations(self):
        '''
        The connector map must be able to handle several registrations of 
        different connectors.
        Check whether it holds the correct data after registration
        '''
        pass

    def testRegisterConnectorMultipleSimilarRegistrations(self):
        '''
        The connector map must be able to handle several registrations of 
        the same connector.
        Check whether it holds the correct data after registration and whether
        it returns the correct ID
        '''
        pass


## connector functions
class TestConnectorFunctions(unittest.TestCase):
    ''' Test the connectir functions '''
    def testRegisterConnectorPortTooLarge(self):
        '''The input portnumber must be below 65536'''
        result = connector_interface.ConnectorFunctions.register_connector(None, 65536)
        self.assertEqual(result, 2)
        
    def testRegisterConnectorPortNotPositive(self):
        '''The input portnumber must be a positive number'''
        result = connector_interface.ConnectorFunctions.register_connector(None, 0)
        self.assertEqual(result, 2)
        result = connector_interface.ConnectorFunctions.register_connector(None, -1)
        self.assertEqual(result, 2)

    def testRegisterConnectorPortInvalidType(self):
        ''' The input portnumber must be an integer'''
        result = connector_interface.ConnectorFunctions.register_connector(None, 42.42)
        self.assertEqual(result, 1)

    def testUnregisterConnectorIDInvalidType(self):
        '''The input must be a valid UUID'''
        result = connector_interface.ConnectorFunctions.unregister_connector(None, "somestuff")
        self.assertEqual(result, 1)


def suite():
    suite = unittest.TestSuite()
    # connectorMap
    suite.addTest(TestConnectorMap("testInitInvalidQueue"))
    suite.addTest(TestConnectorMap("testInitValidQueue"))
    suite.addTest(TestConnectorMap("testRegisterConnectorInvalidPort"))
    suite.addTest(TestConnectorMap("testRegisterConnectorInvalidIP"))
    suite.addTest(TestConnectorMap("testRegisterConnectorValidPort"))
    suite.addTest(TestConnectorMap("testRegisterConnectorValidIP"))
    suite.addTest(TestConnectorMap("testUnregisterConnectorInvalidID"))
    suite.addTest(TestConnectorMap("testUnregisterConnectorValidID"))
    suite.addTest(TestConnectorMap("testRegisterConnectorReturn"))
    suite.addTest(TestConnectorMap("testRegisterConnectorMultipleRegistrations"))
    suite.addTest(TestConnectorMap("testRegisterConnectorMultipleSimilarRegistrations"))
    # connector_functions
    suite.addTest(TestConnectorFunctions("testRegisterConnectorPortTooLarge"))
    suite.addTest(TestConnectorFunctions("testRegisterConnectorPortNotPositive"))
    suite.addTest(TestConnectorFunctions("testRegisterConnectorPortInvalidType"))
    suite.addTest(TestConnectorFunctions("testUnregisterConnectorIDInvalidType"))
    return suite

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()