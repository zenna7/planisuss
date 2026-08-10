# Autors: Marco Zennaro - Fabio Bruschi

# Imports
import os
import numpy as np
import matplotlib.pyplot as plt
import GlobalVariables
from Classes import *


# WORLD GENERATION ###########################################################
def generateWorld():
    GlobalVariables.global_day = 0

    for i in range(NUMCELL):
        for j in range(NUMCELL):
            if i == 0 or i == NUMCELL - 1 or j == 0 or j == NUMCELL - 1:
                GlobalVariables.world[i, j] = Cell(i, j)
                GlobalVariables.world[i, j].setWater()
            else:
                GlobalVariables.world[i, j] = Cell(i, j, random.randint(1, 70))
    generateAnimal()


def generateAnimal():
    for i in range(1, NUMCELL - 1):
        for j in range(1, NUMCELL - 1):
            if not GlobalVariables.world[i, j].isWater:
                prob = random.randint(0, 3)
                if prob == 1:
                    prob = random.randint(0, 6)
                    # spawn of a pride
                    if prob < 1:
                        density = random.randint(2, SPAWN_MAX_C)
                        population = [Carviz(f"{0}C{i}-{j}{chr(k + 97)}") for k in range(density)]
                        GlobalVariables.world[i, j].setPopulation(Pride(f"C{GlobalVariables.group_count_p}",
                                                                        population))
                        GlobalVariables.group_count_p += 1
                    # spawn of a herd
                    elif prob < 2:
                        density = random.randint(2, SPAWN_MAX_E)
                        population = [Erbast(f"{0}E{i}-{j}{chr(k + 97)}") for k in range(density)]
                        GlobalVariables.world[i, j].setPopulation(Herd(f"C{GlobalVariables.group_count_h}",
                                                                       population))
                        GlobalVariables.group_count_h += 1
                    # spawn of a single carviz
                    elif prob < 4:
                        GlobalVariables.world[i, j].setPopulation(Carviz(f"{0}C{i}-{j}/"))
                    # spawn of a single erbast
                    else:
                        GlobalVariables.world[i, j].setPopulation(Erbast(f"{0}E{i}-{j}/"))


# DAY PHASES ON PLANISUSS ####################################################
def planisussDay():
    world_help = np.empty((NUMCELL, NUMCELL), dtype=object)

    # Loop through the world and move the population of each cell
    for i in range(1, NUMCELL - 1):
        for j in range(1, NUMCELL - 1):
            if not GlobalVariables.world[i, j].isWater:
                GlobalVariables.world[i, j].increaseVeg()
                entity = GlobalVariables.world[i, j].population
                if entity:
                    moveAnimals(GlobalVariables.world[i, j], entity, world_help)

    # Loop through the world and check the population of each cell
    for i in range(1, NUMCELL - 1):
        for j in range(1, NUMCELL - 1):
            current_population = world_help[i, j]
            population = None

            # Check if the cell is empty
            if current_population:
                population = current_population.checkDeath()

            if population:
                # increase the age of each entity
                population.increaseDayLived()
                if isinstance(population, Animal):
                    new_population = population.birth(GlobalVariables.world[i, j])
                    if new_population:
                        while len(new_population) > 1:
                            entity1 = new_population.pop()
                            entity2 = new_population.pop()
                            merge = mergeEntities(entity1, entity2)
                            entity3 = merge[0]
                            new_population.append(entity3)
                        world_help[i, j] = new_population[0]

                else:
                    birth = population.birth(GlobalVariables.world[i, j])
                    if birth:
                        group, extra_entity = birth[0], birth[1]
                        world_help[i, j] = group

                        if extra_entity:
                            for animal in extra_entity:
                                moveAnimals(GlobalVariables.world[i, j], animal, world_help,
                                            exclude_cell=GlobalVariables.world[i, j])

    for i in range(1, NUMCELL - 1):
        for j in range(1, NUMCELL - 1):
            if not GlobalVariables.world[i, j].isWater:
                GlobalVariables.world[i, j].setPopulation(world_help[i, j])


def moveAnimals(cell, entity, world_help, exclude_cell=None):
    # pick the surrounding cells
    neighbourhoodCells = cell.getNeighbours()
    entity_list = entity.nextMove(neighbourhoodCells)

    while entity_list:
        entity, newCoords = entity_list.pop()
        if world_help[newCoords] is None:
            world_help[newCoords] = entity
        else:
            current_entity = world_help[newCoords]
            cell_entities = cellContested(current_entity, entity)
            new_entity, extra_entity = cell_entities[0], cell_entities[1]
            world_help[newCoords] = new_entity
            if extra_entity:
                moveAnimals(cell, extra_entity, world_help, exclude_cell=GlobalVariables.world[newCoords])


def cellContested(entity1, entity2):
    if decideFight(entity1, entity2):
        return fight(entity1, entity2), None
    else:
        return mergeEntities(entity1, entity2)


def decideFight(entity1, entity2):
    if isinstance(entity1, Pride) and isinstance(entity2, Pride):
        if abs(entity1.averageEnergy() - entity2.averageEnergy()) > 40:
            return True

    if isinstance(entity1, Carviz) and isinstance(entity2, Carviz):
        if abs(entity1.energy - entity2.energy) > 40:
            return True

    if isinstance(entity1, Carviz) and isinstance(entity2, Erbast):
        return True

    if isinstance(entity1, Erbast) and isinstance(entity2, Carviz):
        return True

    if isinstance(entity1, Carviz) and isinstance(entity2, Herd):
        return True

    if isinstance(entity1, Herd) and isinstance(entity2, Carviz):
        return True

    if (isinstance(entity1, Pride) and isinstance(entity2, Carviz) or
            isinstance(entity1, Carviz) and isinstance(entity2, Pride)):
        if isinstance(entity1, Carviz):
            entity1, entity2 = entity2, entity1
        if entity1.populationSize() > 2 and abs(entity1.averageEnergy() - entity2.energy) > 35:
            return True

    if isinstance(entity1, Pride) and isinstance(entity2, Herd):
        return True

    if isinstance(entity1, Herd) and isinstance(entity2, Pride):
        return True

    if isinstance(entity1, Pride) and isinstance(entity2, Erbast):
        return True

    if isinstance(entity1, Erbast) and isinstance(entity2, Pride):
        return True

    return False


def mergeEntities(entity1, entity2):
    if isinstance(entity1, Animal):
        entity1, entity2 = entity2, entity1

    if isinstance(entity1, Pride):
        if isinstance(entity2, Carviz):
            if entity1.addAnimal(entity2):
                return entity1, None
            else:
                return entity1, entity2
        if isinstance(entity2, Pride):
            final_entity = Pride(f"P{GlobalVariables.group_count_p}", entity1.population + entity2.population)
            GlobalVariables.group_count_p += 1
            return final_entity, None

    if isinstance(entity1, Herd):
        if isinstance(entity2, Erbast):
            if entity1.addAnimal(entity2):
                return entity1, None
            else:
                return entity1, entity2
        if isinstance(entity2, Herd):
            final_entity = Herd(f"H{GlobalVariables.group_count_h}", entity1.population + entity2.population)
            GlobalVariables.group_count_h += 1
            return final_entity, None

    if isinstance(entity1, Carviz):
        final_entity = Pride(f"C{GlobalVariables.group_count_p}", [entity1, entity2])
        GlobalVariables.group_count_p += 1
        return final_entity, None

    if isinstance(entity1, Erbast):
        final_entity = Herd(f"H{GlobalVariables.group_count_h}", [entity1, entity2])
        GlobalVariables.group_count_h += 1
        return final_entity, None


def fight(entity1, entity2):
    if isinstance(entity1, Erbast) or isinstance(entity1, Herd):
        entity1, entity2 = entity2, entity1

    if isinstance(entity1, Carviz) and isinstance(entity2, Carviz):
        c1, c2 = entity1, entity2
        energy_diff = c1.energy - c2.energy
        win_prob_c1 = 50 + int(energy_diff / 2)
        c1_win = 0
        c2_win = 0
        for i in range(3):
            prob = random.randint(0, 100)
            if prob <= win_prob_c1:
                c1_win += 1
            else:
                c2_win += 1
        if c1_win > c2_win:
            c2.kill()
            c1.gainEnergy(CAR_EAT_ENERGY_GAIN)
            return c1
        else:
            c1.kill()
            c2.gainEnergy(CAR_EAT_ENERGY_GAIN)
            return c2

    if isinstance(entity1, Carviz) and isinstance(entity2, Erbast):
        carviz, erbast = entity1, entity2
        c_energy = carviz.energy
        e_energy = int(erbast.energy / 2)
        if c_energy < e_energy:
            c_energy = int(c_energy * 1.5)
        energy_diff = c_energy - e_energy
        if energy_diff < 0:
            energy_diff = int(energy_diff * 0.8)
        else:
            energy_diff = int(energy_diff * 1.2)

        win_prob_c = 55 + int(energy_diff / 2)
        c_win = 0
        e_win = 0
        for i in range(3):
            prob = random.randint(0, 100)
            if prob <= win_prob_c:
                c_win += 1
            else:
                e_win += 1
        if c_win > e_win:
            erbast.kill()
            carviz.gainEnergy()
            return carviz
        else:
            carviz.kill()
            erbast.loseEnergy(FIGHT_ENERGY_LOSS_E)
            return erbast

    if isinstance(entity1, Carviz) and isinstance(entity2, Herd):
        carviz, herd = entity1, entity2
        if herd.populationSize() > 2:
            for erbast in herd.population:
                erbast.loseEnergy(FIGHT_ENERGY_LOSS_E)
            carviz.kill()
            return herd
        else:
            while herd.population and not carviz.isDead():
                erbast = herd.population.pop(0)
                winner = fight(carviz, erbast)
                if isinstance(winner, Erbast):
                    herd.addAnimal(winner)
            if carviz.isDead():
                return herd
            else:
                return carviz

    if isinstance(entity1, Pride) and isinstance(entity2, Carviz):
        pride, carviz = entity1, entity2
        for c in pride.population:
            c.gainEnergy(CAR_EAT_ENERGY_GAIN)
        carviz.kill()
        return pride

    if isinstance(entity1, Pride) and isinstance(entity2, Pride):
        pride1, pride2 = entity1, entity2
        while pride1.population and pride2.population:
            carviz1 = pride1.population.pop(0)
            carviz2 = pride2.population.pop(0)
            winner = fight(carviz1, carviz2)
            if winner == carviz1:
                pride1.addAnimal(winner)
            else:
                pride2.addAnimal(winner)
        if pride1.population:
            return pride1
        else:
            return pride2

    if isinstance(entity1, Pride) and isinstance(entity2, Herd):
        pride, herd = entity1, entity2
        if herd.populationSize() > (pride.populationSize() * 1.3):
            while pride.population and herd.population:
                carviz = pride.population.pop(0)
                erbast = herd.population.pop(0)
                winner = fight(carviz, erbast)
                if isinstance(winner, Erbast):
                    herd.addAnimal(winner)
                else:
                    pride.addAnimal(winner)
            if pride.population:
                return pride
            else:
                return herd
        else:
            for erbast in herd.population:
                erbast.kill()
            for carviz in pride.population:
                carviz.gainEnergy(ERB_EAT_ENERGY_GAIN)
            return pride

    if isinstance(entity1, Pride) and isinstance(entity2, Erbast):
        pride, erbast = entity1, entity2
        for carviz in pride.population:
            carviz.gainEnergy(ERB_EAT_ENERGY_GAIN / 2)
            if carviz.energy < 10:
                carviz.energy = 10
        erbast.kill()
        return pride


# WORLD MANAGEMENT ###########################################################
def simulation(i):
    if i != 0:
        planisussDay()
        GlobalVariables.global_day += 1

    # Flag to allow for printing the sorld as a string
    worldToString()
    w_RGB = worldConverter()

    plt.cla()
    plt.imshow(w_RGB)
    plt.title("Running: Day " + str(GlobalVariables.global_day))
    plt.xticks([])
    plt.yticks([])


def worldConverter():
    world_rgb = np.zeros((NUMCELL, NUMCELL, 3), dtype=float)

    vegetob_density_tot = 0
    c_tot = 0
    e_tot = 0
    c_indiv_tot = 0
    e_indiv_tot = 0
    p_tot = 0
    h_tot = 0

    for i in range(NUMCELL):
        for j in range(NUMCELL):
            world_rgb[i, j] = GlobalVariables.world[i, j].getColor()

            vegetob_density_tot += GlobalVariables.world[i, j].getVegetobDensity()
            entity = GlobalVariables.world[i, j].population
            if entity:
                if isinstance(entity, Carviz):
                    c_tot += 1
                    c_indiv_tot += 1
                if isinstance(entity, Erbast):
                    e_tot += 1
                    e_indiv_tot += 1
                if isinstance(entity, Pride):
                    p_tot += 1
                    c_tot += entity.populationSize()
                if isinstance(entity, Herd):
                    h_tot += 1
                    e_tot += entity.populationSize()

    save = {"global_vegetob_densisty": round(vegetob_density_tot / (NUMCELL * NUMCELL), 2),
            "carviz_tot": c_tot,
            "erbast_tot": e_tot,
            "carviz_indiv": c_indiv_tot,
            "erbast_indiv": e_indiv_tot,
            "carviz_group": c_tot - c_indiv_tot,
            "erbast_group": e_tot - e_indiv_tot,
            "pride_tot": p_tot,
            "herd_tot": h_tot}

    GlobalVariables.data_save.addDayData(GlobalVariables.global_day, save)
    GlobalVariables.image_save.addDayData(GlobalVariables.global_day, world_rgb)
    GlobalVariables.world_save.addDayData(GlobalVariables.global_day, GlobalVariables.world)

    return world_rgb


def worldToString():
    print("Day " + str(GlobalVariables.global_day) + " ########################################################")
    for i in range(NUMCELL):
        for j in range(NUMCELL):
            print(GlobalVariables.world[i, j])
    print("##############################################################\n")


# SCREEN AND MENU ############################################################
def navigateAnimation(event):
    if event.key == " ":
        if GlobalVariables.world_running:
            GlobalVariables.anim.pause()
            GlobalVariables.world_running = False
            GlobalVariables.current_day = GlobalVariables.global_day
            GlobalVariables.current_data = GlobalVariables.data_save.getLast()
            GlobalVariables.current_image = GlobalVariables.image_save.getLast()
            GlobalVariables.current_world = GlobalVariables.world_save.getLast()
            updateScreen()
        else:
            plt.clf()
            GlobalVariables.anim.resume()
            GlobalVariables.world_running = True
            GlobalVariables.world_screen = True
            GlobalVariables.vegetob_screen = False
            GlobalVariables.population_screen = False
            GlobalVariables.graph_screen = False

    if event.key == "v" and not GlobalVariables.world_running and not GlobalVariables.save_screen:
        if GlobalVariables.vegetob_screen:
            GlobalVariables.world_screen = True
            GlobalVariables.vegetob_screen = False
            GlobalVariables.population_screen = False
            GlobalVariables.graph_screen = False
        else:
            GlobalVariables.world_screen = False
            GlobalVariables.vegetob_screen = True
            GlobalVariables.population_screen = False
            GlobalVariables.graph_screen = False
        updateScreen()

    if event.key == "w" and not GlobalVariables.world_running and not GlobalVariables.save_screen:
        GlobalVariables.world_screen = True
        GlobalVariables.vegetob_screen = False
        GlobalVariables.population_screen = False
        GlobalVariables.graph_screen = False
        updateScreen()

    if event.key == "p" and not GlobalVariables.world_running and not GlobalVariables.save_screen:
        if GlobalVariables.population_screen:
            GlobalVariables.world_screen = True
            GlobalVariables.vegetob_screen = False
            GlobalVariables.population_screen = False
            GlobalVariables.graph_screen = False
        else:
            GlobalVariables.world_screen = False
            GlobalVariables.vegetob_screen = False
            GlobalVariables.population_screen = True
            GlobalVariables.graph_screen = False
        updateScreen()

    if event.key == "g" and not GlobalVariables.world_running and not GlobalVariables.save_screen:
        if GlobalVariables.graph_screen:
            GlobalVariables.world_screen = True
            GlobalVariables.vegetob_screen = False
            GlobalVariables.population_screen = False
            GlobalVariables.graph_screen = False
        else:
            GlobalVariables.world_screen = False
            GlobalVariables.vegetob_screen = False
            GlobalVariables.population_screen = False
            GlobalVariables.graph_screen = True
        updateScreen()

    if event.key == "x" and not GlobalVariables.world_running:
        if GlobalVariables.save_screen:
            GlobalVariables.world_screen = True
            GlobalVariables.vegetob_screen = False
            GlobalVariables.population_screen = False
            GlobalVariables.graph_screen = False
            GlobalVariables.save_screen = False
        else:
            GlobalVariables.world_screen = False
            GlobalVariables.vegetob_screen = False
            GlobalVariables.population_screen = False
            GlobalVariables.graph_screen = False
            GlobalVariables.save_screen = True
        updateScreen()

    if event.key == "y" and not GlobalVariables.world_running and GlobalVariables.save_screen:
        np.save("world_save.npy", GlobalVariables.current_world.getData())
        with open("day_save.txt", "w") as f:
            text = (f"This file contains some data of the last save.\n"
                    f"{str(GlobalVariables.current_day)}\n"
                    f"{str(GlobalVariables.group_count_p)}\n"
                    f"{str(GlobalVariables.group_count_h)}\n")
            f.write(text)
        plt.cla()
        plt.clf()
        plt.text(0.5, 0.5, "World saved! Press any button to exit", horizontalalignment="center",
                 verticalalignment="center", fontsize=20)
        plt.xticks([])
        plt.yticks([])
        plt.box(False)
        plt.draw()
        plt.waitforbuttonpress()
        GlobalVariables.world_screen = True
        GlobalVariables.save_screen = False
        updateScreen()

    if event.key == "n" and not GlobalVariables.world_running and GlobalVariables.save_screen:
        plt.clf()
        plt.cla()
        plt.text(0.5, 0.5, "Nothing saved. Press any button to exit", horizontalalignment="center",
                 verticalalignment="center", fontsize=20)
        plt.xticks([])
        plt.yticks([])
        plt.box(False)
        plt.draw()
        plt.waitforbuttonpress()
        GlobalVariables.world_screen = True
        GlobalVariables.save_screen = False
        updateScreen()

    if event.key == "left" and not GlobalVariables.world_running:
        if GlobalVariables.current_day > GlobalVariables.global_day - GlobalVariables.data_save.size() + 1:
            GlobalVariables.current_day -= 1
            GlobalVariables.current_image = GlobalVariables.current_image.getPrev()
            GlobalVariables.current_data = GlobalVariables.current_data.getPrev()
            GlobalVariables.current_world = GlobalVariables.current_world.getPrev()
            updateScreen()

    if event.key == "right" and not GlobalVariables.world_running:
        if GlobalVariables.current_day < GlobalVariables.global_day:
            GlobalVariables.current_day += 1
            GlobalVariables.current_image = GlobalVariables.current_image.getNext()
            GlobalVariables.current_data = GlobalVariables.current_data.getNext()
            GlobalVariables.current_world = GlobalVariables.current_world.getNext()
            updateScreen()


def updateScreen():
    plt.cla()

    if GlobalVariables.world_screen:
        plt.clf()
        plt.subplot(1, 1, 1)
        plt.imshow(GlobalVariables.current_image.getData())
        plt.title("Paused: Day " + str(GlobalVariables.current_day))
        plt.xticks([])
        plt.yticks([])

    elif GlobalVariables.save_screen:
        plt.clf()
        plt.suptitle("Save Menu")
        plt.subplot(2, 1, 1)
        text = '''Do you want to save the following world?
(Use [<] and [>] to navigate between days)
[Y]es    [N]o'''
        plt.text(0.5, 0.5, text, horizontalalignment="center", verticalalignment="center", fontsize=20)
        plt.xticks([])
        plt.yticks([])
        plt.box(False)

        plt.subplot(2, 1, 2)
        plt.imshow(GlobalVariables.current_image.getData())
        plt.title("You are saving: Day " + str(GlobalVariables.current_day))
        plt.xticks([])
        plt.yticks([])

    else:
        days = GlobalVariables.data_save.getFirst()
        x_values = []
        while days:
            x_values.append(days.getDay())
            days = days.getNext()

        y_veg = []
        y_ctot, y_cind = [], []
        y_etot, y_eind = [], []
        y_ptot, y_cgroup = [], []
        y_htot, y_egroup = [], []

        data = GlobalVariables.data_save.getFirst()
        while data:
            y_veg.append(data.getData("global_vegetob_densisty"))
            y_ctot.append(data.getData("carviz_tot"))
            y_cind.append(data.getData("carviz_indiv"))
            y_etot.append(data.getData("erbast_tot"))
            y_eind.append(data.getData("erbast_indiv"))
            y_cgroup.append(data.getData("carviz_group"))
            y_egroup.append(data.getData("erbast_group"))
            y_ptot.append(data.getData("pride_tot"))
            y_htot.append(data.getData("herd_tot"))
            data = data.getNext()

        if GlobalVariables.vegetob_screen:
            plt.clf()
            plt.subplot(1, 1, 1)
            if GlobalVariables.global_day < MAX_DAY_STORAGE:
                plt.axis([x_values[0] - 0.5, MAX_DAY_STORAGE + 1, min(y_veg) - 2, max(y_veg) + 15])
            else:
                plt.axis([x_values[0] - 0.5, x_values[-1] + 1, min(y_veg) - 2, max(y_veg) + 15])

            plt.plot(x_values, y_veg, color="green", label="")
            plt.plot(GlobalVariables.current_data.getDay(),
                     GlobalVariables.current_data.getData("global_vegetob_densisty"), "go",
                     label=str(GlobalVariables.current_data.getData("global_vegetob_densisty")))
            plt.title("Vegetob Informations")
            plt.legend(loc="upper left")
            plt.xlabel("Day")
            plt.ylabel("Vegetob density")
            plt.grid(True, axis="y", linestyle=":", alpha=0.4)

        if GlobalVariables.population_screen:
            plt.clf()
            plt.suptitle("Population Informations")
            plt.subplot(2, 2, 1)
            plt.cla()
            if GlobalVariables.global_day < MAX_DAY_STORAGE:
                plt.axis([x_values[0] - 0.5, MAX_DAY_STORAGE + 0.5,
                          min(min(y_eind), min(y_cind)) - 10, max(max(y_ctot), max(y_etot)) + 30])
            else:
                plt.axis([x_values[0] - 0.5, x_values[-1] + 0.5,
                          min(min(y_eind), min(y_cind)) - 10, max(max(y_ctot), max(y_etot)) + 30])

            plt.plot(x_values, y_ctot, color="red", label="")  # carviz tot
            plt.plot(x_values, y_cind, color="red", label="")  # carviz indiv
            plt.plot(GlobalVariables.current_data.getDay(),
                     GlobalVariables.current_data.getData("carviz_tot"), "rs",
                     label=f"Total: {str(GlobalVariables.current_data.getData('''carviz_tot'''))}")
            plt.plot(GlobalVariables.current_data.getDay(),
                     GlobalVariables.current_data.getData("carviz_indiv"), "ro",
                     label=f"Alone: {str(GlobalVariables.current_data.getData('''carviz_indiv'''))}")
            plt.title("Carviz Informations")
            plt.legend(loc="upper left")
            plt.xlabel("")
            plt.ylabel("Number")
            plt.grid(True, axis="y", linestyle=":", alpha=0.4)

            plt.subplot(2, 2, 2)
            plt.cla()
            if GlobalVariables.global_day < MAX_DAY_STORAGE:
                plt.axis([x_values[0] - 0.5, MAX_DAY_STORAGE + 0.5,
                          min(min(y_eind), min(y_cind)) - 10, max(max(y_ctot), max(y_etot)) + 30])
            else:
                plt.axis([x_values[0] - 0.5, x_values[-1] + 0.5,
                          min(min(y_eind), min(y_cind)) - 10, max(max(y_ctot), max(y_etot)) + 30])

            plt.plot(x_values, y_etot, color="blue", label="")  # erbast tot
            plt.plot(x_values, y_eind, color="blue", label="")  # erbast indiv
            plt.plot(GlobalVariables.current_data.getDay(),
                     GlobalVariables.current_data.getData("erbast_tot"), "bs",
                     label=f"Total: {str(GlobalVariables.current_data.getData('''erbast_tot'''))}")
            plt.plot(GlobalVariables.current_data.getDay(),
                     GlobalVariables.current_data.getData("erbast_indiv"), "bo",
                     label=f"Alone: {str(GlobalVariables.current_data.getData('''erbast_indiv'''))}")
            plt.title("Erbast Informations")
            plt.legend(loc="upper left")
            plt.xlabel("")
            plt.ylabel("")
            plt.grid(True, axis="y", linestyle=":", alpha=0.4)

            plt.subplot(2, 2, 3)
            plt.cla()
            if GlobalVariables.global_day < MAX_DAY_STORAGE:
                plt.axis([x_values[0] - 0.5, MAX_DAY_STORAGE + 0.5,
                          min(min(y_htot), min(y_ptot)) - 5, max(max(y_egroup), max(y_cgroup)) + 30])
            else:
                plt.axis([x_values[0] - 0.5, x_values[-1] + 0.5,
                          min(min(y_htot), min(y_ptot)) - 5, max(max(y_egroup), max(y_cgroup)) + 30])

            plt.bar(x_values, y_ptot, color="pink", width=0.5, align="edge")  # pride tot
            plt.bar(x_values, y_cgroup, color="red", width=-0.5, align="edge")  # carviz in group
            plt.plot(GlobalVariables.current_data.getDay() - 0.25,
                     GlobalVariables.current_data.getData("carviz_group"), "mD",
                     label=f"Carviz in Prides: {str(GlobalVariables.current_data.getData('''carviz_group'''))}")
            plt.plot(GlobalVariables.current_data.getDay() + 0.25,
                     GlobalVariables.current_data.getData("pride_tot"), "rD",
                     label=f"Number of Pride: {str(GlobalVariables.current_data.getData('''pride_tot'''))}")
            plt.title("Pride Informations")
            plt.legend(loc="upper left")
            plt.xlabel("Day")
            plt.ylabel("Number")
            plt.grid(True, axis="y", linestyle=":", alpha=0.4)

            plt.subplot(2, 2, 4)
            plt.cla()
            if GlobalVariables.global_day < MAX_DAY_STORAGE:
                plt.axis([x_values[0] - 0.5, MAX_DAY_STORAGE + 0.5,
                          min(min(y_htot), min(y_ptot)) - 5, max(max(y_egroup), max(y_cgroup)) + 30])
            else:
                plt.axis([x_values[0] - 0.5, x_values[-1] + 0.5,
                          min(min(y_htot), min(y_ptot)) - 5, max(max(y_egroup), max(y_cgroup)) + 30])

            plt.bar(x_values, y_htot, color="cyan", width=0.5, align="edge")  # herd tot
            plt.bar(x_values, y_egroup, color="blue", width=-0.5, align="edge")  # erbast in group
            plt.plot(GlobalVariables.current_data.getDay() - 0.25,
                     GlobalVariables.current_data.getData("erbast_group"), "mD",
                     label=f"Erbast in Herds: {str(GlobalVariables.current_data.getData('''erbast_group'''))}")
            plt.plot(GlobalVariables.current_data.getDay() + 0.25,
                     GlobalVariables.current_data.getData("herd_tot"), "bD",
                     label=f"Number of Herd: {str(GlobalVariables.current_data.getData('''herd_tot'''))}")
            plt.title("Herd Informations")
            plt.legend(loc="upper left")
            plt.xlabel("Day")
            plt.ylabel("")
            plt.grid(True, axis="y", linestyle=":", alpha=0.4)

        if GlobalVariables.graph_screen:
            plt.clf()
            plt.suptitle("General Informations")
            grid = plt.GridSpec(1, 4, wspace=0.4, width_ratios=[9, 1, 1, 1])

            plt.subplot(grid[0, 0])
            if GlobalVariables.global_day < MAX_DAY_STORAGE:
                plt.axis([x_values[0] - 0.5, MAX_DAY_STORAGE + 0.5, 0,
                          max(max(y_ctot), max(y_etot), max(y_veg)) + 30])
            else:
                plt.axis([x_values[0] - 0.5, x_values[-1] + 0.5, 0,
                          max(max(y_ctot), max(y_etot), max(y_veg)) + 30])

            plt.plot(GlobalVariables.current_data.getDay(), 0, "kD",
                     label="Day: " + str(GlobalVariables.current_data.getDay()))  # day tracker
            plt.plot(x_values, y_ctot, color="red", label="Carviz")  # carviz
            plt.plot(x_values, y_etot, color="blue", label="Erbast")  # erbast
            plt.plot(x_values, y_veg, color="green", label="Erbast")  # vegetob
            plt.plot(x_values, y_ptot, color="hotpink", label="Pride")  # pride
            plt.plot(x_values, y_htot, color="cyan", label="Herd")  # herd
            plt.title("Graph")
            plt.legend(loc="upper left")
            plt.xlabel("Day " + str(GlobalVariables.current_data.getDay()))
            plt.xticks([])
            plt.ylabel("Number")
            plt.grid(True, axis="y", linestyle=":", alpha=0.4)

            plt.subplot(grid[0, 1])
            plt.bar(GlobalVariables.current_data.getDay(), GlobalVariables.current_data.getData("carviz_tot"),
                    color="red",  width=-0.5, align="edge")  # carviz tot
            plt.bar(GlobalVariables.current_data.getDay(), GlobalVariables.current_data.getData("erbast_tot"),
                    color="blue",  width=0.5, align="edge")  # erbast tot
            plt.title("Carviz - Erbast")
            plt.xlabel("")
            plt.xticks([])
            plt.ylabel("")
            plt.yticks([GlobalVariables.current_data.getData("carviz_tot"),
                        GlobalVariables.current_data.getData("erbast_tot")],
                       [str(GlobalVariables.current_data.getData("carviz_tot")),
                        str(GlobalVariables.current_data.getData("erbast_tot"))])
            plt.ylim(top=max(max(y_ctot), max(y_etot), max(y_veg)) + 30)

            plt.subplot(grid[0, 2])
            plt.bar(GlobalVariables.current_data.getDay(), GlobalVariables.current_data.getData("pride_tot"),
                    color="hotpink", width=-0.5, align="edge")  # pride tot
            plt.bar(GlobalVariables.current_data.getDay(), GlobalVariables.current_data.getData("herd_tot"),
                    color="cyan", width=0.5, align="edge")  # herd tot
            plt.title("Pride - Herd")
            plt.xticks([])
            plt.ylabel("")
            plt.yticks([GlobalVariables.current_data.getData("pride_tot"),
                        GlobalVariables.current_data.getData("herd_tot")],
                       [str(GlobalVariables.current_data.getData("pride_tot")),
                        str(GlobalVariables.current_data.getData("herd_tot"))])
            plt.ylim(top=max(max(y_ctot), max(y_etot), max(y_veg)) + 30)

            plt.subplot(grid[0, 3])
            plt.bar(GlobalVariables.current_data.getDay(),
                    GlobalVariables.current_data.getData("global_vegetob_densisty"), color="green")  # veg tot
            plt.title("Vegetob")
            plt.xlabel("")
            plt.xticks([])
            plt.ylabel("")
            plt.yticks([GlobalVariables.current_data.getData("global_vegetob_densisty")],
                       [str(GlobalVariables.current_data.getData("global_vegetob_densisty"))])
            plt.ylim(top=100)

    plt.draw()


def startingMenu():
    if os.path.exists("world_save.npy") and os.path.exists("day_save.txt"):
        GlobalVariables.save_found = True

    fig = plt.figure(figsize=(10, 6))
    fig.canvas.manager.set_window_title('Starting menu')
    fig.canvas.mpl_connect('key_press_event', loadMenu)

    string = '''Welcome to Planisuss!
The simulation runs automatically. 
To pause and resume it press [SPACE]
------------------------------------------------------
Commands when paused:
    [V] to see the vegetob density GlobalVariables days
    [P] to see the informations about the population 
    [G] to see the general overview
    [W] to see the world
    [X] to save the world
    [<] and [>] to navigate between days
------------------------------------------------------
'''
    if GlobalVariables.save_found:
        text = string + '''Save in memory found!
Press [L] to load
Press [D] to open the developer menu
[Close] to start a new simulation'''
        plt.text(0.01, 0.5, text, horizontalalignment="left", verticalalignment="center", fontsize=20)
    else:
        text = string + '''No save in memory found
Press [D] to activate the developer menu
[Close] to start a new simulation'''
        plt.text(0.01, 0.5, text, horizontalalignment="left", verticalalignment="center", fontsize=20)
    plt.xticks([])
    plt.yticks([])
    plt.box(False)
    plt.show()
    GlobalVariables.world_screen = True
    GlobalVariables.save_screen = False
    GlobalVariables.world_running = True


def loadMenu(event):
    if event.key == "l" and GlobalVariables.save_found:
        GlobalVariables.world = np.load("world_save.npy", allow_pickle=True)
        with open("day_save.txt", "r") as f:
            lines = f.readlines()
            GlobalVariables.global_day = int(lines[1].strip("\n"))
            GlobalVariables.group_count_p = int(lines[2].strip("\n"))
            GlobalVariables.group_count_h = int(lines[3].strip("\n"))
        GlobalVariables.world_loaded = True
        plt.cla()
        plt.clf()
        text = '''World Loaded!
[Close] to start the simulation'''
        plt.text(0.5, 0.5, text,  horizontalalignment="center", verticalalignment="center", fontsize=20)
        plt.xticks([])
        plt.yticks([])
        plt.box(False)
        GlobalVariables.world_screen = True
        GlobalVariables.save_screen = False
        GlobalVariables.world_running = True
        plt.draw()

    if event.key == "d":
        plt.clf()
        plt.cla()
        text = '''Developer menu activated!
[Close] and update the console to start'''
        plt.text(0.5, 0.5, text, horizontalalignment="center", verticalalignment="center", fontsize=20)
        plt.xticks([])
        plt.yticks([])
        plt.box(False)
        plt.draw()
        GlobalVariables.world_screen = True
        GlobalVariables.save_screen = False
        GlobalVariables.world_running = True
        GlobalVariables.DEV = True


# DEVELOPER FUNCTIONS ########################################################
def generateWorldDEV():
    GlobalVariables.global_day = 0
    for i in range(NUMCELL):
        for j in range(NUMCELL):
            if i == 0 or i == NUMCELL - 1 or j == 0 or j == NUMCELL - 1:
                GlobalVariables.world[i, j] = Cell(i, j)
                GlobalVariables.world[i, j].setWater()
            else:
                GlobalVariables.world[i, j] = Cell(i, j, 60)
    generateAnimalDEV()


def generateAnimalDEV():
    world_number = int(input("Test world: "))
    match world_number:
        case 1:
            for cell in GlobalVariables.world[1:4, 2]:
                cell.setWater()
            GlobalVariables.world[2, 1].setPopulation(Erbast("2100"))
            GlobalVariables.world[2, 3].setPopulation(Erbast("2300"))
            GlobalVariables.world[3, 1].setVegetobDensity(100)
            GlobalVariables.world[1, 3].setVegetobDensity(100)

        case 2:
            GlobalVariables.world[1, 1].setWater()
            GlobalVariables.world[3, 3].setWater()
            GlobalVariables.world[2, 2].setPopulation(Erbast("2200"))
            GlobalVariables.world[1, 2].setVegetobDensity(100)

        case 3:
            GlobalVariables.world[1, 1].setWater()
            GlobalVariables.world[3, 3].setWater()
            GlobalVariables.world[2, 2].setPopulation(Carviz("2200"))
            GlobalVariables.world[1, 2].setVegetobDensity(100)

        case 4:
            GlobalVariables.world[1, 1].setWater()
            GlobalVariables.world[3, 1].setPopulation(Erbast("3100"))
            GlobalVariables.world[1, 3].setPopulation(Carviz("1300"))
            GlobalVariables.world[2, 2].setVegetobDensity(100)

        case 5:
            GlobalVariables.world[1, 1].setWater()
            GlobalVariables.world[1, 2].setPopulation(Erbast("1200"))
            GlobalVariables.world[3, 1].setPopulation(Erbast("3100"))
            GlobalVariables.world[2, 2].setVegetobDensity(100)

        case 6:
            GlobalVariables.world[1, 1].setWater()
            GlobalVariables.world[1, 2].setPopulation(Carviz("1200"))
            GlobalVariables.world[3, 1].setPopulation(Carviz("3100"))
            GlobalVariables.world[2, 2].setVegetobDensity(100)

        case 7:
            GlobalVariables.world[2, 1].setWater()
            GlobalVariables.world[2, 2].setPopulation(Erbast("2200"))
            GlobalVariables.world[2, 3].setPopulation(Carviz("3200"))
            GlobalVariables.world[1, 3].setVegetobDensity(100)

        case 8:
            GlobalVariables.world[1, 1].setPopulation(Erbast("1100"))
            GlobalVariables.world[1, 2].setPopulation(Erbast("1200"))
            GlobalVariables.world[1, 3].setPopulation(Erbast("1300"))
            GlobalVariables.world[2, 1].setPopulation(Erbast("2100"))
            GlobalVariables.world[2, 2].setVegetobDensity(100)
            GlobalVariables.world[2, 3].setPopulation(Erbast("2300"))
            GlobalVariables.world[3, 1].setPopulation(Erbast("3100"))
            GlobalVariables.world[3, 2].setPopulation(Erbast("3200"))
            GlobalVariables.world[3, 3].setPopulation(Herd("H1", [Erbast(f"{2}{1}{0}{k}") for k in range(3)]))

        case 9:
            GlobalVariables.world[2, 2].setVegetobDensity(100)
            GlobalVariables.world[1, 3].setPopulation(Pride("P1", [Carviz(f"{2}{1}{0}{k}") for k in range(3)]))
            GlobalVariables.world[3, 1].setPopulation(Pride("P2", [Carviz(f"{2}{1}{0}{k}") for k in range(3)]))

        case 10:
            GlobalVariables.world[2, 2].setVegetobDensity(100)
            GlobalVariables.world[1, 3].setPopulation(Herd("H1", [Erbast(f"{2}{1}{0}{k}") for k in range(3)]))
            GlobalVariables.world[3, 1].setPopulation(Herd("H2", [Erbast(f"{2}{1}{0}{k}") for k in range(3)]))

        case 11:
            GlobalVariables.world[2, 2].setVegetobDensity(100)
            GlobalVariables.world[1, 3].setPopulation(Carviz("1300"))
            GlobalVariables.world[3, 1].setPopulation(Pride("P1", [Carviz(f"{2}{1}{0}{k}") for k in range(3)]))

        case 12:
            GlobalVariables.world[2, 2].setVegetobDensity(100)
            GlobalVariables.world[1, 3].setPopulation(Erbast("1300"))
            GlobalVariables.world[3, 1].setPopulation(Pride("P1", [Carviz(f"{2}{1}{0}{k}") for k in range(3)]))

        case 13:
            GlobalVariables.world[2, 2].setVegetobDensity(100)
            GlobalVariables.world[1, 3].setPopulation(Pride("P1", [Carviz(f"{2}{1}{0}{k}") for k in range(3)]))
            GlobalVariables.world[3, 1].setPopulation(Erbast("1300"))

        case 14:
            GlobalVariables.world[2, 2].setVegetobDensity(100)
            GlobalVariables.world[1, 3].setPopulation(Pride("P1", [Carviz(f"{2}{1}{0}{k}") for k in range(3)]))
            GlobalVariables.world[3, 1].setPopulation(Herd("H1", [Erbast(f"{2}{1}{0}{k}") for k in range(3)]))
