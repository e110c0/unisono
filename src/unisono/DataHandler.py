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

import logging
from queue import Queue

class DataHandler:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    def __init__(self):
        self.resultq = Queue()
        self.plugins = {}
        self.dataitems = {}
        try:
            active_plugins = configparser.get('M&Ms','active_plugins')
        except:
            # TODO get all
            active_plugins = 'cvalues'
            pass
        for p in active_plugins.split(','):
            try:
                p = p.strip()
                mod = __import__('unisono.mmplugins', globals(), locals(), p)
            except:
                # FIXME: logging
                pass
            for n,v in vars(getattr(mod, p)).items():
                if type(v) == type and issubclass(v, mmtemplate):
                    self.logger.debug(':-)')
                    iq = Queue()
                    o = v(iq,self.resultq)
                    self.plugins[n]=o,iq
        self.logger.debug('plugin list: %r'%self.plugins)