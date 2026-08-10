# Autors: Marco Zennaro - Fabio Bruschi

# Imports
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import GlobalVariables
from Functions import *


# Main
def main():
    startingMenu()

    if not GlobalVariables.world_loaded:
        if GlobalVariables.DEV:
            generateWorldDEV()
        else:
            generateWorld()

    # Plotting settings
    fig = plt.figure(figsize=(15, 8))
    fig.canvas.manager.set_window_title('Planisuss')
    fig.canvas.mpl_connect('key_press_event', navigateAnimation)

    # Animation
    GlobalVariables.anim = animation.FuncAnimation(fig, func=simulation,
                                                   interval=150,
                                                   frames=75,
                                                   repeat=False,
                                                   init_func=lambda: None,
                                                   cache_frame_data=False)
    plt.show()


if __name__ == "__main__":
    main()
