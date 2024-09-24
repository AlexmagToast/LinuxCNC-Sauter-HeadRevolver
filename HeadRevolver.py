#!/usr/bin/python3.9
import time, hal , re

#	HeadRevolver for LinuxCNC
#	By Alexander Richter, info@theartoftinkering.com 2022
#	Please consider supporting me on Patreon.com/theartoftinkering
#
#   This Program supports the Hydraulic Turret by Sauter. 
#	It was included in the Weiler Primus CNC and runs entirely by one hydraulik piston. More detail can be seen here: 
#   https://www.youtube.com/watch?v=d5WtskW0o68
#
#	This script waits for "trequest" to go high. It will then read "toolnumber" and look it up in the Tool table. 
# 	There it looks for "R" and the Number 1-4 representing one of each Turret sides in the comment section. 
#	Then the current Turrent pos is checked and the Hydraulic will cycle until the required Turret Pos is reached. 
#	Lastly the "toolchanged" Pin goes High, which will indicate to LinuxCNC that the Turret is ready. 
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
File = "/home/primuscnc/linuxcnc/configs/WeilerPrimusCNC/tool.tbl" #change this to point to your tool table file

pistonreturn = 1
#HAL Setup
c = hal.component("Sauter") #name that we will cal pins from in hal

#Inputs 
c.newpin("hydraulik", hal.HAL_BIT, hal.HAL_IN)
c.newpin("pos1", hal.HAL_BIT, hal.HAL_IN)
c.newpin("pos2", hal.HAL_BIT, hal.HAL_IN)
c.newpin("pos3", hal.HAL_BIT, hal.HAL_IN)
c.newpin("pos4", hal.HAL_BIT, hal.HAL_IN)
c.newpin("trequest", hal.HAL_BIT, hal.HAL_IN)

c.newpin("toolnumber", hal.HAL_S32, hal.HAL_IN)


#Outputs
c.newpin("coilA", hal.HAL_BIT, hal.HAL_OUT)
c.newpin("coilB", hal.HAL_BIT, hal.HAL_OUT)

c.newpin("toolchanged", hal.HAL_BIT, hal.HAL_OUT)

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


def defineToolpos(toolnbr):  #finds Toolorientation on Revolver

    regex = r".*T(\d+).*;.*R(\d+)"
    fileinhalt = ""

    with open(File) as f:
        fileinhalt = f.read()

    matches = re.finditer(regex, fileinhalt, re.MULTILINE)

    for matchNum, match in enumerate(matches, start=1):
        
        #print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = m3atchNum, start = match.start(), end = match.end(), match = match.group()))
        T = int(match.group(1))
        R = int(match.group(2))
        
        if T == toolnbr:
            return (R)

def wait(counter):#wait for piston to return
    return counter + pistonreturn < time.time()

while True:
	time.sleep(0.1)
	try:
		#c.debug = defineToolpos(c.toolnumber)
		if c.hydraulik == 0: c.fault = 1
		else:c.fault = 0
		c.toolchanged = 0

		if c.trequest == 1 and c.toolchanged == 0:
			time.sleep(0.1)
			
			newTool = defineToolpos(c.toolnumber)
			if newTool != getPosition():
				c.toolchanged = 0
				c.debug = State
				while State == 0: #Standard Position
					c.coilA = 1
					c.coilB = 0
					if getPosition() == 0:
						State = 1
					time.sleep(0.1)
				c.debug = State
				while State == 1: #Start turning to new Position and wait for reaching new Position
					start_time = time.time()  
					time.sleep(1.25)         
					if getPosition() != 0: #proceed to next State if new Position is reached
						State = 2
					elif time.time() - start_time > 5: # return to Start State if the Toolhead fails to reach Position after 5 seconds
						State = 0
				c.debug = State
				while State == 2:
					c.coilA = 0
					c.coilB = 1
					time.sleep(1.25)
					State = 3
					
				c.debug = State
				
				if State == 3:
					c.coilA = 0
					c.coilB = 0
					State = 0
					c.debug = State
			if newTool == getPosition():
				c.toolchanged = 1 
	except:
		pass

