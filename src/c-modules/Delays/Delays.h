/**
 * Delays.h
 *
 *        Created on: Jul 27, 2008
 *           Authors: korscheck, dh
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

#ifndef CDELAY_H_
#define CDELAY_H_

#include <stdio.h>
#include <signal.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <netinet/ip6.h>
#include <netinet/icmp6.h>
#include <sys/time.h>
#include <stdbool.h>

#include "networkfunctions.h"
#include "mathfunctions.h"

/* t_request struct is module specific and must be prepared by the python module */

struct t_request {
	char *identifier1;
	char *identifier2;
};

/* t_result is module specific and should represent the result dictionary as
 * it is expected from the python module. The generic python module will take
 * of the translation care*/
struct t_result {
	int HOPCOUNT;
	int RTT;
	int RTT_MIN;
	int RTT_MAX;
	int RTT_DEVIATION;
	int RTT_JITTER;
	int OWD;
	int OWD_MIN;
	int OWD_MAX;
	int OWD_DEVIATION;
	int OWD_JITTER;
	int LOSSRATE;
	int error;
	char *errortext;
};

/* struct with all the variables we need for the calculations*/
struct t_mvars {
	int seqno;
	int received;
	int loss;
	int hopcount;
	int error;
	char* errortext;
};
/* *****************************************************************************
 * Constants
 * ****************************************************************************/
static const int DEFAULT_PACKETCOUNT = 10;
static const int DEFAULT_TIMEOUT = 5;
static const int FEWDATA_LIMIT = 2;


/*
 * do the actual measurement
 */
struct t_result measure(struct t_request req);

/*
 * for ipv6
 */
struct t_mvars measure_ipv6(int64_t delays[], int packetcount,
		struct sockaddr_in6 *addr);

/*
 * for ipv4
 */

struct t_mvars measure_ipv4(int64_t delays[], int packetcount,
		struct sockaddr_in *addr);

// helpers
/**
 * Calculates the checksum of the constructed ICMP-packet.
 * @param b Buffer
 * @param len Size of the packet
 * @return Checksum of the packetheader
 */
u_short checksum(void *b, int len);

#endif /* CDELAY_H_ */
