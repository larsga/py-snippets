"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Mark N. Read, 2016.
"""
import random
import math

# Taken from this page:
# http://markread.info/2016/08/code-to-generate-a-levy-distribution/

def levy_distro(mu):
	''' From the Harris Nature paper. '''
	# uniform distribution, in range [-0.5pi, 0.5pi]
	x = random.uniform(-0.5 * math.pi, 0.5 * math.pi)

	# y has a unit exponential distribution.
	y = -math.log(random.uniform(0.0, 1.0))

	a = math.sin( (mu - 1.0) * x ) / (math.pow(math.cos(x), (1.0 / (mu - 1.0))))
	b = math.pow( (math.cos((2.0 - mu) * x) / y), ((2.0 - mu) / (mu - 1.0)) )

	z = a * b
	return z
