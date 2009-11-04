'''
dataitem.py

 Created on: Oct 29th, 2009
 Authors: dh
 
 $LastChangedBy: dh $
 $LastChangedDate: 2009-10-27 15:26:13 +0100 (Tue, 27 Oct 2009) $
 $Revision: 1968 $
 
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
import logging

logger = logging.getLogger(__file__)

class DataItem:
    '''
    data item object to hold local and remote cache time, number of identifiers 
    to be used to store result
    '''
    def __init__(self, name, idcount = 0, localctime=0, remotectime=0):
        self.idcount = idcount
        self.diname = name
        self.localctime = localctime
        self.remotectime = remotectime

    @property
    def name(self):
        return self.diname

    @property
    def identifier_count(self):
        return self.idcount

    @property
    def local_cache_time(self):
        return self.localctime

    @property
    def remote_cache_time(self):
        return self.remotectime
		
    def __repr__(self):
        return "%s(%i,%i,%i)"%(self.diname,self.idcount,self.localctime,self.remotectime)

