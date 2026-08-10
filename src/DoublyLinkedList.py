# Autors: Marco Zennaro - Fabio Bruschi

# Imports
from settings import MAX_DAY_STORAGE


# NODE CLASS ##################################################################
class DayData:
    def __init__(self, day, data):
        self.next = None
        self.prev = None
        self.day = day
        self.data = data

    def setData(self, newData):
        self.data = newData

    def getData(self, key=None):
        if isinstance(self.data, dict):
            if key:
                return self.data[key]
        return self.data

    def setDay(self, newDay):
        self.day = newDay

    def getDay(self):
        return self.day

    def setNext(self, newNext):
        self.next = newNext

    def getNext(self):
        return self.next

    def setPrev(self, newPrev):
        self.prev = newPrev

    def getPrev(self):
        return self.prev

    def __str__(self):
        string = 'Day: ' + str(self.day) + '\n'
        if isinstance(self.data, dict):
            for key, value in self.data.items():
                string += f'\t{key}: {value}\n'
            return string
        else:
            return string + str(self.data)


# DOUBLY LINKED LIST CLASS ####################################################
class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def isEmpty(self):
        return self.head is None

    def addDayData(self, day, data):
        if self.size() > MAX_DAY_STORAGE:
            self.removeHead()

        newDay = DayData(day, data)
        if self.head is None:
            self.head = newDay
            self.tail = newDay
        else:
            self.tail.setNext(newDay)
            newDay.setPrev(self.tail)
            self.tail = newDay

    def addDataInDay(self, day, data):
        day_found = self.searchDay(day)
        if day_found:
            day_found.setData(data)
        else:
            self.addDayData(day, data)

    def size(self):
        current = self.head
        count = 0
        while current is not None:
            count = count + 1
            current = current.getNext()
        return count

    def searchDay(self, searched_day):
        current = self.head
        while current:
            if current.getDay() == searched_day:
                return current
            else:
                current = current.getNext()
        return None

    def getFirst(self):
        return self.head

    def getLast(self):
        return self.tail

    def removeHead(self):
        if self.head is None:
            return
        else:
            self.head = self.head.getNext()
            self.head.setPrev(None)

    def remove(self, day):
        current = self.head
        while current:
            if current.getDay() == day:
                if current == self.head:
                    self.head = current.getNext()
                    self.head.setPrev(None)
                elif current == self.tail:
                    self.tail = current.getPrev()
                    self.tail.setNext(None)
                else:
                    current.getPrev().setNext(current.getNext())
                    current.getNext().setPrev(current.getPrev())
                return
            else:
                current = current.getNext()

    def __str__(self):
        current = self.head
        string = ""
        while current:
            string += str(current) + "\n"
            current = current.getNext()
        return string
