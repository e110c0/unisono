/**
 * mathfunctions.c
 *
 *        Created on: Oct 26, 2008
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
#include "mathfunctions.h"

/**
 * Calculates the delta of two timeval-structui
 */
struct timeval deltaTime(struct timeval tv1, struct timeval tv2) {
	struct timeval delta;
	int64_t inusec;
	inusec = (tv2.tv_sec - tv1.tv_sec) * 1000000 + (tv2.tv_usec - tv1.tv_usec);
	delta.tv_sec = inusec / 1000000;
	delta.tv_usec = inusec % 1000000;
	return delta;
}

/**
 * Calculates the delta of two timeval-structui
 */
int64_t deltaTime64(struct timeval tv1, struct timeval tv2) {
	return ((tv2.tv_sec - tv1.tv_sec) * 1000000 + (tv2.tv_usec - tv1.tv_usec));
}

/**
 * get timeval as int64_t
 * @param tv struct timeval
 * @result int64_t the timestamp in microseconds
 */
int64_t timeval2int64(struct timeval tv) {
	return (tv.tv_sec * 1000000 + tv.tv_usec);
}

/**
 * Determines the maximum value of an array
 * @param v pointer to an array of int
 * @param n number of values
 * @result int max value, LONG_LONG_MAX if n = 0
 */
int64_t max(int64_t *v, int n) {
	int64_t max = 0;
	/* handle n = 0 */
	if (n == 0){
		return LLONG_MAX; 
	}
	int i;
	for (i = 0; i < n; i++) {
		if (v[i] > max) {
			max = v[i];
		}
	}
	return max;
}
/**
 * Determines the minimum value of an array
 * @param v pointer to an array of int
 * @param n number of values
 * @result int min value, LONG_LONG_MIN if n = 0
 */
int64_t min(int64_t *v, int n) {
	/* handle n = 0 */
	if (n == 0){
		return LLONG_MAX; 
	}
	int64_t min = 999999999;
	int i;
	for (i = 0; i < n; i++) {
		if (v[i] < min) {
			min = v[i];
		}
	}
	return min;
}

/**
 * Calculates the arithmetic mean of all results
 * @param v pointer to an array of int
 * @param n number of values
 * @result int average value, LONG_LONG_MAX if n = 0
 */
int64_t average(int64_t *v, int n) {
	int64_t sum = 0;
	/* handle divide by 0 */
	if (n == 0){
		return LLONG_MAX;
	}
	int i;
	for (i = 0; i < n; i++) {
		sum += v[i];
	}
	sum /=n;
	return sum;
}
/**
 * Calculates the standard deviation over all values
 * @param v pointer to an array of int
 * @param n number of values
 * @result int deviation, LONG_LONG_MAX if n = 0
 */
int64_t deviation(int64_t *v, int n) {
	int64_t m = average(v, n);
	int64_t sum = 0;
	/* handle divide by 0 */
	if (n == 0){
		return LLONG_MAX;
	}
	int i;
	for (i = 0; i < n; i++) {
		if (v[i] > 0) {
			sum += (v[i] - m) * (v[i] - m);
		}
	}
	return sqrt(sum / n);
}

/**
 * Calculates the jitter over all values
 * @param v pointer to an array of int
 * @param n number of values
 * @result int jitter, LONG_LONG_MAX if n = 0
 */
int64_t jitter(int64_t *v, int n) {
	int64_t sum = 0;
	/* handle divide by 0 */
	if (n == 0){
		return LLONG_MAX;
	}
	int i;
	for (i = 0; i < n - 1; i++) {
		sum += abs(v[i + 1] - v[i]);
	}
	return (sum / n);
}

