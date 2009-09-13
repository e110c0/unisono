/**
 * recv.c
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
#include "recv.h"
/**
 * receive a packet train
 */

int recv_train(int train_length, int train_id, int packet_size, int sock_udp, struct timeval *timestamps){
  char *pack_buf;

  struct timeval c_time, select_tv;
  fd_set readset;
  int rcvd = 0,
      badtrain = 0,
      exp_packet = 0,
      timeout = 5;
  int32_t c_packet, c_train_id;

  packet_size = (max_packet_size > packet_size) ? packet_size : max_packet_size;

  if ( (pack_buf = malloc(packet_size*sizeof(char)) ) == NULL ){
    return(-1);
  }

  do{
    FD_ZERO(&readset);
    FD_SET(sock_udp,&readset);
    select_tv.tv_sec=timeout;
    select_tv.tv_usec=0;
    timeout = 1;
    if (select(sock_udp+1,&readset,NULL,NULL,&select_tv) > 0 ){
        if (FD_ISSET(sock_udp,&readset) ){
          if (recvfrom(sock_udp, pack_buf, packet_size, 0, NULL, NULL) != -1){
              gettimeofday ( &c_time, 0 );
              memcpy(&c_train_id, pack_buf, sizeof(int32_t));
              memcpy(&c_packet, pack_buf+sizeof(int32_t), sizeof(int32_t));
              c_packet = ntohl(c_packet);
              c_train_id = ntohl(c_train_id);
              if (c_train_id == train_id && c_packet == exp_packet ){
                  rcvd++;
                  exp_packet++;
                  timestamps[c_packet] = c_time;
                  if (rcvd == train_length) break;
              } else {
                badtrain = 1;
              }
          }
        } else {
//           break;
        }
    } else {
      break;
    }
  } while(1);

  return badtrain;
}

/**
 * receive a packet fleet
 */
int recv_fleet(){
  return 0;
}
