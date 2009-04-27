'''
configuration.py

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
import configparser
import os.path

__unisonoconfig = None

def init_configuration():
    global __unisonoconfig
    __unisonoconfig = configparser.SafeConfigParser()
    files = ['/etc/unisono.cfg', '~/.unisono.cfg', '../etc/unisono.cfg']
    foundany = 0
    for i in range(len(files)):
        try:
            __unisonoconfig.readfp(open(os.path.expanduser(files[i])))
            foundany = 1
            print("config file read: ", os.path.expanduser(files[i]))
        except:
            print('config file ', os.path.expanduser(files[i]), ' not found')
    if (foundany == 0):
        print('WARNING: no configuration found, using default values!')

def get_configparser():
    if __unisonoconfig == None:
        init_configuration()
    return __unisonoconfig

