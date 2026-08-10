# Autors: Marco Zennaro - Fabio Bruschi

# Imports
import numpy as np
from DoublyLinkedList import *
from settings import *


# STARTING MENU VARIABLES ####################################################
save_found = False
world_loaded = False
DEV = False


# MAIN OBJECTS ###############################################################
anim = None
world = np.empty((NUMCELL, NUMCELL), dtype=object)


# WORLD VARIABLES ############################################################
global_day = 0
group_count_p = 0
group_count_h = 0


# SAVE OBJECTS ###############################################################
data_save = DoublyLinkedList()
image_save = DoublyLinkedList()
world_save = DoublyLinkedList()


# PLOTTING VARIABLES #########################################################
current_day = 0
current_data = None
current_image = None
current_world = None


# SCREEN VARIABLES ###########################################################
world_running = False

world_screen = False
vegetob_screen = False
population_screen = False
graph_screen = False
save_screen = True
