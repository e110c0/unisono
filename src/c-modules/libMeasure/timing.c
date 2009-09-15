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

#include "timing.h"

/**
 * minimal time the system can sleep un usec
 *
 * return int sleeptime in usec
 */
int min_sleep_usec() {
	return -1;
}

/**
 * latency for receiving packets from the network
 *
 * return int sleeptime in usec
 */
int32_t recv_latency(int sock_udp, int port) {
	struct sockaddr_in rcv;
	char *random_data;
	float min_OSdelta[50], ord_min_OSdelta[50];
	int j;
	struct timeval current_time, first_time;

	if ((random_data = malloc(max_packet_size * sizeof(char))) == NULL) {
		return -1;
	}
	srandom(getpid()); /* Create random payload; does it matter? */
	for (j = 0; j < max_packet_size - 1; j++)
		random_data[j] = (char) (random() & 0x000000ff);

	bzero((char *) &rcv, sizeof(rcv));
	rcv.sin_family = AF_INET;
	rcv.sin_addr.s_addr = INADDR_ANY;
	rcv.sin_port = htons(port);
	for (j = 0; j < 50; j++) {
		if (sendto(sock_udp, random_data, max_packet_size, 0,
				(struct sockaddr*) &rcv, sizeof(rcv)) == -1) {
			return -1;
		}
		gettimeofday(&first_time, NULL);
		recvfrom(sock_udp, random_data, max_packet_size, 0, NULL, NULL);
		gettimeofday(&current_time, NULL);
		min_OSdelta[j] = timeval_delta(first_time, current_time);
	}
	/* Use median  of measured latencies to avoid outliers */

	order_float(min_OSdelta, ord_min_OSdelta, 50);
	free(random_data);
	return ((int32_t)(ord_min_OSdelta[24] + ord_min_OSdelta[25]) / 2);

}

/**
 * latency for sending packets from the network
 *
 * return int sleeptime in usec
 */
int32_t send_latency() {
	char *pack_buf;
	float min_OSdelta[50], ord_min_OSdelta[50];
	int i, len;
	int sock_udp;
	struct timeval first_time, current_time;
	struct sockaddr_in snd_udp_addr, rcv_udp_addr;

	if (max_packet_size == 0 || (pack_buf = malloc(max_packet_size
			* sizeof(char))) == NULL) {
		return (-1);
	}
	if ((sock_udp = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
		return (-1);
	}
	bzero((char*) &snd_udp_addr, sizeof(snd_udp_addr));
	snd_udp_addr.sin_family = AF_INET;
	snd_udp_addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
	snd_udp_addr.sin_port = 0;
	if (bind(sock_udp, (struct sockaddr*) &snd_udp_addr, sizeof(snd_udp_addr))
			< 0) {
		return (-1);
	}

	len = sizeof(rcv_udp_addr);
	if (getsockname(sock_udp, (struct sockaddr *) &rcv_udp_addr,
			(socklen_t *) &len) < 0) {
		return (-1);
	}

	if (connect(sock_udp, (struct sockaddr *) &rcv_udp_addr,
			sizeof(rcv_udp_addr)) < 0) {
		return (-1);
	}
	srandom(getpid()); /* Create random payload; does it matter? */
	for (i = 0; i < max_packet_size - 1; i++)
		pack_buf[i] = (char) (random() & 0x000000ff);
	for (i = 0; i < 50; i++) {
		gettimeofday(&first_time, NULL);
		if (send(sock_udp, pack_buf, max_packet_size, 0) == -1)
			return -1;
		gettimeofday(&current_time, NULL);
		recv(sock_udp, pack_buf, max_packet_size, 0);
		min_OSdelta[i] = timeval_delta(first_time, current_time);
	}
	/* Use median  of measured latencies to avoid outliers */
	order_float(min_OSdelta, ord_min_OSdelta, 50);
	if (pack_buf != NULL)
		free(pack_buf);
	return (ord_min_OSdelta[25]);
}
