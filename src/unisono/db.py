'''
db.py

 Created on: Jun 18, 2009
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

import logging
import sqlite3

class NotInCacheError(Exception):
    pass

class InvalidTableLayout(Exception):
    pass

class DataBase():
    '''
    DataBase class for unisono caching
    
    This class provides a generic interface for all caching purposes.
    The database is created in memory. 
    '''
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    def __init__(self):
        '''
        Constructor
        '''
        self.dbcon = sqlite3.connect(":memory:")
        self.dbcursor = self.dbcon.cursor()
        self.create_table('RTT', 2, 'INT')
        self.purge('RTT', 2132135)

    def create_table(self, name, idcount, valuetype):
        '''
        Create a new table in the cache
        
        For each data item, the cache holds its own table. The table is named 
        after the data item (e.g. RTT for RTT data items)
        
        @param name table name as string
        @param idcount number of identifiers required for this data item. Must
                       be >0
        @param valuetype the type of the result values as string. Must be one of
                         TEXT, INT, REAL
        '''
        command = "create table " + name + "("
        if idcount < 1:
            raise InvalidTableLayout()
        if valuetype not in ['Text', 'INT', 'REAL']:
            raise InvalidTableLayout()
        for i in range(idcount):
            command = command + "identifier" + str(i) + " TEXT,"
        command = command + " time INT, value " + valuetype + ");"
        try:
            self.dbcursor.execute(command)
            self.dbcon.commit()
            self.logger.debug("table %s created ! ", name)
        except sqlite3.OperationalError:
            self.logger.info("table %s exists, skipping", name)

        
    def check_for(self, paramap):
        self.logger.debug('Checking db for %s', paramap)
        result = {}
        table = paramap['dataitem']
        identifier1 = paramap['identifier1']
        if 'identifier2' in paramap.keys():
            identifier2 = paramap['identifier2']
        else:
            identifier2 = None
        command = ""
        c = self.dbcon.cursor()
        c.execute(command)
        if paramap['dataitem'] == 'RTT':
            result[paramap['dataitem']] = 1234124
        else:
            raise NotInCacheError()
        return result

    def store(self, paramap):
        status = 0
        self.logger.debug('Storing %s', paramap)
        return status
    
    def purge(self, table, time):
        '''
        Purge all entries in a table upt to a specific time
        
        @param table table to be purged (string)
        @param time unix time stamp in seconds (int) 
        '''
        self.logger.debug('Purge table %s up to %s', table, time)
        c = self.dbcon.cursor()
        c.execute("delete from " + table + " where time < " + str(time) + ";")
        
        self.dbcon.commit()