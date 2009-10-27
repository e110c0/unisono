/**
 * send.h
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
#ifndef SEND_H_
#define SEND_H_
#include <arpa/inet.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#include "mconstants.h"

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
int send_train(int train_length, int train_id, int packet_size, int sock_udp, int spacing);

/**
 * send a packet fleet
 */
int send_fleet(int train_count, int train_length, int packet_size, int sock_udp, int spacing);

#endif /*SEND_H_*/
