import random


class GeigerSimulator:
    CPM_TEXT = 'cpm'
    RADIATION_TEXT = 'radiation'
    ACKNOWLEDGES_TEXT = 'acknowledges'

    def __init__(self):
        self.__random_CPM = [0, 60, 120, 180]
        self.__last_radiation = [0]
        self.__is_acknowledged = False

    def get_CPM(self):
        return random.choice(self.__random_CPM)

    def get_radiation(self):
        if self.__is_acknowledged:
            current_random = random.randint(0, 3)
            if len(self.__last_radiation) > 0:
                if self.__last_radiation[0] != current_random:
                    self.__last_radiation.pop(0)
                    self.__last_radiation.append(current_random)

            if len(self.__last_radiation) == 0:
                self.__last_radiation.append(current_random)

        return self.__last_radiation[0]

    def is_count_acknowledged(self):
        return self.__is_acknowledged

    def get_values(self):
        is_acknowledges_vales = random.randint(0, 1000000)
        if is_acknowledges_vales < 500000:
            self.__is_acknowledged = True

        else:
            self.__is_acknowledged = False

        return {self.CPM_TEXT: self.get_CPM(),
                self.RADIATION_TEXT: self.get_radiation(),
                self.ACKNOWLEDGES_TEXT: is_acknowledges_vales}

    def __str__(self):
        return f'{self.get_CPM()} {self.get_radiation()} {self.is_count_acknowledged()}'
