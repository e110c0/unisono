/**
 * networkfunctions.h
 *
 *        Created on: Dec 11, 2008
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

/**
 *  network functions required by several M&Ms
 */

#ifndef NETWORKFUNCTIONS_H_
#define NETWORKFUNCTIONS_H_

#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <string.h>

int parse_addr_str(const char *node, struct sockaddr *addr,
		socklen_t *addrlen);

void set_port(struct sockaddr *addr, uint16_t port);

#endif /* NETWORKFUNCTIONS_H_ */
