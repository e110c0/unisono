#!/usr/bin/env python3
'''
file_name

 Created on: Mar 23, 2009
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


if __name__ == '__main__':
    import xmlrpc.client
    s = xmlrpc.client.ServerProxy('http://localhost:45312')
    # Print list of available methods
    print("we do some stuff")
    print(s.system.listMethods())
    print(s.system.methodHelp('list_available_dataitems'))
    print(s.register_connector(312312,43222))
    print(s.list_available_dataitems())
