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
from unisono import connector_interface

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
    suite.addTest(TestConnectorFunctions("testRegisterConnectorPortTooLarge"))
    suite.addTest(TestConnectorFunctions("testRegisterConnectorPortNotPositive"))
    suite.addTest(TestConnectorFunctions("testRegisterConnectorPortInvalidType"))
    suite.addTest(TestConnectorFunctions("testUnregisterConnectorIDInvalidType"))
    return suite

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()