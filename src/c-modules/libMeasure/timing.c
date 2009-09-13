/**
 * timing.c
 *
 *        Created on: Jul 27, 2009
 *           Authors: dh
 *
 *    $LastChangedBy: haage $
 *  $LastChangedDate: 2009-07-16 15:56:35 +0200 (Thu, 16 Jul 2009) $
 *         $Revision: 1526 $
 *
 * (C) 2008-2009 by Computer Networks and Internet, University of Tuebingen
 *
 * This file is part of UNISONO Unified Information Service for Overlay
 * Network Optimization.
 *
 * UNISONO is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * UNISONO is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with UNISONO.  If not, see <http://www.gnu.org/licenses/>.
 */

/**
 * minimal time the system can sleep un usec
 *
 * return int sleeptime in usec
 */
int min_sleep_usec(){
  return -1;
}

/**
 * latency for receiving packets from the network
 *
 * return int sleeptime in usec
 */
int recv_latency(){
  return -1;
}

/**
 * latency for sending packets from the network
 *
 * return int sleeptime in usec
 */
int send_latency(){
  return -1;
}