#!/usr/bin/env python

import liblo
import sys
import random
from math import *

VERBOSE = True
MIN_WEIGHT = 1.0

PART = 0
MASS = 1

#*************#
NEXT_ID = 0
def getId():
    global NEXT_ID
    NEXT_ID += 1
    return NEXT_ID

#*************#
class Mass(object):
    def __init__(self):
        self.id = getId()
        self.T = MASS
        self.totalWeight = 1.0
        self.parent = None
        self.isBalanced = True

    def printPart(self, lvl = 0, osc = None):
        return

#*************#
class MobilePart(object):
    def __init__(self):
        self.id = getId()
        self.T = PART
        self.isBalanced = False
        self.m = [MIN_WEIGHT, MIN_WEIGHT]
        self.l = 2.0
        self.totalWeight = 2 * MIN_WEIGHT
        self.handle = 0.5
        self.children = []
        self.parent = None

    def printPart(self, lvl = 0, osc = None):
        for child in self.children:
            for i in range(lvl):
                print('-'),
            print("Child id: " + str(child[0].id) + " -> " + str(child[1]))

        if (osc != None):
            liblo.send(osc, '/mobilize/part', ('i', lvl), ('i', self.id))
            for child in self.children:
                liblo.send(osc, 'mobilize/child', ('i', child[0].id), ('i', child[0].T), ('f', child[1]))

        for child in self.children:
            newLvl = lvl + 1
            child[0].printPart(newLvl, osc)

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

        orderedChildren = []
        for child in self.children:
            if len(orderedChildren) == 0:
                orderedChildren.append(child)
            else:
                for i in range(len(orderedChildren)):
                    if child[0].totalWeight < orderedChildren[i][0].totalWeight:
                        orderedChildren.insert(i, child)
                    else:
                        orderedChildren.insert(i + 1, child)

        nbr = len(orderedChildren)
        self.m = 0
        torque = 0.0
        for i in range(nbr):
            if i == nbr - 1 and i % 2 == 0:
                orderedChildren[i][1] = self.handle
            elif i % 2 == 0:
                pos = random.uniform(0.0, self.handle)
                orderedChildren[i][1] = pos            
                torque = (self.handle - pos) * orderedChildren[i][0].totalWeight
            else:
                w = orderedChildren[i][0].totalWeight
                pos = torque / w + self.handle
                orderedChildren[i][1] = pos

            self.totalWeight += orderedChildren[i][0].totalWeight

        self.isBalanced = True

        if VERBOSE:
            print(str(self) + ":")
            for child in self.children:
                print(str(child[0].id) + " -> " + str(child[1]))

#*************#
def addPart_callback(path, args, types, src, user_data):
    mobileRoot = user_data[0]
    mobilePtr = user_data[1]

    position = 0.5
    length = args[0]

    if VERBOSE:
        print("New part of length " + str(length) + " - Parent: " + str(mobilePtr))

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
def mass_callback(path, args, types, src, user_data):
    mass = args[0]

    newMass = Mass();
    newMass.totalWeight = mass
    user_data[1].addChild(newMass, 0.5)

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
    user_data[0].printPart(osc = user_data[2])
    
#*************#
if __name__ == "__main__":
    mobileRoot = MobilePart()
    mobilePtr = mobileRoot

    try:
        oscServer = liblo.Server(12500)
        oscClient = liblo.Address('127.0.0.1', 12502)
    except liblo.AddressError, err:
        print(str(err))
        sys.exit()

    user_data = [mobileRoot, mobilePtr, oscClient]
    oscServer.add_method("/mobilize/addPart", "f", addPart_callback, user_data)
    oscServer.add_method("/mobilize/handle", "f", handle_callback, user_data)
    oscServer.add_method("/mobilize/mass", "f", mass_callback, user_data)
    oscServer.add_method("/mobilize/parent", "", parent_callback, user_data)
    oscServer.add_method("/mobilize/balance", "", balance_callback, user_data)
    oscServer.add_method("/mobilize/print", "", print_callback, user_data)

    while True:
        oscServer.recv(33)
