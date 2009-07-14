/**
 * Delays.c
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

#include "Delays.h"

/* read hopcount from ancillary msg */
int read_hops(struct msghdr *msg) {
	struct cmsghdr *c;
	int hops = 0;

	for (c = CMSG_FIRSTHDR(msg); c != NULL; c = CMSG_NXTHDR(msg, c)) {
		if (c->cmsg_level != SOL_IPV6)
			continue;
		switch(c->cmsg_type) {
		case IPV6_HOPLIMIT:
			if (c->cmsg_len < CMSG_LEN(sizeof(int)))
				continue;
			hops = *(int*)CMSG_DATA(c);
		}
	}
	return hops;
}

/*
 * for ipv6
 */
struct t_mvars measure_ipv6(int64_t delays[], int packetcount,
			    struct sockaddr_in6 *addr) {
	int rawsock, ident, addrlen, recv_bytes;
	struct t_mvars mvars;	// return vars
	struct timeval timeout; // timeout for sending packets
	unsigned int headersize = sizeof(struct icmp6_hdr);
	unsigned int datasize = sizeof(struct timeval);
	unsigned int packetsize = headersize + datasize;
	unsigned char packet[packetsize]; // echo request
	// receiving buffer for incoming packets
	unsigned char buffer[sizeof(struct ip6_hdr) + packetsize]; // echo reply
	struct icmp6_hdr *icp = (struct icmp6_hdr*) packet;
	struct icmp6_hdr *icp_reply;
	struct timeval *t1 = (struct timeval*) &packet[headersize]; // now
	// the IPv6 header is automatically removed on received packets. see:
	// http://manpages.ubuntu.com/manpages/hardy/man4/icmp6.4.html
	struct timeval *t2 = (struct timeval*) &buffer[sizeof(struct icmp6_hdr)]; // receive
	
	struct icmp6_filter fil;

	char addrbuf[128];
	char ans_data[4096];
	struct iovec iov;
	struct msghdr msg;
	int on = 1;

	fd_set fds; // socket-container for select()
	// prepare mvars
	mvars.seqno = 0; // packet number
	mvars.received = 0; // number of received replys
	mvars.loss = 0;
	mvars.error = 0;
	mvars.hopcount = 0;
	// init buffers
	memset(delays, 0, sizeof(int64_t) * packetcount);
	memset(packet, 0, packetsize);
	memset(buffer, 0, sizeof(struct ip6_hdr) + packetsize);
	// create RAW socket
	if ((rawsock = socket(AF_INET6, SOCK_RAW, IPPROTO_ICMPV6)) < 0) {
		mvars.error = errno;
		mvars.errortext = "could not open raw socket";
		return mvars;
	}
	// set up ICMP header
	icp->icmp6_type = ICMP6_ECHO_REQUEST;
	icp->icmp6_code = 0;
	ident = 42; //getpid() & 0xFFFF;
	icp->icmp6_id = ident;
	// set up destination structure -> mostly done
	addr->sin6_port = 0;
	addrlen = sizeof(addr);
	// fill the socket-container
	FD_ZERO(&fds);
	FD_SET(rawsock, &fds);

	ICMP6_FILTER_SETPASS(ICMP6_ECHO_REPLY, &fil);
	setsockopt (rawsock, IPPROTO_ICMPV6, ICMP6_FILTER, &fil, sizeof (fil));
	if (setsockopt(rawsock, IPPROTO_IPV6, IPV6_RECVHOPLIMIT, &on, sizeof(on)) == -1) {
		mvars.error = ERROR_SETSOCKOPT_IPV6;
		mvars.errortext = "could not setsockopt IPV6_RECVHOPLIMIT. we won't be able to read IPv6 hop limits.";
	}
 	    
	// used by sendmsg()
	memset(&msg, 0, sizeof(msg));
	memset(&addrbuf, 0, sizeof(addrbuf));
	iov.iov_len = sizeof(buffer);
	iov.iov_base = &buffer;
	msg.msg_name = addrbuf;
	msg.msg_namelen = sizeof(addrbuf);
	msg.msg_iov = &iov;
	msg.msg_iovlen = 1;
	msg.msg_control = ans_data;
	msg.msg_controllen = sizeof(ans_data);

	// try to send 'packetcount' ICMP-packets (echo requests)
	while ((mvars.seqno < packetcount) && (mvars.received < packetcount)) {
		//prepare the packet for sending
		icp->icmp6_seq = (mvars.seqno << 8);
		// current time on this node
		gettimeofday(t1, NULL);
		// checksum is provided by IP6-header and calculated automatically
		icp->icmp6_cksum = 0;
		//icp->icmp6_cksum = checksum((u_short*) icp, packetsize);
		// send the packet
		if ((sendto(rawsock, packet, packetsize, 0, (struct sockaddr*) addr,
			    sizeof(struct sockaddr_in6))) < 0) {
			mvars.error = errno;
			mvars.errortext = strerror(mvars.error);
			return mvars;
		} else {
			// count up seqno
			mvars.seqno++;
		}
		// wait for an incoming packet (with timeout)
		// listen in a loop as we might receive packets
		// that are not meant for us
		bool notforus = true;
		while (notforus) {
			timeout.tv_sec = DEFAULT_TIMEOUT;
			timeout.tv_usec = 0;
			
			if (select(rawsock + 1, &fds, (fd_set*) 0, (fd_set*) 0, &timeout) < 0) {
				mvars.error = errno;
				mvars.errortext = strerror(mvars.error);
				return mvars;
			}
			
			if (!FD_ISSET(rawsock, &fds)) {
				// count this as loss
				mvars.loss++;
				printf("no reply for packet %i. Counted as loss.\n",
				       mvars.seqno);
				break;
			}
			// there is some data on the socket, read it
			if ((recv_bytes = recvmsg(rawsock, &msg, 0)) < 0) {
				mvars.error = errno;
				mvars.errortext = strerror(mvars.error);
				return mvars;
			}
			// current time on this node AFTER the packet has been received
			gettimeofday(t1, NULL);
			// compare with IPv4: buffer has no offset anymore, since the IPv6 header is already
			// removed on receive.
			icp_reply = (struct icmp6_hdr*) (buffer);
			// does the packet belong to us? and is it an echo reply?
			// NOW: comparison instead of assignment, both comparisons must be true -> AND

			// 06.07.2009: should always be true, since we implemented a filter above, but just leave it for
			// debug functionality
			if ((icp_reply->icmp6_id == ident) 
			     && (icp_reply->icmp6_type == ICMP6_ECHO_REPLY)) {
				// everything seems to be ok, calculate RTT
				// do not account times for losses!
				delays[mvars.received] = deltaTime64(*t2, *t1);
				mvars.received++;
				notforus = false;
//				getsockopt(rawsock, IPPROTO_IPV6, IPV6_RECVHOPLIMIT, &socket_hlim, sizeof(socket_hlim));
				mvars.hopcount = read_hops(&msg);
				// not a very safe calculation of hop count, because the hop limit
				// could have been changed on the socket. but for now, it must be sufficient.
				if (mvars.hopcount < 65) {
					mvars.hopcount = 65 - mvars.hopcount;
				}
				else if (mvars.hopcount < 129) {
					mvars.hopcount = 129 - mvars.hopcount;
				}
				else {
					mvars.hopcount = 255 - mvars.hopcount;
				}
			} else {
				//printf("got a wrong icmp packet. why?\n");
				notforus = true;
			}
		}
	}
	// if we lost too many packets, set error message
	if (mvars.loss > (packetcount - FEWDATA_LIMIT)) {
		mvars.error = ERROR_FEWDATA_LIMIT;
		mvars.errortext = "Not enough data gathered for evaluation. Destination host unreachable?";
	} else {
		mvars.error = 0;
		mvars.errortext = "Everything went fine.";
	}
	return mvars;
}

/*
 * for ipv4
 */

struct t_mvars measure_ipv4(int64_t delays[], int packetcount,
			    struct sockaddr_in *addr) {
	int ident = 0; // is different for each process, so that echo replies do not
	struct t_mvars mvars;
	struct timeval timeout; //Timeout for sending packets
	int addrlen, recv_bytes, rawsock;
	unsigned int headersize = sizeof(struct icmphdr);
	unsigned int datasize = sizeof(struct timeval);
	unsigned int packetsize = headersize + datasize;
	unsigned char packet[packetsize]; // echo request

	// Important: 'buffer' is the receiving buffer for INCOMING packets. It contains
	// the IP-header and therefore it is larger than the 'packet'-buffer.
	// The'packet'-buffer will be expanded by the kernel (the IP-header is added
	// automatically!).
	unsigned char buffer[sizeof(struct iphdr) + packetsize]; // echo reply
	struct icmphdr *icp = (struct icmphdr*) packet;
	struct icmphdr *icp_reply;
	struct timeval *t1 = (struct timeval*) &packet[headersize]; // now
	struct timeval *t2 = (struct timeval*) &buffer[sizeof(struct icmphdr)
						       + sizeof(struct iphdr)]; // receive
	fd_set fds; // socket-container for select()
	// prepare mvars
	mvars.seqno = 0; // packet number
	mvars.received = 0; // number of received replys
	mvars.loss = 0;
	mvars.error = 0;
	mvars.hopcount = 0;
	// init buffers

	memset(delays, 0, sizeof(int64_t) * packetcount);
	memset(packet, 0, packetsize);
	memset(buffer, 0, sizeof(struct iphdr) + packetsize);
	// create RAW socket
	if ((rawsock = socket(AF_INET,SOCK_RAW, IPPROTO_ICMP)) < 0) {
		mvars.error = errno;
		mvars.errortext = "could not open raw socket";
		return mvars;
	}
	// set up ICMP header
	icp->type = ICMP_ECHO;
	icp->code = 0;
	ident = 42; //getpid() & 0xFFFF;
	icp->un.echo.id = ident;
	// set up destination structure -> mostly done

	addr->sin_port = 0;
	addrlen = sizeof(addr);
	// fill the socket-container
	FD_ZERO(&fds);
	FD_SET(rawsock, &fds);

	// try to send 'packetcount' ICMP-packets (echo requests)
	while ((mvars.seqno < packetcount) && (mvars.received < packetcount)) {
		//prepare the packet for sending
		icp->un.echo.sequence = (mvars.seqno << 8);
		// calculate checksum of packet after everything is set
		icp->checksum = 0;
		// current time on this node
		gettimeofday(t1, NULL);
		icp->checksum = checksum((u_short*) icp, packetsize);
		// send the packet
		if ((sendto(rawsock, packet, packetsize, 0, (struct sockaddr*) addr,
			    sizeof(struct sockaddr_in))) < 0) {
			mvars.error = errno;
			mvars.errortext = strerror(mvars.error);
			return mvars;
		} else {
			// count up seqno
			mvars.seqno++;
		}
		// wait for an incoming packet (with timeout)
		// listen in a loop as we might receive packets
		// that are not meant for us
		bool notforus = true;
		while (notforus) {
			timeout.tv_sec = DEFAULT_TIMEOUT;
			timeout.tv_usec = 0;
			if (select(rawsock + 1, &fds, (fd_set*) 0, (fd_set*) 0, &timeout) < 0) {
				mvars.error = errno;
				mvars.errortext = strerror(mvars.error);
				return mvars;
			}
			
			if (!FD_ISSET(rawsock, &fds)) {
				// count this as loss
				mvars.loss++;
				printf("no reply for packet %i. Counted as loss.\n", mvars.seqno);
				break;
			}
			// there is some data on the socket, read it
			if ((recv_bytes = recvfrom(rawsock, buffer, sizeof(struct iphdr)
						   + packetsize, 0, (struct sockaddr*) addr,
						   (socklen_t*) &addrlen)) < 0) {
				mvars.error = errno;
				mvars.errortext = strerror(mvars.error);
				return mvars;
			}
			// current time on this node AFTER the packet has been received
			gettimeofday(t1, NULL);
			// skip the IP header of the received packet and look at the ICMP header
			icp_reply = (struct icmphdr*) (buffer + sizeof(struct iphdr));
			// does the packet belong to us? and is it an echo reply?
			// NOW: comparison instead of assignment, both comparisons must be true -> AND
			if ((icp_reply->un.echo.id == ident) 
			     && (icp_reply->type == ICMP_ECHOREPLY)) {
				// everything seems to be ok, calculate RTT
				// do not account times for losses!
				delays[mvars.received] = deltaTime64(*t2, *t1);
				mvars.received++;
				notforus = false;
				if (((struct iphdr*) buffer)->ttl > 128) {
					mvars.hopcount = 255 - ((struct iphdr*) buffer)->ttl;
				} else if (((struct iphdr*) buffer)->ttl > 128) {
					mvars.hopcount = 129 - ((struct iphdr*) buffer)->ttl;
				} else {
					mvars.hopcount = 65 - ((struct iphdr*) buffer)->ttl;
				}
			} else {
				//printf("got a wrong icmp packet. why?\n");
				notforus = true;
			}
		}
	}
	// if we lost too many packets, set error message
	if (mvars.loss > (packetcount - FEWDATA_LIMIT)) {
		mvars.error = ERROR_FEWDATA_LIMIT;
		mvars.errortext = "Not enough data gathered for evaluation. Destination host unreachable?";
	} else {
		mvars.error = 0;
		mvars.errortext = "Everything went fine.";
	}
	return mvars;
}

struct t_result measure(struct t_request req) {
	int i;
	int packetcount = DEFAULT_PACKETCOUNT;
	struct sockaddr_storage addr_buf;
	struct sockaddr *target;
	socklen_t target_len;
	struct t_result res;
	struct t_mvars mvars;
	int64_t delays[packetcount]; // array with RTTs
	mvars.received = -1;
	memset(&addr_buf, 0, sizeof(addr_buf));
	target = (struct sockaddr *) (&addr_buf);
	if ((res.error = parse_addr_str(req.identifier2, target, &target_len))) {
		res.errortext = "invalid identifier";
		res.HOPCOUNT = -1;
		res.RTT = -1;
		res.RTT_MIN = -1;
		res.RTT_MAX = -1;
		res.RTT_DEVIATION = -1;
		res.RTT_JITTER = -1;
		res.OWD = -1;
		res.OWD_MIN = -1;
		res.OWD_MAX = -1;
		res.OWD_DEVIATION = -1;
		res.OWD_JITTER = -1;
		res.LOSSRATE = -1;
		return res;
	}
	if (target->sa_family == AF_INET) {
		mvars = measure_ipv4(delays, packetcount,
				     (struct sockaddr_in *) target);
	} else if (target->sa_family == AF_INET6) {
		mvars = measure_ipv6(delays, packetcount,
				     (struct sockaddr_in6 *) target);
	} else {
		// handle unknown protocol
	}
	// calculate and prepare results
	res.RTT = average(delays, mvars.received);
	res.RTT_MIN = min(delays, mvars.received);
	res.RTT_MAX = max(delays, mvars.received);
	res.RTT_DEVIATION = deviation(delays, mvars.received);
	res.RTT_JITTER = jitter(delays, mvars.received);
	//	// to provide fake owd, we use the times/2 for owd at the moment
	for (i = 0; i < mvars.received; i++) {
		delays[i] /= 2;
	}
	res.OWD = average(delays, mvars.received);
	res.OWD_MIN = min(delays, mvars.received);
	res.OWD_MAX = max(delays, mvars.received);
	res.OWD_DEVIATION = deviation(delays, mvars.received);
	res.OWD_JITTER = jitter(delays, mvars.received);

	//	// we can estimate roughly a loss rate
	if (mvars.seqno > 0) {
		res.LOSSRATE = 1000 * mvars.loss / (mvars.seqno);
	} else {
		res.LOSSRATE = 1000;
	}
	res.HOPCOUNT = mvars.hopcount;
	// add the error code
	res.error = mvars.error;
	res.errortext = mvars.errortext;
	return res;
}

/**
 * Calculates the checksum for an ICMP packet
 */
u_short checksum(void *b, int len) {
	u_short *buf = (u_short*) b;
	u_short r;
	unsigned int sum = 0;
	for (; len > 1; len -= 2)
		sum += *buf++;
	if (len == 1) {
		u_short padding = 0;
		*(u_char *) (&padding) = *(u_char *) buf;
		sum += padding;
	}
	sum = (sum >> 16) + (sum & 0xFFFF);
	sum += (sum >> 16);
	r = ~sum;
	return r;
}

