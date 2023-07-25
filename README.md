
# Sauter Head Revolver for LinuxCNC

By Alexander Richter, info@theartoftinkering.com 2022  
please consider supporting me on Patreon:  
https://www.patreon.com/theartoftinkering  

Website: https://theartoftinkering.com  
Youtube: https://youtube.com/@theartoftinkering


This is a little script to manage Toolchages useing the Hydraulic Head Revolver of an old Weiler Primus CNC machine I am retrofitting. 

# Compatiblity
This software works with LinuxCNC 2.8, 2.9 and 2.10. For 2.8 however you have to change #!/usr/bin/python3.9 in the first line of arduino.py to #!/usr/bin/python2.7.

# Installation
1. edit headrevolver.py to find your tool.tbl file.
2. make headrevolver.py executable with chmod +x, delete the suffix .py and copy
it to /usr/bin  
    ```sudo chmod +x headrevolver.py  ```  
    ```sudo cp headrevolver.py /usr/bin/headrevolver  ```  

3. add this entry to the end of your hal file: ```loadusr headrevolver```  

4. you should now see new Pins created in your hal, which you can connect to your settings. Have a look at hal_example for reference. 

# License
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
