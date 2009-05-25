/**
 * mathfunctions.h
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
#ifndef MATHFUNCTIONS_H_
#define MATHFUNCTIONS_H_

#include <time.h>
#include <limits.h>
#include <stdlib.h>
#include <sys/time.h>
#include <sys/types.h>
//#include <string.h>
#include <math.h> // only required for calculation stuff!
/**
 * Helper functions needed for several measurement modules
 */

/**
 * Calculates the delta of two timeval-structures
 * @param tv1 earlier timestamp
 * @param tv2 later timerstamp
 * @result struct timeval delta t
 */
struct timeval deltaTime(struct timeval tv1, struct timeval tv2);

/**
 * Calculates the delta of two timeval-structures
 * @param tv1 earlier timestamp
 * @param tv2 later timerstamp
 * @result int64_t delta t in microseconds
 */
int64_t deltaTime64(struct timeval tv1, struct timeval tv2);

/**
 * get timeval as int64_t
 * @param tv struct timeval
 * @result int64_t the timestamp in microseconds
 */
int64_t timeval2int64(struct timeval tv);

/**
 * Determines the maximum value of an array
 * @param v pointer to an array of int
 * @param n number of values
 * @result int max value, LONG_LONG_MAX if n = 0
 */
int64_t max(int64_t *v, int n);

/**
 * Determines the minimum value of an array
 * @param v pointer to an array of int
 * @param n number of values
 * @result int min value, LONG_LONG_MIN if n = 0
 */
int64_t min(int64_t *v, int n);

/**
 * Calculates the arithmetic mean of all results
 * @param v pointer to an array of int
 * @param n number of values
 * @result int average value, LONG_LONG_MAX if n = 0
 */
int64_t average(int64_t *v, int n);

/**
 * Calculates the standard deviation over all values
 * @param v pointer to an array of int
 * @param n number of values
 * @result int deviation, LONG_LONG_MAX if n = 0
 */
int64_t deviation(int64_t *v, int n);

/**
 * Calculates the jitter over all values
 * @param v pointer to an array of int
 * @param n number of values
 * @result int jitter, LONG_LONG_MAX if n = 0
 */
int64_t jitter(int64_t *v, int n);

#endif /* MATHFUNCTIONS_H_ */
