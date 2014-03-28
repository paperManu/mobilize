#!/bin/bash
oscsend localhost 12500 /mobilize/mass f 2
oscsend localhost 12500 /mobilize/mass f 3
oscsend localhost 12500 /mobilize/addPart f 2
oscsend localhost 12500 /mobilize/mass f 1
oscsend localhost 12500 /mobilize/mass f 1
oscsend localhost 12500 /mobilize/balance
oscsend localhost 12500 /mobilize/print
