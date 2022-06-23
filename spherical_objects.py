#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 19:14:16 2022

@author: sahab
"""

import math
from typing import List

# Lens constants assuming a 1080p image
f = 714.285714
center = [960, 540]
D = 1.082984  # For image-1, switch to 0.871413 for image-2


def cartesian2sphere(pt):
    x = (pt[0] - center[0]) / f
    y = (pt[1] - center[1]) / f

    r = math.sqrt(x*x + y*y)
    if r != 0:
        x /= r
        y /= r
    r *= D
    sin_theta = math.sin(r)
    x *= sin_theta
    y *= sin_theta
    z = math.cos(r)

    return [x, y, z]


def sphere2cartesian(pt):
    r = math.acos(pt[2])
    r /= D
    if pt[2] != 1:
        r /= math.sqrt(1 - pt[2] * pt[2])
    x = r * pt[0] * f + center[0]
    y = r * pt[1] * f + center[1]
    return [x, y]


def convert_point(point: List[int]) -> List[int]:
    """Convert single points between Cartesian and spherical coordinate systems"""
    if len(point) == 2:
        return cartesian2sphere(point)
    elif len(point) == 3:
        return sphere2cartesian(point)
    else:
        raise ValueError(f'Expected point to be 2 or 3D, got {len(point)} dimensions')


class CartesianBbox:

    def __init__(self, points: List[int], fmt: str):
        assert fmt in ['xyxy', 'xywh', 'cxcywh'], 'Invalid bbox format'
        assert len(points) == 4, 'Cartesian bbox must have 4 values'
        if fmt=='xywh': 
            points = xywh_to_xyxy(points)
        elif fmt=='cxcywh':
            points = cxcywh_to_xyxy(points)
            
        self.points = points
        self.fmt = fmt


class SphericalBbox:

    def __init__(self, points: List[int], fmt: str):
        assert fmt in ['xyzxyz', 'xyzwhd', 'cxcyczwhd'], 'Invalid spherical bbox format'
        assert len(points) == 6, 'Spherical bbox must have 6 values'
        if fmt=='xyzwhd': 
            points = xyzwhd_to_xyzxyz(points)
        elif fmt=='cxcyczwhd':
            points = cxcyzwhd_to_xyzxyz(points)
        self.points = points
        self.fmt = fmt


def xyzwhd_to_xyzxyz(points: List[int]):
    x1, y1, z1, w, h, d = points
    
    x2 = x1 + w
    y2 = y1 + h
    z2 = z1 + d
    
    return [x1, y1, z1, x2, y2, z2]

def cxcyczwhd_to_xyzxyz(points: List[int]):
    cx, cy, cz, w, h, d = points
    
    x1 = cx - w // 2
    y1 = cy - h // 2
    z1 = cz - d // 2
    
    x2 = cx + w // 2
    y2 = cy + h // 2
    z2 = cz + d // 2
    
    return [x1, y1, z1, x2, y2, z2]		
		
def bbox_to_spherical(cartesian: CartesianBbox) -> SphericalBbox:
        points = cartesian.points
        p1 = convert_point(points[:2])
        p2 = convert_point(points[2:])
        return SphericalBbox([*p1, *p2], 'xyzxyz')
        

def points2_distance(p1: List[int], p2: List[int]) -> float:
    return (math.sqrt(math.pow(p1[0]-p2[0], 2) + \
                      math.pow(p1[1]-p2[1], 2)) )
        
class CartesianPolygon:

    def __init__(self, points: List[int]):
        # assert fmt in ['xyxy', 'xywh', 'cxcywh'], 'Invalid bbox format'
        assert len(points)%2== 0, 'All points in cartesian polygon must be pairs of coordinates.' 
        assert len(points) <= 40 and len(points)>=6, 'The number of points in cartesian polygon must be between 3 and 20.' + \
            f' You gave {len(points)//2} points.'
        self.points = points
        self.numPoints = len(self.points)//2
        # self = fmt
    
    def getPoint(self, index) -> List[int]:
        ### Returns point at position: index in polygon
        assert index<self.numPoints, 'Polygon point index ' + str(index) + ' out of bounds.'
        return self.points[2*index:2*index+2]

    def isRegular(self) -> bool:
        
        eps = 1e-3
        # optimize code structure: call getPoint
        # prev_side_len = distances.append(points2_distance(getPoint(self, 0), getPoint(self, 1)))
        prev_side_len = points2_distance(self.points[2*0:2*0+2], self.points[2*1:2*1+2] )
        for i in range(1, self.numPoints-1):
            # point1, point2 = getPoint(i), getPoint(i+1)
            point1, point2 = self.points[2*i:2*i+2], self.points[2*(i+1):2*(i+1)+2]
            # print(point1, point2)
            curr_side_len = points2_distance(point1, point2)
            # print(prev_side_len, curr_side_len)
            if (curr_side_len - prev_side_len) > eps:
                return False
            else: 
                prev_side_len = curr_side_len
                
        return True
        
    



class SphericalPolygon: # Question 4
    
    def __init__(self, points: List[int]):
        assert len(points) <= 60 and len(points)>=9, 'The number of points in spherical polygon must be between 3 and 20.'
        assert len(points)%3 == 0, 'All points in spherical polygon must be triplets of coordinates.' + \
            f' You gave {len(points)//3} points.'
        self.points = points
        self.numPoints = len(points) // 3
        
    def getPoint(self, index: int) -> List[int]:
        ### Returns point at position: index in polygon
        assert index<self.numPoints, 'Spherical polygon point index ' + str(index) + ' out of bounds.'
        return self.points[3*index:3*index+3]

    def isRegular(self) -> bool:
        distances = []
        eps = 1e-3
        # prev_side_len = distances.append(points3_distance(getPoint(self, 0), getPoint(self, 1)))
        prev_side_len = points3_distance(self.points[3*0:3*0+3], self.points[3*1:3*1+3])
        for i in range(1, self.numPoints-1):
            # point1, point2 = getPoint(i), getPoint(i+1)
            point1, point2 = self.points[3*i:3*i+3], self.points[3*(i+1):3*(i+1)+3]
            # print(point1, point2)
            curr_side_len = points3_distance(point1, point2)
            # print(prev_side_len, curr_side_len)
            if curr_side_len - prev_side_len > eps:
                return False
            else: 
                prev_side_len = curr_side_len
                
        return True
        
    
def points3_distance(p1: List[int], p2: List[int]) -> float:
    assert len(p1)==3 and len(p2)==3, 'p1 and p2 should have length=3'
    return (math.sqrt(math.pow(p1[0]-p2[0], 2) + \
                      math.pow(p1[1]-p2[1], 2) + \
                      math.pow(p1[2]-p2[2], 2)) )
            
def polygon_to_spherical(cP: CartesianPolygon) -> SphericalPolygon: # Question 4
    # sp_points = [0] * (len(points)/2)*3
    sp_points = []
    for i in range(0, 2, len(cP.points)):
        p_2 = cP.points[i:i+2]
        p_3 = convert_point(p_2)
        sp_points.append(p_3)
    
    return SphericalPolygon(sp_points)




def xywh_to_xyxy(points: List[int]):
    x1, y1, w, h = points
    x2 = x1 + w
    y2 = y1 + h
    return [x1, y1, x2, y2]

def cxcywh_to_xyxy(points: List[int]):
    cx, cy, w, h = points
    x1 = cx - w // 2
    y1 = cy - h // 2
    x2 = cx + w // 2
    y2 = cy + h // 2
    return [x1, y1, x2, y2]
    
# BBox testing
print('Cartesian Bbox testing')
points = [10,20,70,80]
print('Input list is: ', points)
fmt = 'xyxy'
cb = CartesianBbox(points, fmt)
print('Cartesian bbox points (Format: ', fmt, ') are: ', cb.points)

fmt = 'xywh'
cb = CartesianBbox(points, fmt)
print('Cartesian bbox points (Format: ', fmt, ') are: ', cb.points)

fmt = 'cxcywh'
cb = CartesianBbox(points, fmt)
print('Cartesian bbox points (Format: ', fmt, ') are: ', cb.points)
print()


# Spherical BBox testing
print('Spherical Bbox testing')
points = [10,20,70,80]
fmt = 'xyxy'
cb = CartesianBbox(points, fmt)
print('Input list (cartesian points) is: ', cb.points)
sb = bbox_to_spherical(cb) # testing with default fmt = 'xyzxyz'
print('Spheical bbox points are: ', sb.points)

print()


#Polygon testing
print('Cartesian Polygon testing')
cP  = CartesianPolygon([1, 2, 3, 4, 5, 6, 7, 8])
print('Cartesian polygon has ', str(cP.numPoints), ' points as given below:')
print(cP.points)
print("Testing of whether the polygon is regular: ", cP.isRegular())
print()

#Spherical Polygon testing
print('Spherical Polygon testing')
sP = SphericalPolygon([1, 2, 3, 4, 5, 6, 7, 8, 9])
print('Cartesian polygon has ', str(sP.numPoints), ' points as given below:')
print(sP.points)
print("Testing of whether the polygon is regular: ", sP.isRegular())
print()

# s = convert_point([-0.8749644005261881, -0.4789278823932819, -0.07117149203251981])
# o = convert_point(points[:2])