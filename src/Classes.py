# Autors: Marco Zennaro - Fabio Bruschi

# Imports
import random
import GlobalVariables
from settings import *


# CELL CLASS #################################################################
class Cell:
    def __init__(self, x, y, density=0):
        self.__Xcoordinate = x
        self.__Ycoordinate = y
        self.__vegetob_density = density
        self.isWater = False
        self.population = None
        self.__color = [0, 0, 0]

    def getCoords(self):
        return self.__Xcoordinate, self.__Ycoordinate

    def setWater(self):
        self.isWater = True
        self.__vegetob_density = 0
        self.__color = COLOR_WATER

    def increaseVeg(self):
        if isinstance(self.__vegetob_density, float):
            self.__vegetob_density = int(self.__vegetob_density) + 1
        else:
            self.__vegetob_density += GROWTH_RATE
        if self.__vegetob_density > MAX_DENSITY:
            self.__vegetob_density = MAX_DENSITY

    def decreaseVeg(self):
        self.__vegetob_density -= VEGETOB_EATEN
        if self.__vegetob_density < 0:
            self.__vegetob_density = 0

    def defineColor(self):
        if self.isWater:
            self.__color = COLOR_WATER
        else:
            if self.population:
                if isinstance(self.population, Carviz):
                    self.__color = COLOR_CARVIZ
                if isinstance(self.population, Erbast):
                    self.__color = COLOR_ERBAST
                if isinstance(self.population, Pride):
                    self.__color = COLOR_PRIDE
                if isinstance(self.population, Herd):
                    self.__color = COLOR_HERD
            else:
                green_tone = self.__vegetob_density / MAX_DENSITY
                if green_tone == 1:
                    self.__color = COLOR_MAX_VEGETOB
                elif green_tone < 0.09:
                    self.__color = COLOR_EARTH
                else:
                    self.__color = [0, green_tone, 0]

    def setColor(self, color):
        self.__color = color

    def getColor(self):
        self.defineColor()
        return self.__color

    def setPopulation(self, element):
        self.population = element

    def getPopulation(self):
        return self.population

    def setVegetobDensity(self, density):
        self.__vegetob_density = density

    def getVegetobDensity(self):
        return self.__vegetob_density

    def getNeighbours(self):
        neighbours = []
        x = self.__Xcoordinate
        y = self.__Ycoordinate
        for i in range(-1, 2):
            for j in range(-1, 2):
                neighbours.append(GlobalVariables.world[x + i, y + j])
        return neighbours

    def __str__(self):
        population_string = ""
        for line in str(self.population).splitlines():
            population_string += f'\t\t{line}\n'

        return (f'Cell: {self.__Xcoordinate}, {self.__Ycoordinate}\n'
                f'\tWater: {self.isWater}\n'
                f'\tVegetob: {self.__vegetob_density}%\n'
                f'\tPopulation: \n'
                f'{population_string}')


# ANIMAL CLASSES #############################################################
class Animal:
    def __init__(self, id):
        self.id = id
        self.energy = random.randint(MIN_ENERGY, MAX_ENERGY)
        self.max_energy = 100
        self.lifetime = random.randint(MIN_AGE, MAX_AGE)
        self.age = 0
        self.inAGroup = False
        self.social_attitude = 0
        self.__memory = []
        self.specie = None

    def increaseDayLived(self):
        if not self.isDead():
            self.age += 1
            self.max_energy = int(self.max_energy * (1 - (self.age / self.lifetime))) + 1

    def isDead(self):
        return self.energy <= 0

    def memorySize(self):
        return len(self.__memory)

    def getMemory(self):
        return self.__memory

    def getLastMemory(self):
        if self.memorySize() > 0:
            return self.__memory[-1]

    def addMemory(self, memory):
        self.__memory.append(memory)
        if self.memorySize() > MAX_DAY_STORAGE:
            self.__memory.pop(0)

    def kill(self):
        self.energy = 0

    def checkDeath(self):
        if self.isDead():
            return None
        else:
            return self

    def __str__(self):
        return (f'Individual - ID: {self.id} -----------------\n'
                f'\tSpecie: {self.specie}\n'
                f'\tEnergy: {self.energy}\n'
                f'\tAge / Lifetime: {self.age} / {self.lifetime} days\n'
                f'\tGroup: {self.inAGroup}\n'
                f'\tSocialness: {self.social_attitude}\n'
                f'---------------------------------------\n')


class Carviz(Animal):
    def __init__(self, id):
        super().__init__(id)
        self.specie = "Carviz"

    def loseEnergy(self, value=MOV_ENERGY_LOSS_C):
        self.energy -= value
        if self.energy <= 0:
            self.kill()

    def gainEnergy(self, value=ERB_EAT_ENERGY_GAIN):
        self.energy += value
        if self.energy > self.max_energy:
            self.energy = self.max_energy

    def nextMove(self, neighCells, groupChoice=None, exclude_cell=None):
        energy_perc = self.energy / self.max_energy
        current_cell = neighCells[4]
        food_cells = []
        stayInGroup = True

        if groupChoice:
            # find food cells
            for cell in neighCells:
                neighbour = cell.getPopulation()
                if neighbour:
                    if (isinstance(neighbour, Erbast) or
                            (isinstance(neighbour, Herd) and neighbour.populationSize() < 3)):
                        food_cells.append(cell)

            if energy_perc < PERC_STARVING_C and groupChoice not in food_cells:
                if self.social_attitude < 0.4 * MAX_SOCIALNESS:
                    stayInGroup = False
                else:
                    self.social_attitude -= 1
                    if self.social_attitude < 0:
                        self.social_attitude = 0
                        stayInGroup = False

            if stayInGroup:
                for i in range(10 - self.social_attitude):
                    prob = random.randint(0, 100)
                    if prob == 1:
                        stayInGroup = False

            if stayInGroup:
                self.social_attitude += 1
                if self.social_attitude > MAX_SOCIALNESS:
                    self.social_attitude = MAX_SOCIALNESS
                return

        # if not stayInGroup or neighCells=None: choose the next best cell
        bestCell = self.chooseBestCell(neighCells, exclude_cell=exclude_cell)
        if bestCell != current_cell:
            self.loseEnergy()

        bestCellCoords = bestCell.getCoords()
        self.addMemory(bestCell)
        return [(self, bestCellCoords)]

    def chooseBestCell(self, neighCells, exclude_cell=None):
        energy_perc = self.energy / self.max_energy
        previous_cell = self.getLastMemory()
        current_cell = neighCells[4]
        richest_cell = None
        dangerous_cells = []
        erbast_cells = []
        available_cells = []

        # find richest cell and eliminate water cells
        for cell in neighCells:
            if not cell.isWater:
                available_cells.append(cell)
                if cell != current_cell and cell != previous_cell:
                    if not richest_cell:
                        richest_cell = cell
                    elif cell.getVegetobDensity() > richest_cell.getVegetobDensity():
                        richest_cell = cell

        if exclude_cell and exclude_cell in available_cells:
            available_cells.remove(exclude_cell)

        if exclude_cell and exclude_cell in erbast_cells:
            erbast_cells.remove(exclude_cell)

        # find neighbours
        for cell in available_cells:
            neighbour = cell.getPopulation()
            if neighbour:
                if isinstance(neighbour, Herd) and neighbour.populationSize() > 2:
                    nearby_cells = cell.getNeighbours()
                    for nearby_cell in nearby_cells:
                        if nearby_cell in available_cells:
                            dangerous_cells.append(nearby_cell)
                if isinstance(neighbour, Erbast):
                    erbast_cells.append(cell)

        if dangerous_cells:
            for dangerous_cell in dangerous_cells:
                if dangerous_cell in available_cells:
                    available_cells.remove(dangerous_cell)
                if dangerous_cell in erbast_cells:
                    erbast_cells.remove(dangerous_cell)

        if erbast_cells:
            prob = random.randint(0, 100)
            if prob < 5 and available_cells:
                final_cell = available_cells[random.randint(0, len(available_cells) - 1)]
            else:
                final_cell = erbast_cells[random.randint(0, len(erbast_cells) - 1)]

        elif richest_cell in available_cells:
            final_cell = richest_cell

        else:
            if len(available_cells) > 1 and energy_perc > PERC_STARVING_C:
                final_cell = available_cells[random.randint(0, len(available_cells) - 1)]
            else:
                final_cell = current_cell

        if final_cell != current_cell:
            self.loseEnergy(MOV_ENERGY_LOSS_C)

        while final_cell == exclude_cell:
            final_cell = neighCells[random.randint(0, len(neighCells) - 1)]

        return final_cell

    def birth(self, cell):
        if self.age > self.lifetime:
            self.kill()
            x, y = cell.getCoords()

            children = random.randint(MAX_BIRTH_C / 2, MAX_BIRTH_C)
            new_carviz_list = [Carviz(f"{GlobalVariables.global_day}C{x}-{y}{chr(k + 97)}") for k in range(children)]
            return new_carviz_list


class Erbast(Animal):
    def __init__(self, id):
        super().__init__(id)
        self.specie = "Erbast"

    def loseEnergy(self, value=MOV_ENERGY_LOSS_E):
        self.energy -= value
        if self.energy <= 0:
            self.kill()

    def gainEnergy(self, value=VEG_EAT_ENERGY_GAIN):
        self.energy += value
        if self.energy > self.max_energy:
            self.energy = self.max_energy

    def nextMove(self, neighCells=None, groupChoice=None, exclude_cell=None):
        energy_perc = self.energy / self.max_energy
        current_cell = neighCells[4]
        dangerous_cells = []
        stayInGroup = True

        if groupChoice:
            # find neighbours and dangerous cells
            for cell in neighCells:
                neighbour = cell.getPopulation()
                if neighbour:
                    if isinstance(neighbour, Pride) or isinstance(neighbour, Carviz):
                        nearby_cells = cell.getNeighbours()
                        for nearby_cell in nearby_cells:
                            if nearby_cell in neighCells:
                                dangerous_cells.append(cell)

            if groupChoice in dangerous_cells:
                stayInGroup = False

            if energy_perc < PERC_STARVING_E and groupChoice != current_cell:
                if self.social_attitude < 0.6 * MAX_SOCIALNESS:
                    stayInGroup = False
                else:
                    self.social_attitude -= 1
                    if self.social_attitude < 0:
                        self.social_attitude = 0
                        stayInGroup = False

            if stayInGroup:
                for i in range(10 - self.social_attitude):
                    prob = random.randint(0, 100)
                    if prob == 1:
                        stayInGroup = False

            if stayInGroup:
                self.social_attitude += 1
                if self.social_attitude > MAX_SOCIALNESS:
                    self.social_attitude = MAX_SOCIALNESS
                return

        # if not stayInGroup or neighCells=None: choose the next best cell
        bestCell = self.chooseBestCell(neighCells, exclude_cell=exclude_cell)
        if bestCell == current_cell and self.energy < self.max_energy:
            self.eatVeg(current_cell)
        else:
            self.loseEnergy()

        bestCellCoords = bestCell.getCoords()
        self.addMemory(bestCell)
        return [(self, bestCellCoords)]

    def eatVeg(self, cell):
        cell.decreaseVeg()
        self.gainEnergy()

    def chooseBestCell(self, neighCells, exclude_cell=None):
        energy_perc = self.energy / self.max_energy
        previous_cell = self.getLastMemory()
        current_cell = neighCells[4]
        richest_cell = None
        avoidable_cell = None
        dangerous_cells = []
        extremeCases_cells = []
        available_cells = []
        final_cell = None

        # find richest cell and eliminate water cells
        for cell in neighCells:
            if not cell.isWater:
                available_cells.append(cell)
                if cell != current_cell and cell != previous_cell:
                    if not richest_cell:
                        richest_cell = cell
                    elif cell.getVegetobDensity() > richest_cell.getVegetobDensity():
                        richest_cell = cell

        if exclude_cell and exclude_cell in available_cells:
            available_cells.remove(exclude_cell)

        # find neighbours
        for cell in available_cells:
            neighbour = cell.getPopulation()
            if neighbour:
                nearby_cells = cell.getNeighbours()
                if isinstance(neighbour, Pride) or isinstance(neighbour, Carviz):
                    extremeCases_cells.append(cell)
                    for nearby_cell in nearby_cells:
                        if nearby_cell in available_cells and nearby_cell not in extremeCases_cells:
                            dangerous_cells.append(nearby_cell)

                if isinstance(neighbour, Herd):
                    if cell == richest_cell and cell in nearby_cells:
                        avoidable_cell = cell

        if dangerous_cells:
            if avoidable_cell in dangerous_cells:
                avoidable_cell = None
            for dangerous_cell in dangerous_cells + extremeCases_cells:
                if dangerous_cell in available_cells:
                    available_cells.remove(dangerous_cell)

            if not available_cells:
                if extremeCases_cells:
                    for cell in extremeCases_cells:
                        if not final_cell:
                            final_cell = cell
                        elif isinstance(cell.getPopulation(), Carviz):
                            final_cell = cell
                else:
                    final_cell = current_cell
            elif avoidable_cell:
                final_cell = avoidable_cell
            else:
                if len(available_cells) > 1:
                    final_cell = available_cells[random.randint(0, len(available_cells) - 1)]
                else:
                    final_cell = available_cells[0]

        else:
            if energy_perc < PERC_STARVING_E:
                final_cell = current_cell
            else:
                final_cell = richest_cell

        if final_cell != current_cell:
            self.loseEnergy(MOV_ENERGY_LOSS_E)

        while final_cell == exclude_cell:
            final_cell = neighCells[random.randint(0, len(neighCells) - 1)]

        return final_cell

    def birth(self, cell):
        if self.age > self.lifetime:
            self.kill()
            x, y = cell.getCoords()

            children = random.randint(MAX_BIRTH_E / 2, MAX_BIRTH_E)
            new_erbast = [Erbast(f"{GlobalVariables .global_day}E{x}-{y}{chr(k + 97)}") for k in range(children)]
            return new_erbast


# GROUPS CLASSES #############################################################
class Group:
    def __init__(self, id, population):
        self.id = id
        self.population = population
        self.__memory = []
        self.type = None

        for animal in self.population:
            animal.inAGroup = True
            animal.social_attitude = 3

    def populationSize(self):
        return len(self.population)

    def averageEnergy(self):
        energySum = 0
        for animal in self.population:
            if animal:
                energySum += animal.energy
        if self.populationSize() == 0:
            averageEnergy = 0
        else:
            averageEnergy = energySum / self.populationSize()
        return averageEnergy

    def addAnimal(self, animal):
        if self.populationSize() < MAX_GROUP_SIZE:
            self.population.append(animal)
            animal.social_attitude = 3
            animal.inAGroup = True
            joined = True
        else:
            joined = False
        return joined

    def removeAnimal(self, animal):
        animal.inAGroup = False
        animal.social_attitude = 0
        self.population.remove(animal)

    def increaseDayLived(self):
        for animal in self.population:
            animal.increaseDayLived()

    def memorySize(self):
        return len(self.__memory)

    def getMemory(self):
        return self.__memory

    def getLastMemory(self):
        if self.memorySize() > 0:
            return self.__memory[-1]

    def addMemory(self, memory):
        self.__memory.append(memory)
        if self.memorySize() > MAX_DAY_STORAGE:
            self.__memory.pop(0)

        for animal in self.population:
            animal.addMemory(memory)

    def checkDeath(self):
        for animal in self.population:
            if animal.isDead():
                self.removeAnimal(animal)

        if self.populationSize() == 1:
            animal = self.population[0]
            animal.inAGroup = False
            animal.social_attitude = 0
            return animal

        if self.populationSize() == 0:
            return None

        return self

    def birth(self, cell):
        new_animals = []
        extra_animals = []
        for animal in self.population:
            children = animal.birth(cell)
            if children:
                while children:
                    new_animals.append(children.pop())
                self.removeAnimal(animal)

        if new_animals:
            while new_animals:
                animal = new_animals.pop()
                if not self.addAnimal(animal):
                    extra_animals.append(animal)

            return self, extra_animals

    def __str__(self):
        population_string = ''
        for individual in self.population:
            for line in str(individual).splitlines():
                population_string += f'\t\t{line}\n'

        return (f'Group - ID: {self.id} ======================================\n'
                f'\tType: {self.type}\n'
                f'\tMembers:\n'
                f'{population_string}'
                f'=====================================================')


class Pride(Group):
    def __init__(self, id, population):
        super().__init__(id, population)
        self.type = "Pride"

    def nextMove(self, neighCells):
        # choose the next best cell
        bestCell = self.chooseBestCell(neighCells)
        current_cell = neighCells[4]
        moveToList = []

        for carviz in self.population:
            newCell = carviz.nextMove(neighCells, groupChoice=bestCell)
            if newCell:
                moveToList += newCell
                self.removeAnimal(carviz)
            elif bestCell != current_cell:
                carviz.loseEnergy()

        if self.populationSize() > 0:
            moveToList.append((self, bestCell.getCoords()))
            self.addMemory(bestCell)
        return moveToList

    def chooseBestCell(self, neighCells):
        averageEnergy = self.averageEnergy()
        previous_cell = self.getLastMemory()
        current_cell = neighCells[4]
        richest_cell = None
        food_cells = []
        available_cells = []

        # find richest cell and eliminate water cells
        for cell in neighCells:
            if not cell.isWater:
                available_cells.append(cell)
                if cell != current_cell and cell != previous_cell:
                    if not richest_cell:
                        richest_cell = cell
                    elif cell.getVegetobDensity() > richest_cell.getVegetobDensity():
                        richest_cell = cell

        # find neighbours
        for cell in available_cells:
            neighbour = cell.getPopulation()
            if neighbour:
                if isinstance(neighbour, Herd) or isinstance(neighbour, Erbast):
                    food_cells.append(cell)

        if food_cells:
            prob = random.randint(0, 100)
            if prob < 5 and available_cells:
                final_cell = available_cells[random.randint(0, len(available_cells) - 1)]
            else:
                final_cell = food_cells[random.randint(0, len(food_cells) - 1)]

        elif richest_cell in available_cells:
            final_cell = richest_cell

        else:
            if len(available_cells) > 1 and averageEnergy > PERC_STARVING_H:
                final_cell = available_cells[random.randint(0, len(available_cells) - 1)]
            else:
                final_cell = current_cell

        return final_cell


class Herd(Group):
    def __init__(self, id, population):
        super().__init__(id, population)
        self.type = "Herd"

    def nextMove(self, neighCells):
        # choose the next best cell
        bestCell = self.chooseBestCell(neighCells)
        current_cell = neighCells[4]
        moveToList = []

        for erbast in self.population:
            newCell = erbast.nextMove(neighCells, groupChoice=bestCell)
            if newCell:
                moveToList += newCell
                self.removeAnimal(erbast)
            elif bestCell == current_cell:
                erbast.eatVeg(current_cell)
            else:
                erbast.loseEnergy()

        if self.populationSize() > 0:
            moveToList.append((self, bestCell.getCoords()))
            self.addMemory(bestCell)
        return moveToList

    def chooseBestCell(self, neighCells):
        averageEnergy = self.averageEnergy()
        size = self.populationSize()
        previous_cell = self.getLastMemory()
        current_cell = neighCells[4]
        richest_cell = None
        dangerous_cells = []
        available_cells = []

        # find richest cell and eliminate water cells
        for cell in neighCells:
            if not cell.isWater:
                available_cells.append(cell)
                if cell != current_cell and cell != previous_cell:
                    if not richest_cell:
                        richest_cell = cell
                    elif cell.getVegetobDensity() > richest_cell.getVegetobDensity():
                        richest_cell = cell

        # find neighbours
        for cell in available_cells:
            neighbour = cell.getPopulation()
            if neighbour:
                nearby_cells = cell.getNeighbours()
                if isinstance(neighbour, Pride) or (size < 3 and isinstance(neighbour, Carviz)):
                    for nearby_cell in nearby_cells:
                        if nearby_cell in available_cells:
                            dangerous_cells.append(nearby_cell)

        if dangerous_cells:
            for dangerous_cell in dangerous_cells:
                if dangerous_cell in available_cells:
                    available_cells.remove(dangerous_cell)

            if not available_cells:
                # give the opportunity to randomly avoid the danger to the single members
                final_cell = current_cell
            else:
                if len(available_cells) > 1:
                    final_cell = available_cells[random.randint(0, len(available_cells) - 1)]
                else:
                    final_cell = available_cells[0]
        else:
            if averageEnergy < PERC_STARVING_H:
                final_cell = current_cell
            else:
                final_cell = richest_cell

        return final_cell
