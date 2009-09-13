/**
 * networkfunctions.c
 *
 *        Created on: Dec 11, 2008
 *           Authors: alex, dh
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

#include "networkfunctions.h"

int parse_addr_str(const char *node, struct sockaddr *addr, socklen_t *addrlen) {
	int res;
	struct addrinfo hints;
	struct addrinfo *result;
	memset(&hints, 0, sizeof(hints));
	hints.ai_family = AF_UNSPEC;
	hints.ai_socktype = SOCK_DGRAM;
	hints.ai_protocol = 0;
	hints.ai_flags = AI_NUMERICHOST;
	res = getaddrinfo(node, 0, &hints, &result);
	if (res == 0) {
		memcpy(addr, result->ai_addr, result->ai_addrlen);
		*addrlen = result->ai_addrlen;
		freeaddrinfo(result);
	}
	return res;
}

void set_port(struct sockaddr *addr, uint16_t port) {
	if (addr->sa_family == AF_INET) {
		struct sockaddr_in *addr_p = (struct sockaddr_in*) (addr);
		addr_p->sin_port = port;
	} else if (addr->sa_family == AF_INET6) {
		struct sockaddr_in6 *addr_p = (struct sockaddr_in6*) (addr);
		addr_p->sin6_port = port;
	}
}

