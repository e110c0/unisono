/**
 * send.c
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
#include "send.h"

/**
 * send a packet train
 *
 * \param train_length length of the packet train_id
 * \param train_id id of the packet train_id
 * \param packet_size packet size for the packet train
 * \param sock_udp socket file descriptor
 * \param spacing time between 2 packets in microseconds
 *
 * \return int status code
 */
int send_train(int train_length, int32_t train_id, int packet_size, int sock_udp, int spacing){
  char *pack_buf ;
  int32_t train_id_n ;
  int32_t pack_id , pack_id_n ;
  int i ;

  packet_size = (max_packet_size > packet_size) ? packet_size : max_packet_size;
  if ( (pack_buf = malloc(max_packet_size*sizeof(char)) ) == NULL ){
    return(-1);
  }
  train_id_n = htonl(train_id) ;
  memcpy(pack_buf, &train_id_n, sizeof(int32_t));
  
  srandom(getpid()); /* Create random payload; does it matter? */
  for (i=2*sizeof(int32_t); i<max_packet_size-1; i++){
    pack_buf[i]=(char)(random()&0x000000ff);
  }

  for (pack_id=0; pack_id < train_length;){
    pack_id_n = htonl(pack_id++);
    memcpy(pack_buf+sizeof(int32_t), &pack_id_n, sizeof(int32_t));
    send(sock_udp, pack_buf, packet_size,0 ) ;
    usleep(spacing);
  }
  pack_id_n = htonl(pack_id);
  memcpy(pack_buf+sizeof(int32_t), &pack_id_n, sizeof(int32_t));
  send(sock_udp, pack_buf, packet_size,0 ) ;

  free(pack_buf);
  return 0 ;
}

/**
 * send a packet fleet
 */
int send_fleet(){
  return 0;
}
