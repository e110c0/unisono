'''
mission_control.py

 Created on: May 19, 2009
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

class MissionControl():
    '''
    MissionControl provides a global coordinator for modules that need to
    communicate with a correspondent measurement node to coordinate a measurement.
    '''


    def __init__(self,):
        '''
        Constructor
        '''

    def send(self, receiver, message):
        '''
        send() tries several different methods to deliver a message to the receiver:
        * try a connection via a connector. hopefully, the connector correspondent 
        to the current request allows this.
        * try connecting directly. This requires the correspondent node to be
         * reachable (no firewall, no NATs inbetween)
         * listening on the UNISONO mission control port
        * the UNISONO DHT (yet to be implemented)
        '''
        pass

    def receive(self):
        '''
        listen on all possible incoming ports and forward a message to the 
        correct module thread
        '''
        pass