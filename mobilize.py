#!/usr/bin/env python

import liblo
import sys
from math import *

#*************#
class MobilePart(object):
    def __init__(self):
        self.isBalanced = False
        self.m = [1.0, 1.0]
        self.l = 2.0
        self.handle = 0.5
        self.children = []
        self.parent = None

    def addChild(self, part, ratio):
        child = [part, ratio]
        self.children.append(child)

    def removeChild(self, part):
        rightChild = None
        for child in children:
            if part in child:
                rightChild = child
                break
        if rightChild != None:
            self.children.remove(rightChild)

    def setLength(self, length):
        self.l = length

    def setHandle(self, ratio):
        self.handle = max(0.0, min(1.0, ratio))

    def getMass(self):
        return self.m[0] + self.m[1]

    def balance(self):
        for child in self.children:
            if child[0].isBalanced = False:
                child.balance()


