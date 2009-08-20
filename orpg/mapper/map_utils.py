"""
 file: map_utils.py

 This file contains generic utility functions
 for use in the openrpg mapping system
"""

import math
"""
 distance_between()
 Returns the distance between two points
"""
def distance_between( x1, y1, x2, y2 ):
   "Returns the distance between two points"
   dx = x2 - x1
   dy = y2 - y1
   return math.sqrt( dx*dx + dy*dy )

"""
 proximity_test()
 Tests if 'test_point' (T) is close (within 'threshold' units) to the
 line segment 'start_point' to 'end_point' (PQ).

 The closest point (R) to T on the line PQ is given by:
    R = P + u (Q - P)
 TR is perpendicular to PQ so:
    (T - R) dot (Q - P) = 0
 Solving these two equations gives the equation for u (see below).

 If u < 0 or u > 1 then R is not within the line segment and we simply
 test against point P or Q.
"""
def proximity_test( start_point, end_point, test_point, threshold ):
   "Test if a point is close to a line segment"
   x1,y1 = start_point
   x2,y2 = end_point
   xt,yt = test_point
   x1 = float(x1)
   x2 = float(x2)
   y1 = float(y1)
   y2 = float(y2)
   xt = float(xt)
   yt = float(yt)

   # Coincident points?
   if x1 == x2 and y1 == y2: d = distance_between(xt, yt, x1, y1)
   else:
       dx = x2 - x1
       dy = y2 - y1
       u = ((xt - x1) * dx + (yt - y1) * dy) / (dx*dx + dy*dy)
       if u < 0: d = distance_between(xt, yt, x1, y1)
       elif u > 1: d = distance_between(xt, yt, x2, y2)
       else:
           xr = x1 + u * dx
           yr = y1 + u * dy
           d = distance_between(xt, yt, xr, yr)
   return d <= threshold
