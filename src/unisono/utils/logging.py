'''
logging.py

 Created on: Mar 25, 2009
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
import sys
from unisono.utils import configuration


try:
    loglevel = configuration.config.get('Logging', 'level')
    loglevel = getattr(logging,loglevel.upper())
except:
    loglevel = logging.INFO
try:
    logfile = configuration.config.get('Logging', 'file')
except:
    logfile = sys.stdout
logging.basicConfig(level=loglevel,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=logfile,
                    filemode='w+')
logging.info('UNISONO logging started')