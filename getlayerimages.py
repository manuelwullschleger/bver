# -------------------------------------------------
# Title: Plots and stores each layer of a gcode file
# Author: Manuel Wullschleger & Marc Röthlisberger
# Date: 12-06-2020
# Version: 1.0
# Availability: https://gitlab.fhnw.ch/manuel.wullschleger/bverproject
# -------------------------------------------------

import matplotlib.pyplot as plt
import os.path
from gcode_reader import GcodeReader

def createLayerImages(gcodePath, destinationPath, printProgress):
    reader = GcodeReader(gcodePath)
    fig = None
    ax = None

    for i in range(1,reader.n_layers+1):
        if(printProgress):
            print("Layer " + str(i) + "/" + str(reader.n_layers))
        fig, ax = reader.plot_layer(i, ax=ax, fig=fig, linewidth=2.5)
        ax.set_ylim(0, 223) #buildplate hight in mm
        ax.set_xlim(0, 223) #buildplate width in mm
        # remove borders of plot ->
        plt.gca().set_axis_off()
        plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
        plt.margins(0,0)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.axis('off')
        # <- remove borders end
        
        #save image
        dest = os.path.join(destinationPath, str(i)+ ".png")
        plt.savefig(dest, bbox_inches = 'tight', pad_inches = 0)
