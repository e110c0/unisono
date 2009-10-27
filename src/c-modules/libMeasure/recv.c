/**
 * recv.c
 *
 *        Created on: Jul 27, 2009
 *           Authors: dh
 *
 *    $LastChangedBy$
 *  $LastChangedDate$
 *         $Revision$
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

void recv_train(int train_length, int train_id, int packet_size, int sock_udp, struct timeval *timestamps, int *result){
  char *pack_buf;

  struct timeval c_time, select_tv;
  fd_set readset;
  int rcvd = 0,
      exp_packet = 0,
      timeout = 5;
  int32_t c_packet = 0, 
          c_train_id = 0;

  *result = 0;
  packet_size = (max_packet_size > packet_size) ? packet_size : max_packet_size;

  if ( (pack_buf = malloc(packet_size*sizeof(char)) ) == NULL ){
    *result = -1;
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
                    timestamps[c_packet].tv_sec = c_time.tv_sec;
                    timestamps[c_packet].tv_usec = c_time.tv_usec;
                    if(c_packet == train_length-1) break;
              } else {
                if(train_id == c_train_id && c_packet+1 < train_length){
                    rcvd++;
                    exp_packet = c_packet+1;
                    *result = 1;
                }
                else if (c_train_id < train_id){
                    // drop old packets
// printf("(EE) drop old packets with train_id %d\n",c_train_id);
                }else{
                    // packets from further trains received ...
// printf("(EE) drop new packets with train_id %d\n",c_train_id);
//                     *result = 1;
                }
              }
              if (rcvd == train_length) break;
          }
        } else {
//           break;
        }
    } else {
      break;
    }
  } while(1);
//   if(*result != 0)  printf("train %d returns with result %d\n",train_id, *result);
  free(pack_buf);
}


/**
 * receive a packet fleet
 */
int recv_fleet(int train_count,
               int train_length,
               int packet_size,
               int sock_udp,
               struct timeval *timestamps){

// new code
    if(train_count < 1)
        return(-1);

//     int send_trains_latency = 1000; // time between trains
//     int *results; // result_array
//     results = malloc(train_count*sizeof(int)); // allocate memory for each train
    packet_size = (max_packet_size > packet_size) ? packet_size : max_packet_size;

    // counters
    int rcvd = 0,
        exp_packet = 0,
        train_id = 0;

    int loop_counter = 0;
    char *pack_buf; // packet buffer
    if ( (pack_buf = malloc(packet_size*sizeof(char)) ) == NULL ){
        //result = -1;
//         printf("tot durch speicher");
        return;
    }
    do{
        // bools
        int last_packet = 0;
        int last_train = 0;
        int max_packets = 0;

        loop_counter++;
        int32_t c_packet = 0 , c_train_id = 0;

        int result = 0;

        // code from recv_train
        struct timeval c_time, select_tv;
        fd_set readset;

        int timeout;
        if(rcvd == 0){
            // initial values for each train
            timeout = 5;
        }else{
            timeout = 1;
        }

        // receive a packet
        FD_ZERO(&readset);
        FD_SET(sock_udp,&readset);
        select_tv.tv_sec=timeout;
        select_tv.tv_usec=0;
        if (select(sock_udp+1,&readset,NULL,NULL,&select_tv) > 0 ){
            if (FD_ISSET(sock_udp,&readset) ){
                if (recvfrom(sock_udp, pack_buf, packet_size, 0, NULL, NULL) != -1){
                    gettimeofday ( &c_time, 0 );
                    memcpy(&c_train_id, pack_buf, sizeof(int32_t));
                    memcpy(&c_packet, pack_buf+sizeof(int32_t), sizeof(int32_t));
                    c_packet = ntohl(c_packet);
                    c_train_id = ntohl(c_train_id);
                    if (c_train_id == train_id && c_packet == exp_packet ){
// printf("(CC)c_train %d \ttrain %d \t c_pack %d \t exp_pack %d\n",c_train_id,train_id,c_packet,exp_packet);
                        rcvd++;
                        exp_packet++;
                        timestamps[train_id * train_length + c_packet].tv_sec = c_time.tv_sec;
                        timestamps[train_id * train_length + c_packet].tv_usec = c_time.tv_usec;
                    } else {
// printf("(EE)c_train %d \ttrain %d \t c_pack %d \t exp_pack %d\n",c_train_id,train_id,c_packet,exp_packet);
                        if(train_id == c_train_id && c_packet+1 < train_length){
                            rcvd++;
                            exp_packet = c_packet+1;
                            result = 1;
                        }
                        else if (c_train_id < train_id){
                            // drop old packets
//                             printf("(EE) drop old packets with train_id %d\n",c_train_id);
                            result = 2;
                        }else{
                            // packets from further trains received ...
//                             printf("(EE) drop new packets with train_id %d\n",c_train_id);
//                             *result = 1;
                            timestamps[c_train_id * train_length + c_packet].tv_sec = c_time.tv_sec;
                            timestamps[c_train_id * train_length + c_packet].tv_usec = c_time.tv_usec;
                            result = 3;
                        }
                    }

                }
            } else {
                break;
            }
        } else {
            break;
        }
    // check if we should abort
    if(c_packet == train_length-1) last_packet = 1;
    if (rcvd == train_length) max_packets = 1;
    if(train_id == train_count-1) last_train = 1;

    if(last_train){
        if(last_packet || max_packets){
            // abort as all trains are received
//             if(result != 0)  printf("train %d returns with result %d\n",train_id, result);
//             printf("abort after train %d and last_packet %d max_packets %d (%d loops)\n",train_id,last_packet,max_packets,loop_counter);
            break;
        }
    }

    if(result == 3){
//         if(result != 0)  printf("train %d returns with result %d\n",train_id, result);
        // packets from the future
        rcvd = 1;
        exp_packet = c_packet+1;
        train_id = c_train_id;
    }

    if(last_packet || max_packets){
        // set counters
        rcvd = 0;
        exp_packet = 0;
        train_id++;
//         if(result != 0)  printf("train %d returns with result %d\n",train_id, result);
    }

  }while(1);

/*
// old code

  if(train_count < 1)
    return(-1);
  int train_id; // the ids will be iterated
  int send_trains_latency = 1000; // time between trains
  int *results; // result_array

  results = malloc(train_count*sizeof(int)); // allocate memory for each train
  packet_size = (max_packet_size > packet_size) ? packet_size : max_packet_size;
  for(train_id=0; train_id < train_count; train_id++){
    recv_train(train_length,
                train_id,
                packet_size,
                sock_udp,
                &timestamps[train_id * train_length], // timestamp-pointer
                &results[train_id]);

    usleep(send_trains_latency);
  }while(train_id < train_count);
*/
  free(pack_buf);
  return 0;
}

int main(){

    struct timeval *timestamps;
    int train_count, train_length, packet_size, sock_udp;
    struct sockaddr_in server;

    sock_udp = socket(AF_INET, SOCK_DGRAM, 0);
    server.sin_family = AF_INET;
    server.sin_port = htons (43212);
    server.sin_addr.s_addr = htonl (INADDR_ANY);
    bind(sock_udp, (struct sockaddr*)&server, sizeof(server));

    train_count = 2;
    train_length = 45;
    packet_size = 1500;
    struct timeval def_tv;
    def_tv.tv_sec = 12345;
    def_tv.tv_sec = 54321;
    timestamps = (struct timeval*) malloc(train_count*train_length*sizeof(struct timeval));
    int i, j;
    for(i=0; i < train_count; i++){
        for(j=0; j < train_length; j++){
//             timestamps[i][j].tv_sec = 1;
            memcpy(timestamps+i*j*sizeof(struct timeval),&def_tv,sizeof(struct timeval));
        }
    }
/*
    for(i=0; i < train_count; i++){
        for(j=0; j < train_length; j++){
            struct timeval c_tv;
            memcpy(&c_tv,timestamps+i*j*sizeof(struct timeval),sizeof(struct timeval));
            printf("ts results %d %d\n",(int)c_tv.tv_sec, (int)c_tv.tv_usec);
        }
    }
*/
    recv_fleet(train_count,train_length,packet_size,sock_udp,timestamps);
    return 0;
}
