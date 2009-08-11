'''
loadapp_config.py

 Created on: Jul 21, 2009
 Authors: korscheck (zxmmi77)

 $LastChangedBy: zxmmi77 $
 $LastChangedDate: 2009-07-24 16:49:33 +0200 (Fri, 24 Jul 2009) $
 $Revision: 1587 $

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

# Config file for loadapp.py

# directory path for dataitems.txt
DATAITEMS_PATH = '../doc/dataitems.txt'
RPC_URL = 'http://localhost:46000'

# scenarios for mass-orders
# format: dictionary where key is the name of the scenario (for combo-box output)
# and value is a list with a fixed amount of fields:
#   [exec_timestamp, name1, name2, dataitem, type, interval, lifetime, upper_threshold, lower_threshold]
# exec_timestamp is relative to starting time and to each other (in microseconds).
# if you have three orders with 1000, 2000, 3000 that means that order #1 is executed after 1 second,
# order #2 is executed after 2 seconds, order #3 is executed after 3 seconds etc.

SCENARIOS = {
'host_infos' : [
	[50, 'marty', '', 'INTERFACE_MAC', 'ONESHOT', 0, 0, 0, 0],
	[100, 'marty', '', 'INTERFACE_MTU', 'ONESHOT', 0, 0, 0, 0]
],

'connection_infos' : [
	[1000, 'marty', 'biff', 'RTT', 'PERIODIC', 10, 60, 0, 0],
	[2000, 'marty', 'biff', 'HOPCOUNT', 'ONESHOT', 0, 0, 0, 0],
	[3000, 'marty', 'biff', 'PATHMTU', 'ONESHOT', 0, 0, 0, 0]
]

}
