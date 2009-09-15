/**
 * helper.c
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
#include "helper.h"

double timeval_delta(struct timeval first, struct timeval second) {
	int32_t sec_delta, usec_delta;
	sec_delta = second.tv_sec - first.tv_sec;
	usec_delta = second.tv_usec - first.tv_usec;
	return (double) sec_delta * 1000000 + usec_delta;
}

void order_int(int32_t unord_arr[], int32_t ord_arr[], int32_t num_elems) {
	int32_t i, j;
	int32_t temp;
	for (i = 0; i < num_elems; i++)
		ord_arr[i] = unord_arr[i];
	for (i = 1; i < num_elems; i++) {
		for (j = i - 1; j >= 0; j--)
			if (ord_arr[j + 1] < ord_arr[j]) {
				temp = ord_arr[j];
				ord_arr[j] = ord_arr[j + 1];
				ord_arr[j + 1] = temp;
			} else
				break;
	}
}
void order_float(float unord_arr[], float ord_arr[], int32_t num_elems) {
	int i, j;
	float temp;
	for (i = 0; i < num_elems; i++)
		ord_arr[i] = unord_arr[i];
	for (i = 1; i < num_elems; i++) {
		for (j = i - 1; j >= 0; j--)
			if (ord_arr[j + 1] < ord_arr[j]) {
				temp = ord_arr[j];
				ord_arr[j] = ord_arr[j + 1];
				ord_arr[j + 1] = temp;
			} else
				break;
	}
}
