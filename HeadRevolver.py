#!/usr/bin/python3.9
import time, hal
#	LubeDude for LinuxCNC
#	By Alexander Richter, info@theartoftinkering.com 2022
#	Please consider supporting me on Patreon.com/theartoftinkering

#
#	This program is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; either version 2 of the License, or
#	(at your option) any later version.
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#	See the GNU General Public License for more details.
#	You should have received a copy of the GNU General Public License
#	along with this program; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  US

#Config
File = "/home/alex/linuxcnc/configs/sim.axis"

pistonreturn = 1
#HAL Setup
c = hal.component("AAA") #name that we will cal pins from in hal

#Inputs 
c.newpin("hydraulik", hal.HAL_BIT, hal.HAL_IN)
c.newpin("pos1", hal.HAL_BIT, hal.HAL_IN)
c.newpin("pos2", hal.HAL_BIT, hal.HAL_IN)
c.newpin("pos3", hal.HAL_BIT, hal.HAL_IN)
c.newpin("pos4", hal.HAL_BIT, hal.HAL_IN)

#Outputs
c.newpin("coilA", hal.HAL_BIT, hal.HAL_OUT)
c.newpin("coilB", hal.HAL_BIT, hal.HAL_OUT)


c.newpin("fault", hal.HAL_BIT, hal.HAL_OUT)
c.newpin("reset", hal.HAL_BIT, hal.HAL_IN)
c.newpin("debug", hal.HAL_FLOAT, hal.HAL_OUT)

c.ready()

State = 0

#functions
def getPosition(): #returns Revolver Position returns 0 while turning
    if c.pos1 == 1:
        return 1
    elif c.pos2 == 1:
         return 2
    elif c.pos3 == 1:
         return 3
    elif c.pos4 == 1:
         return 4
    else:
        return 0


def extract_nbr(input_str):
    if input_str is None or input_str == '':
        return 0

    out_number = ''
    for ele in input_str:
        if ele.isdigit():
            out_number += ele
    return int(out_number) 

def defineToolpos(toolnbr):  #finds Toolorientation on Revolver
    with open(File) as f:
        for line in f:
            data = line.strip()
            data = data.split(" ",1)
            if toolnbr == extract_nbr(data[0]):
                data = data[1].split("Q",1)
                return extract_nbr(data[1][0])
                break

def wait(counter):#wait for piston to return
    return counter + pistonreturn < time.time()

while True:
	try:
		c.debug = State
		nextTool = hal.get_value("iocontrol.0.tool-prep-number")
	
		if c.hydraulik == 0: c.fault = 1
		else:c.fault = 0


		if hal.get_value("iocontrol.0.tool-prepare"):
			preppedTool = defineToolpos(nextTool)
			hal.set_p("iocontrol.0.tool-prepared","1")

		if hal.get_value("iocontrol.0.tool-change") == 1:
			if preppedTool != getPosition():
				while State == 0:
					c.CoilA = 1
					c.CoilB = 0
					if getPosition() == 0:
						State = 1
				c.debug = State
				while State == 1:
					if getPosition != 0:
						State = 2
				c.debug = State
				while State == 2:
					c.CoilA = 0
					c.CoilB = 1
					if wait(time.time()) == 1:
						State = 3
				c.debug = State
				if State == 3:
					c.CoilA = 0
					c.CoilB = 0
					State = 0
					hal.set_p("iocontrol.0.tool-changed","1")
					c.debug = State
	except:
		pass

