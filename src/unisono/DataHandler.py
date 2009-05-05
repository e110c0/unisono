'''
DataHandler.py

 Created on: Apr 6, 2009
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

from unisono.utils import configuration
from unisono.mmplugins.mmtemplates import mmtemplate
from unisono import XMLRPCReplyHandler

import threading
import logging
from queue import Queue

class DataHandler:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    def __init__(self):
        # queue used for the results
        self.resultq = Queue()
        # queue used for incoming orders
        self.orderq = Queue()
        # list of registered plugins with their queue and object
        self.plugins = {}
        # list of datitems with the registered plugin and its cost
        self.dataitems = {}
        # initialize M&Ms
        config = configuration.get_configparser()
        try:
            active_plugins = config.get('M&Ms', 'active_plugins')
            self.logger.info('Loading plugins: %s', active_plugins)
        except:
            self.logger.info('No plugins configured, loading defaults.')
            # TODO get all available by default
            active_plugins = 'cvalues'
            pass
        for p in active_plugins.split(','):
            try:
                p = p.strip()
                mod = __import__('unisono.mmplugins', globals(), locals(), [p])
                mod = getattr(mod, p)
                self.logger.debug('Mod: %s', mod)
            except:
                self.logger.error('Could not load plugin %s', p)
            for n, v in vars(mod).items():
                if type(v) == type and issubclass(v, mmtemplate):
                    iq = Queue()
                    mm = v(iq, self.resultq)
                    self.plugins[n] = mm, iq
                    self.registerMM(mm)
                    mm_thread = threading.Thread(target=mm.run)
                    # Exit the server thread when the main thread terminates
                    mm_thread.setDaemon(True)
                    mm_thread.start()
                    self.logger.info("M&M %s loop running in thread: %s", mm.name, mm_thread.name)
        self.logger.debug('plugin list: %r' % self.plugins)
        self.logger.debug('registered dataitems: %s', self.dataitems)
    def run(self):
        ''' The main method of unisono
        '''
        self.plugins['cValues'][1].put({'dataitem':'max_shared_upstream_bandwidth'})
 
        self.unregisterAllMM()

    def registerMM(self, mm):
        di = mm.availableDataItems()
        cost = mm.getCost()
        self.logger.debug('Data items: %s', di)
        self.logger.debug('Cost: %s', cost)
        # merge with current dataitem list
        for i in di:
            # TODO: how to use the old it
            self.dataitems[i] = { mm, cost }
            
    def unregisterMM(self, mm):
        self.logger.debug('Unregistering %s', mm)
        di = mm.availableDataItems()
        for i in di:
            # TODO: only delete the correspondent entry
            del self.dataitems[i]

    def unregisterAllMM(self):
        for mm in self.plugins:
            
            self.unregisterMM(self.plugins[mm][0])
    
    def processOrder(self, order):
        # get requested dataitem
        # check data base
        # if not available, get module list
        # check if any module handles a similar order at the moment
        # if not, choose cheapest and send the order to the module
        
        pass
    def processResult(self):
        while (True):
            # wait for event
            self.logger.debug('waiting for a result')
            result = self.resultq.get()
            # read values
            self.logger.debug('got a result: %s', result)
            # TODO: save result in db/cache
            # send the result
            #XMLRPCReplyHandler.sendResult(result)
        
        
        
        
        
        