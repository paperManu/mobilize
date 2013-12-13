#!/usr/bin/env python

import liblo
import sys
from math import *

VERBOSE = True
MIN_WEIGHT = 1.0

#*************#
class MobilePart(object):
    def __init__(self):
        self.isBalanced = False
        self.m = [MIN_WEIGHT, MIN_WEIGHT]
        self.l = 2.0
        self.totalWeight = 2 * MIN_WEIGHT
        self.handle = 0.5
        self.children = []
        self.parent = None

    def printPart(self, lvl = 0):
        for i in range(lvl):
            print('-'),
        print("Left: " + str(self.m[0]) + " - Right: " + str(self.m[1]))

        for child in self.children:
            newLvl = lvl + 1
            child[0].printPart(newLvl)

    def addChild(self, part, ratio):
        child = [part, ratio]
        self.children.append(child)
        child[0].parent = self
        self.isBalanced = False

    def removeChild(self, part):
        rightChild = None
        for child in children:
            if part in child:
                rightChild = child
                break
        if rightChild != None:
            self.children.remove(rightChild)

        self.isBalanced = False

    def setLength(self, length):
        if length <= 0.0:
            return
        self.l = length

    def setHandle(self, ratio):
        if ratio == 0.0 or ratio == 1.0:
            print("Setting the handle to one end will lead to a mobile impossible to balance")
            return
        self.handle = max(0.0, min(1.0, ratio))

    def getMass(self):
        return self.m[0] + self.m[1]

    def balance(self):
        for child in self.children:
            if child[0].isBalanced == False:
                child[0].balance()

        self.totalWeight = 0.0

        childrenTorque = 0.0
        for child in self.children:
            position = child[1] - self.handle
            childrenTorque += child[0].totalWeight * position
            self.totalWeight += child[0].totalWeight

        if childrenTorque > 0:
            print("1 - " + str(childrenTorque))
            rightTorque = childrenTorque + self.m[1] * (1.0 - self.handle)
            self.m[0] = abs(rightTorque / self.handle)
        elif childrenTorque < 0:
            print("2 - " + str(childrenTorque))
            leftTorque = childrenTorque + self.m[0] * self.handle
            self.m[1] = abs(leftTorque / (1.0 - self.handle))
        else:
            print("3 - " + str(childrenTorque))
            if self.handle >= 0.5:
                self.m[0] = MIN_WEIGHT
                torque = self.m[0] * self.handle
                self.m[1] = abs(torque / (1.0 - self.handle))
            else:
                self.m[1] = MIN_WEIGHT
                torque = self.m[0] * (1.0 - self.handle)
                self.m[1] = abs(torque / self.handle)

        self.totalWeight += self.m[0]
        self.totalWeight += self.m[1]

        self.isBalanced = True

        if VERBOSE:
            print(str(self) + " - Left = " + str(self.m[0]) + " -- Right = " + str(self.m[1]) + " -- Total = " + str(self.totalWeight))

#*************#
def addPart_callback(path, args, types, src, user_data):
    mobileRoot = user_data[0]
    mobilePtr = user_data[1]

    position = args[0]
    length = args[1]

    if VERBOSE:
        print("New part at position " + str(position) + " of length " + str(length) + " - Parent: " + str(mobilePtr))

    newPart = MobilePart()
    newPart.setLength(length)
    user_data[1].addChild(newPart, position)

    user_data[1] = newPart

#*************#
def handle_callback(path, args, types, src, user_data):
    handle = args[0]
    if handle <= 0.0 or handle >= 1.0:
        return

    user_data[1].setHandle(handle)
    if VERBOSE:
        print("Set the handle position to " + str(handle) + " - " + str(user_data[1]))

#*************#
def parent_callback(path, args, types, src, user_data):
    mobileRoot = user_data[0]
    mobilePtr = user_data[1]

    if mobilePtr.parent != None:
        if VERBOSE:
            print("Going up to the parent of the current node! - Parent: " + str(mobilePtr.parent))
        user_data[1] = mobilePtr.parent
    elif VERBOSE:
        print("Can't go higher, already at the root - Current node:" + str(mobilePtr.parent))

#*************3
def balance_callback(path, args, types, src, user_data):
    mobileRoot = user_data[0]
    mobilePtr = user_data[1]
    mobileRoot.balance()

#*************#
def print_callback(path, args, types, src, user_data):
    user_data[0].printPart()
    
#*************#
if __name__ == "__main__":
    mobileRoot = MobilePart()
    mobilePtr = mobileRoot

    try:
        oscServer = liblo.Server(12500)
    except liblo.AddressError, err:
        print(str(err))
        sys.exit()

    user_data = [mobileRoot, mobilePtr]
    oscServer.add_method("/mobilize/addPart", "ff", addPart_callback, user_data)
    oscServer.add_method("/mobilize/handle", "f", handle_callback, user_data)
    oscServer.add_method("/mobilize/parent", "", parent_callback, user_data)
    oscServer.add_method("/mobilize/balance", "", balance_callback, user_data)
    oscServer.add_method("/mobilize/print", "", print_callback, user_data)

    while True:
        oscServer.recv(33)
