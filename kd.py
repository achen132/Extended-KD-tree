from __future__ import annotations
import json
import math
from typing import List

# Datum class.
# DO NOT MODIFY.
class Datum():
    def __init__(self,
                 coords : List[int],
                 code   : str):
        self.coords = coords
        self.code   = code
    def to_json(self) -> str:
        dict_repr = {'code':self.code,'coords':self.coords}
        return(dict_repr)

# Internal node class.
# DO NOT MODIFY.
class NodeInternal():
    def  __init__(self,
                  splitindex : int,
                  splitvalue : int,
                  leftchild,
                  rightchild):
        self.splitindex = splitindex
        self.splitvalue = splitvalue
        self.leftchild  = leftchild
        self.rightchild = rightchild

# Leaf node class.
# DO NOT MODIFY.
class NodeLeaf():
    def  __init__(self,
                  data : List[Datum]):
        self.data = data

# KD tree class.
class KDtree():
    def  __init__(self,
                  k    : int,
                  m    : int,
                  root = None):
        self.k    = k
        self.m    = m
        self.root = root

    # For the tree rooted at root, dump the tree to stringified JSON object and return.
    # DO NOT MODIFY.
    def dump(self) -> str:
        def _to_dict(node) -> dict:
            if isinstance(node,NodeLeaf):
                return {
                    "p": str([{'coords': datum.coords,'code': datum.code} for datum in node.data])
                }
            else:
                return {
                    "splitindex": node.splitindex,
                    "splitvalue": node.splitvalue,
                    "l": (_to_dict(node.leftchild)  if node.leftchild  is not None else None),
                    "r": (_to_dict(node.rightchild) if node.rightchild is not None else None)
                }
        if self.root is None:
            dict_repr = {}
        else:
            dict_repr = _to_dict(self.root)
        return json.dumps(dict_repr,indent=2)

    # Insert the Datum with the given code and coords into the tree.
    # The Datum with the given coords is guaranteed to not be in the tree.
    def insert(self,point:tuple[int],code:str):
        if self.root == None:
            self.root = NodeLeaf(data = [Datum(code = code, coords = point)])
        else:
            self.root = self.insertHelp(point, code, self.root)
    
    def insertHelp(self, point:tuple[int], code:str, curr):
        if(isinstance(curr, NodeLeaf)):
            curr.data.append(Datum(code = code, coords = point))
            curr = self.split(curr)
            return curr
        elif (isinstance(curr, NodeInternal)):
            if point[curr.splitindex] >= curr.splitvalue:
                curr.rightchild = self.insertHelp(point, code, curr.rightchild)
            else:
                curr.leftchild = self.insertHelp(point, code, curr.leftchild)
            return curr
        
    def boundingBox(self, curr):
        if isinstance(curr,NodeLeaf):
            return self.minmax(curr)
        elif isinstance(curr,NodeInternal):
            (minLeft, maxLeft) = self.boundingBox(curr.leftchild)
            (minRight, maxRight) = self.boundingBox(curr.rightchild)
            min = []
            max = []
            count = 0
            while count < self.k:
                if minLeft[count] < minRight[count]:
                    min.append(minLeft[count])
                else:
                    min.append(minRight[count])
                if maxLeft[count] > maxRight[count]:
                    max.append(maxLeft[count])
                else:
                    max.append(maxRight[count])
                count = count + 1
            return (min, max)
        
    def minmax(self, curr:NodeLeaf):
        count = 0
        dimMin = []
        dimMax = []
        #print(curr.data[0].coords)
        while count < self.k:
            for i in curr.data:
                #print(i.coords[count])
                if i == curr.data[0]:
                    dimMin.append(curr.data[0].coords[count])
                    dimMax.append(curr.data[0].coords[count])
                else:
                    if dimMin[count] >= i.coords[count]:
                        dimMin[count] = i.coords[count]
                    if dimMax[count] <= i.coords[count]:
                        dimMax[count] = i.coords[count]
            count = count + 1                
        #print()
        return (dimMin, dimMax)
        
    def split(self, curr:NodeLeaf):
        if len(curr.data) > self.m:
            splitvalue = None

            (dimMin, dimMax) = self.minmax(curr)

            minIndex = 0
            minDiff = 0
            count = 0
            while count < len(dimMin):
                #print(dimMax[count])
                #print(dimMin[count])
                if dimMax[count] - dimMin[count] > minDiff:
                    minIndex = count
                    minDiff = dimMax[count] - dimMin[count]
                count = count + 1

            sorted = self.mergesort(curr.data, minIndex)
            index = math.floor(len(sorted)/2)
            if len(sorted) % 2 == 0:
                splitvalue = (sorted[index-1].coords[minIndex]+sorted[index].coords[minIndex])/2
            else:
                splitvalue = sorted[index].coords[minIndex]
            leftchild = NodeLeaf(data = sorted[:index])
            rightchild = NodeLeaf(data = sorted[index:])
            temp = NodeInternal(splitvalue = float(splitvalue), splitindex = minIndex, leftchild = leftchild, rightchild = rightchild)
            #print(splitvalue)
            #print()
            return temp
        return curr
    
    def mergesort(self, lst, dim):
        if(len(lst)==1):
            return lst
        else:
            #print(dim)
            index = math.floor(len(lst)/2)
            left = self.mergesort(lst[:index], dim)
            right = self.mergesort(lst[index:], dim)
            i = 0
            j = 0
            output = []
            while i < len(left) and j < len(right):
                if left[i].coords[dim] < right[j].coords[dim]:
                    output.append(left[i])
                    i = i + 1
                else:
                    output.append(right[j])
                    j = j + 1
            while i < len(left):
                output.append(left[i])
                i = i + 1
            while j < len(right):
                output.append(right[j])
                j = j + 1
            return output


    # Delete the Datum with the given point from the tree.
    # The Datum with the given point is guaranteed to be in the tree.
    def delete(self,point:tuple[int]):
        (self.root, temp) = self.deleteHelp(point, self.root)
    
    def deleteHelp(self, point, curr):
        if isinstance(curr, NodeLeaf):
            for i in curr.data:
                if i.coords == point:
                    curr.data.remove(i)
            if len(curr.data) == 0:
                return curr, True
            return curr, False
        elif isinstance(curr, NodeInternal):
            if point[curr.splitindex] >= curr.splitvalue:
                (curr.rightchild, empty) = self.deleteHelp(point, curr.rightchild)
                if empty:
                    curr = curr.leftchild
            else:
                (curr.leftchild, empty) = self.deleteHelp(point, curr.leftchild)
                if empty:
                    curr = curr.rightchild
            return curr, False
        
    def sortPoints(self, point, lst):
        if(len(lst)==1):
            return lst
        else:
            index = math.floor(len(lst)/2)
            left = self.sortPoints(point, lst[:index])
            right = self.sortPoints(point, lst[index:])
            i = 0
            j = 0
            output = []
            while i < len(left) and j < len(right):
                if self.pointToPoint(point, left[i]) < self.pointToPoint(point, right[j]):
                    output.append(left[i])
                    i = i + 1
                elif self.pointToPoint(point, left[i]) == self.pointToPoint(point, right[j]):
                    if left[i].code < right[j].code:
                        output.append(left[i])
                        i = i + 1
                    else:
                        output.append(right[j])
                        j = j + 1
                else:
                    output.append(right[j])
                    j = j + 1
            while i < len(left):
                output.append(left[i])
                i = i + 1
            while j < len(right):
                output.append(right[j])
                j = j + 1
            return output

    # Find the k nearest neighbors to the point.
    def knn(self,k:int,point:tuple[int]) -> str:
        # Use the strategy discussed in class and in the notes.
        # The list should be a list of elements of type Datum.
        # While recursing, count the number of leaf nodes visited while you construct the list.
        # The following lines should be replaced by code that does the job.
        leaveschecked = 0
        knnlist = []
        leaveschecked = self.knnHelp(k, point, self.root, knnlist)
        knnlist = self.sortPoints(point, knnlist)
        # The following return line can probably be left alone unless you make changes in variable names.
        return(json.dumps({"leaveschecked":leaveschecked,"points":[datum.to_json() for datum in knnlist]}))
    
    def knnHelp(self, n, point, curr, acc: List):
        
        if isinstance(curr, NodeInternal):
            (minLeft, maxLeft) = self.boundingBox(curr.leftchild)
            (minRight, maxRight) = self.boundingBox(curr.rightchild)
            dleft = self.distance(point, minLeft, maxLeft)
            dright = self.distance(point, minRight, maxRight)
            output = 0
            if dleft <= dright:
                if len(acc) < n:
                    output = output + self.knnHelp(n, point, curr.leftchild, acc)
                else:
                    (maxIndex, maxDistance) = self.max(point, acc)
                    if dleft <= maxDistance:
                        output = output + self.knnHelp(n, point, curr.leftchild, acc)
                if len(acc) < n:
                    output = output + self.knnHelp(n, point, curr.rightchild, acc)
                else:
                    (maxIndex, maxDistance) = self.max(point, acc)
                    if dright <= maxDistance:
                        output = output + self.knnHelp(n, point, curr.rightchild, acc)
            else:
                if len(acc) < n:
                    output = output + self.knnHelp(n, point, curr.rightchild, acc)
                else:
                    (maxIndex, maxDistance) = self.max(point, acc)
                    if dright <= maxDistance:
                        output = output + self.knnHelp(n, point, curr.rightchild, acc)
                if len(acc) < n:
                    output = output + self.knnHelp(n, point, curr.leftchild, acc)
                else:
                    (maxIndex, maxDistance) = self.max(point, acc)
                    if dleft <= maxDistance:
                        output = output + self.knnHelp(n, point, curr.leftchild, acc)

            # if len(acc) < n:
            #     if dleft < dright:
            #         output = output + self.knnHelp(n, point, curr.leftchild, acc)
            #         #print(len(acc))
            #         if len(acc) < n:
            #             output = output + self.knnHelp(n, point, curr.rightchild, acc)
            #     else:
            #         output = output + self.knnHelp(n, point, curr.rightchild, acc)
            #         if len(acc) < n:
            #             output = output + self.knnHelp(n, point, curr.leftchild, acc)
            # if len(acc) == n:
            #     (maxIndex, maxDistance) = self.max(point, acc)
            #     print(maxDistance)
            #     print(dleft)
            #     if dleft < maxDistance:
            #         output = output + self.knnHelp(n, point, curr, acc)
            #     (maxIndex, maxDistance) = self.max(point, acc)
            #     if dright < maxDistance:
            #         #print("HOW")
            #         output = output + self.knnHelp(n, point, curr, acc)
            acc = self.sortPoints(point, acc)
            return output


        elif isinstance(curr, NodeLeaf):
            #print(curr.data[0].coords)
            maxIndex = 0
            maxDistance = 0
            updated = False
            if len(acc) > 0:
                (maxIndex, maxDistance) = self.max(point, acc)
            for i in curr.data:
                if len(acc) < n:
                    acc.append(i)
                    updated = True
                else:
                    if updated == True:
                        (maxIndex, maxDistance) = self.max(point, acc)
                        updated = False
                    if self.pointToPoint(point, i) < maxDistance:
                        acc[maxIndex] = i
                        updated = True
                    elif self.pointToPoint(point, i) == maxDistance:
                        if i.code < acc[maxIndex].code:
                            acc[maxIndex] = i
                            updated = True
            return 1

    def pointToPoint(self, point1, point2):
        count = 0
        output = 0
        while count < self.k:
            output = output + (point1[count] - point2.coords[count])**2
            count = count + 1
        return output

    def max(self, point, points:list):
        maxDistance = 0
        maxIndex = 0
        count = 0
        for i in points:
            distance = self.pointToPoint(point, i)
            if distance > maxDistance:
                maxDistance = distance
                maxIndex = count
            count = count + 1
        return (maxIndex, maxDistance)

    def distance(self, point, min, max):
        output = 0
        count = 0
        while count < self.k:
            if point[count] > max[count]:
                output = output + (point[count] - max[count])**2
            elif point[count] < min[count]:
                output = output + (min[count] - point[count])**2
            count = count + 1
        return output
