import sys
import os

path = r"testprint6\testprint6p.gcode"
output = r"testprint6\testprint6.gcode"

lines = []
with open(path) as fp:
    lineNr = 0
    positioningLineNr = 0
    lookingForPosCords = False
    for line in fp:
        if(line == ";TimeLapse End\n"):
            lines.append("")
            positioningLineNr = lineNr
            lookingForPosCords = True
            lineNr += 1
        if(lookingForPosCords and line.startswith("G1 F")):
            lines[positioningLineNr] = line.split(" E",1)[0] + "\n"
            lookingForPosCords = False
        lines.append(line)
        lineNr += 1

with open(output, mode='wt', encoding='utf-8') as myfile:
        for line in lines:
            myfile.write(line)
