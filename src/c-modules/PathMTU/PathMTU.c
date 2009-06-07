/**
 *  PathMTU.c
 *
 *        Created on: 01.03.09
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

#include "PathMTU.h"

uint32_t get_error(unsigned int *new_mtu) {
	struct sockaddr_in dst;
	int res;
	struct msghdr msgh;
	struct cmsghdr *cmsgh;
	struct iovec iov;
	uint8_t cbuf[512];
	uint8_t payload[512];
	struct sock_extended_err *err;

	iov.iov_len = sizeof(payload);
	iov.iov_base = payload;
	msgh.msg_name = &dst;
	msgh.msg_namelen = sizeof(dst);
	msgh.msg_iov = &iov;
	msgh.msg_iovlen = 1;
	msgh.msg_flags = 0;
	msgh.msg_control = cbuf;
	msgh.msg_controllen = sizeof(cbuf);

	res = recvmsg(sockfd, &msgh, MSG_ERRQUEUE);
	if (res < 0) {
		if (errno == EAGAIN) {
			return 0;
		}
		close(sockfd);
		return -1;
	}

	for (cmsgh = CMSG_FIRSTHDR(&msgh); cmsgh; cmsgh = CMSG_NXTHDR(&msgh, cmsgh)) {
		if ((cmsgh->cmsg_level == IPPROTO_IP && cmsgh->cmsg_type == IP_RECVERR)
				|| (cmsgh->cmsg_level == IPPROTO_IPV6 && cmsgh->cmsg_type
						== IPV6_RECVERR)) {
			err = (struct sock_extended_err *) CMSG_DATA(cmsgh);
			if (err->ee_errno == EMSGSIZE) {
				*new_mtu = err->ee_info;
			}
			return err->ee_errno;
		}
	}
	return 0;
}

void data_wait() {
	fd_set fds;
	struct timeval tv;
	FD_ZERO(&fds);
	FD_SET(sockfd, &fds);
	tv.tv_sec = 1;
	tv.tv_usec = 0;
	select(sockfd + 1, &fds, NULL, NULL, &tv);
}

uint32_t probe_mtu(unsigned int mtu, unsigned int *new_mtu) {
	unsigned int retry = 0;
	uint32_t error;
	int ret;
	char buf[max_mtu];
	memset(buf, 0, sizeof(buf));
	while (retry < 10) {
#ifdef DEBUG
		printf("probe_mtu retry %d\n", retry);
#endif
		ret = sendto(sockfd, buf, mtu - headerlen, 0, target, target_len);
		error = get_error(new_mtu);
#ifdef DEBUG
		printf("probe_mtu error %d\n", error);
#endif
		if (error != 0) {
			if (error != EMSGSIZE && error != ECONNREFUSED) {
				++retry;
				continue;
			} else {
				return error;
			}
		}
		data_wait();
		if (recv(sockfd, buf, sizeof(buf), MSG_DONTWAIT) > 0) {
#ifdef DEBUG
			printf("probe_mtu got response -> active port -> change port");
#endif
			set_port(target, base_port + retry);
		}
		++retry;
		continue;
	}
	// return the last error
	return error;
}

int pmtu(void) {
	uint32_t send_error;
	int retry = 0;
	unsigned int mtu = max_mtu;
	unsigned int new_mtu;
	while (mtu > min_mtu && retry < 10) {
#ifdef DEBUG
		printf("pmtu try with mtu %i\n", mtu);
#endif
		send_error = probe_mtu(mtu, &new_mtu);

		// mtu is too large
		if (send_error == EMSGSIZE) {
#ifdef DEBUG
			printf("pmtu mtu value %d is too large -> set to new value %d\n", mtu, new_mtu);
#endif
			mtu = new_mtu;
			// host was reached
		} else if (send_error == ECONNREFUSED) {
#ifdef DEBUG
			printf("pmtu host was reached -> got mtu\n");
#endif
			return mtu;
			// host seems not to be reachable
		} else {
#ifdef DEBUG
			printf("pmtu host seems not to be reachable -> can't measure mtu\n");
#endif
			return 0;
			close(sockfd);
		}
		++retry;
	}
	return 0;
}

struct t_result measure(struct t_request req) {
	struct sockaddr_storage addr_buf;
	struct t_result res;
	int rescode;
	memset(&addr_buf, 0, sizeof(addr_buf));
	target = (struct sockaddr *) (&addr_buf);
	res.error = parse_addr_str(req.identifier2, target, &target_len);
	if ( res.error != 0) {
		res.errortext = "invalid identifier";
		res.PATHMTU = -1;
		res.HOPCOUNT = -1;
		return res;
	}

	set_port(target, base_port);
	// socket stuff et al
	sockfd = socket(target->sa_family, SOCK_DGRAM, 0);
	if (sockfd == -1) {
		//		res.errortext = "CPathMTU socket: ";
		res.error = errno;
		return res;
	}
	if (target->sa_family == AF_INET) {
		unsigned int opt = IP_PMTUDISC_PROBE;
		if (setsockopt(sockfd, IPPROTO_IP, IP_MTU_DISCOVER, &opt, sizeof(opt))
				== -1) {
			//			res.errortext = "CPathMTU setsockopt(IP_MTU_DISCOVER): ";
			res.error = errno;
			close(sockfd);
			return res;;
		}
		opt = true;
		if (setsockopt(sockfd, IPPROTO_IP, IP_RECVERR, &opt, sizeof(opt)) == -1) {
			//			res.error = "CPathMTU setsockopt(IP_RECVERR): ";
			res.error = errno;
			close(sockfd);
			return res;
		}
	} else if (target->sa_family == AF_INET6) {
		unsigned int opt = IPV6_PMTUDISC_PROBE;
		if (setsockopt(sockfd, IPPROTO_IPV6, IPV6_MTU_DISCOVER, &opt,
				sizeof(opt)) == -1) {
			//			res.error = "CPathMTU setsockopt(IP_MTU_DISCOVER): ";
			res.error = errno;
			close(sockfd);
			return res;
		}
		opt = true;
		if (setsockopt(sockfd, IPPROTO_IPV6, IPV6_RECVERR, &opt, sizeof(opt))
				== -1) {
			//			res.error = "CPathMTU setsockopt(IP_RECVERR): ";
			res.error = errno;
			close(sockfd);
			return res;
		}
	}

	res.PATHMTU = pmtu();
	close(sockfd);

	printf("Measure MTU:  %s  -->  %s\n", req.identifier1, req.identifier2);
	// TODO: get the hopcount
	if (res.PATHMTU != 0) {
		// FIXME: extract hopcount from icmp error
		res.HOPCOUNT = 0;
		res.error = 0;
		res.errortext = "Everything went fine.";
	} else {
		res.HOPCOUNT = 0;
		res.error = -1;
		res.errortext = "host not reachable with icmp";
	}
	return res;
}
