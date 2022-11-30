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
File = "D:\Git\LinuxCNC-Sauter-HeadRevolver\sim.tbl"

pistonreturn = 1
#HAL Setup
c = hal.component("lubedude") #name that we will cal pins from in hal

#Inputs 
c.newpin("Hydraulik", hal.HAL_BIT, hal.HAL_IN)
c.newpin("pos1", hal.HAL_BIT, hal.HAL_IN)
c.newpin("pos2", hal.HAL_BIT, hal.HAL_IN)
c.newpin("pos3", hal.HAL_BIT, hal.HAL_IN)
c.newpin("pos4", hal.HAL_BIT, hal.HAL_IN)

#Outputs
c.newpin("CoilA", hal.HAL_BIT, hal.HAL_OUT)
c.newpin("CoilB", hal.HAL_BIT, hal.HAL_OUT)

#Logic

"""tool-prep-number
tool-prep-loop
tool-changed
tool-change-loop
tool-change"""



c.newpin("ToolChangecmd", hal.HAL_BIT, hal.HAL_IN)
c.newpin("ToolChanged", hal.HAL_BIT, hal.HAL_OUT)
c.newpin("nextToolNo",hal.HAL_FLOAT, hal.HAL_IN)


c.newpin("Fault", hal.HAL_BIT, hal.HAL_OUT)
c.newpin("Reset", hal.HAL_BIT, hal.HAL_IN)

c.ready()


State = 0
def getPosition():
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

def defineToolpos(toolnbr):
    with open(File) as f:
        for line in f:
            data = line.strip()
            data = data.split(" ",1)
            if toolnbr == extract_nbr(data[0]):
                data = data[1].split("Q",1)
                return extract_nbr(data[1][0])
                break

def wait(counter):
    return counter + pistonreturn < time.time()

while True:
    if c.Hydraulik == 0: c.Fault = 1
    if c.Reset == 1: c.Fault = 0

    nextTool = c.nextToolNo
    nextTool = defineToolpos(nextTool)
    if c.ToolChangecmd == 1:
        if nextTool != getPosition():
            
            c.ToolChanged = 0
            while State == 0:
                c.CoilA = 1
                c.CoilB = 0
                if getPosition() == 0:
                    State = 1

            while State == 1:
                if getPosition != 0:
                    State = 2

            while State == 2:
                c.CoilA = 0
                c.CoilB = 1
                if wait(time.time()) == 1:
                    State = 3
            if State == 3:
                c.CoilA = 0
                c.CoilB = 0
                State = 0
                c.ToolChanged = 1
                
    

