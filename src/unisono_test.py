#!/usr/bin/env python3.0
# encoding: utf-8
'''
unisono_test.py

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


# python lib imports
import unittest
# unisono imports
import unisono.test.connector_interface
import unisono.test.nic_resources
import unisono.test.order
import unisono.test.mission_control

# init testsuites
connector_interface_testsuite = unisono.test.connector_interface.suite()
order_testsuite = unisono.test.order.suite()
nic_resources_testsuite = unisono.test.nic_resources.suite()
mission_control_testsuite = unisono.test.mission_control.suite()

# join testsuites
alltests = unittest.TestSuite((
        connector_interface_testsuite,
        order_testsuite,
        nic_resources_testsuite
#        mission_control_testsuite
        ))

# init testrunner as textbased runner
runner = unittest.TextTestRunner()

# run tests
runner.run(alltests)
