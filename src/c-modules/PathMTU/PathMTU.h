/**
 *  CPathMTU.h
 *
 *        Created on:  01.03.09
 *           Authors: alex, dh
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

#ifndef PATHMTU_H_
#define PATHMTU_H_

//#include <iostream.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <errno.h>
#include <arpa/inet.h>

#include <linux/types.h>
#include <linux/errqueue.h>

#include "networkfunctions.h"

/* kernel knows this since 2.6.22 but glibc didn't include it until  08.08.2008
 (see glibc cvs libc/sysdeps/unix/sysv/linux/bits/in.h rev 1.20
 -> not in ubuntu 8.04 glibc */

#ifndef IP_PMTUDISC_PROBE
#define IP_PMTUDISC_PROBE  3	/* Ignore dst pmtu.  */
#endif

#ifndef IPV6_PMTUDISC_PROBE
#define IPV6_PMTUDISC_PROBE	3	/* Ignore dst pmtu.  */
#endif

const static unsigned int headerlen = 28;
const static unsigned int max_mtu = 65535;
const static unsigned int min_mtu = 576;
const static uint16_t base_port = 43201;
struct sockaddr *target;
socklen_t target_len;
unsigned int result_mtu;
int sockfd;

/* t_request struct is module specific and must be prepared by the python module */

struct t_request{
  char *identifier1;
  char *identifier2;
};

/* t_result is module specific and should represent the result dictionary as
 * it is expected from the python module. The generic python module will take
 * of the translation care*/
struct t_result{
  int PATHMTU;
  int HOPCOUNT;
  int error;
  char *errortext;
};

struct t_result result;

/*
 * do the actual measurement
 */
struct t_result measure(struct t_request req);

uint32_t get_error(unsigned int *new_mtu);

void data_wait();

uint32_t probe_mtu(unsigned int mtu, unsigned int *new_mtu);

int pmtu(void);

#endif /* PATHMTU_H_ */
