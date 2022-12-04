"""Module containing the Landscape class and its four subtypes: Lowland, Highland, Desert and Water.
 Instances of these objects are the cells of which the island consists of and are intermediaries to
 the animal and island modules. """

import random
import biosim.animal as ba
import itertools


class Landscape():
    """ Defines the properties of the particular cell of the island"""

    def __init__(self):
        """ Defining attributes needed"""
        self.herb_list = []
        self.carn_list = []
        self.adjacent_cells = []
        self.set_fodder()
        self.accessability = None

    @classmethod
    def set_params(cls, given_parameters):
        """ Applies the given parameters by the user"""
        for param, value in given_parameters.items():
            if value < 0:
                raise ValueError(f"{param} cannot be negative")
            elif param not in cls.params:
                raise ValueError(f'{str(param)} is not a valid parameter')
            else:
                cls.params[param] = value

    def set_fodder(self):
        """Sets available fodder to equal f_max"""
        self.available_fodder = self.params['f_max']

    def _sort_fitness(self, descending=True):
        """
        Sorts animals by fitness.
        Parameters
        ----------
        descending (Boolean): If True, sorts animals by fitness decendingly

        Returns
        -------
        herbs_fitness_sorted: list
        """
        herbs_fitness_sorted = sorted(self.herb_list, key=lambda x: x.fitness, reverse=descending)
        return herbs_fitness_sorted

    def remove_animal_if_dead(self, dead, animal):
        """
        Removes herbivore from cell if the animal is dead.
        Parameters
        ----------
        dead: boolean
            Boolean indicating if animal is dead or not.
        animal: instance of Animal
        """
        if dead:
            self.get_animal_list(animal).remove(animal)

    def get_animal_list(self, animal):
        """
        Gets the animal list.
        Parameters
        ----------
        animal

        Returns
        -------
        proper_list_dict: dict
            The list of the animal.
        """
        proper_list_dict = {ba.Herbivore: self.herb_list, ba.Carnivore: self.carn_list}
        return proper_list_dict[type(animal)]

    def feed_herbivores(self):
        """
        Gives all herbivore a turn at eating. The fittest herbivore eats first.
        """
        herbs = self._sort_fitness()
        i = 0
        while self.available_fodder > 0 and i + 1 <= len(herbs):
            herb = herbs[i]
            if self.available_fodder - herb.params['F'] >= 0:
                F = herb.params['F']
            else:
                F = self.available_fodder
            self.available_fodder -= F
            herb.eat(F)
            i += 1

    def facilitate_hunting(self):
        """
        If the carnivore is eligible and need to hunt for the least fit herbivore, it facilitates
        the hunting.
        """
        random.shuffle(self.carn_list)
        for carnivore in self.carn_list:
            sorted_herbivores = self._sort_fitness(descending=False)
            weight_eaten = 0
            i = 0
            while weight_eaten < carnivore.params["F"] and i < len(sorted_herbivores):
                herbivore = sorted_herbivores[i]
                if carnivore.killing_probability(herbivore):
                    weight_eaten += herbivore.weight
                    carnivore.eat(herbivore.weight)
                    herbivore.die()
                    self.herb_list.remove(herbivore)
                i += 1

    def procreate_herbivores(self):
        """
        Iterates through herbivores in cell and calculates probability of procreation.
        The function then runs birth() if procreation happens and appends new herbivore to
        herb_list.
        """
        Nh = len(self.herb_list)
        new_herb_list = []
        for herb in self.herb_list:
            if herb.calculate_procreation_probability(Nh):
                new_herb = herb.birth()
                if new_herb is not None:
                    new_herb_list.append(new_herb)
        self.herb_list += new_herb_list

    def procreate_carnivores(self):
        """
        Iterates through carnivores in cell and calculates probability of procreation.
        The function then runs birth() if procreation happens and appends new carnivore to
        carn_list.
        """
        Nc = len(self.carn_list)
        new_carn_list = []
        for carn in self.carn_list:
            if carn.calculate_procreation_probability(Nc):
                new_carn = carn.birth()
                if new_carn is not None:
                    new_carn_list.append(new_carn)
        self.carn_list += new_carn_list

    def migrate_herbivores(self):
        """
        Gives every herbivore in the cell the option of migrating or not.
        """
        if "," in self.herb_list:
            index = self.herb_list.index(",")
        else:
            index = len(self.herb_list)

        for herbivore in self.herb_list[0:index]:
            if herbivore.migrate_or_not():
                direction = herbivore.migration_direction()
                destination = self.adjacent_cells[direction]
                if destination.accessability:
                    if 0 < direction < 3 and "," not in destination.herb_list:
                        destination.herb_list.append(",")
                    destination.herb_list.append(herbivore)
                    self.herb_list.remove(herbivore)

        while "," in self.herb_list:
            self.herb_list.remove(",")

    def migrate_carnivores(self):
        """
        Updates the herbivore if the carnivore migrates to the cell.
        Returns
        -------
        carn_list: list
            list of the new updated carnivore list.
        """
        if "," in self.carn_list:
            index = self.carn_list.index(",")
        else:
            index = len(self.carn_list)

        for carnivore in self.carn_list[0:index]:
            if carnivore.migrate_or_not():
                direction = carnivore.migration_direction()
                destination = self.adjacent_cells[direction]
                if destination.accessability:
                    if 0 < direction < 3 and "," not in destination.carn_list:
                        destination.carn_list.append(",")
                    destination.carn_list.append(carnivore)
                    self.carn_list.remove(carnivore)
        while "," in self.carn_list:
            self.carn_list.remove(",")

    def age_animals(self):
        """
        Increases the age of the animal.
        """
        for animal in self.get_animals():
            animal.aging()

    def update_life_status_of_animals(self):
        """
        If the animal is dead, it removes the animal from the list.
        """
        for animal in self.get_animals():
            dead_or_not = animal.update_life_status()
            self.remove_animal_if_dead(dead_or_not, animal)

    def animals_lose_weight(self):
        """
        Decrease the weight of the animal.
        """
        for animal in self.get_animals():
            animal.weight_loss()

    def get_fitness(self):
        """
        Gets the age of animal.
        """
        return [[herbivore.fitness for herbivore in self.herb_list],
                [carnivore.fitness for carnivore in self.carn_list]]

    def get_age(self):
        """
        Gets the age of animal.
        """
        return [[herbivore.age for herbivore in self.herb_list],
                [carnivore.age for carnivore in self.carn_list]]

    def get_weight(self):
        """
        Retrieves the weight of the animal.
        """
        return [[herbivore.weight for herbivore in self.herb_list],
                [carnivore.weight for carnivore in self.carn_list]]

    def get_animals(self):
        """
        Retrieves the list of herbivore and carnivore.
        """
        return itertools.chain(self.herb_list, self.carn_list)


class Lowland(Landscape):
    """
    Lowland class. Initialises at_hand_fodder with params['f_max']
    """
    params = {'f_max': 800.0}
    default_params = {'f_max': 800.0}

    def __init__(self):
        super().__init__()
        self.accessability = True


class Highland(Landscape):
    """
    Highland class with the properties of the highland cell. Initializing at_hand_fodder with
    params['f_max']
    """
    params = {"f_max": 300.0}
    default_params = {'f_max': 0}

    def __init__(self):
        super().__init__()
        self.accessability = True


class Desert(Landscape):
    """Desert class with properties of desert cell."""
    params = {'f_max': 0}
    default_params = {'f_max': 0}

    def __init__(self):
        super().__init__()
        self.accessability = True


class Water(Landscape):
    """Water class with the properties of water cell."""
    params = {"f_max": 0}
    default_params = {"f_max": 0}
    """Water has no fodder and no one can migrate to it"""

    def __init__(self):
        super().__init__()
        self.accessability = False


def set_animal_parameters(species, parameters):
    """Sets the parameter of Herbivore and Carnivore."""
    if species.title() == "Herbivore":
        ba.Herbivore.set_params(parameters)
    elif species.title() == "Carnivore":
        ba.Carnivore.set_params(parameters)
    else:
        raise ValueError(f'{species} is not a species')


def num_animals_per_species():
    """
    The number of herbivore and carnivore in the cell.
    """
    return {"Herbivore": ba.Herbivore.amount(), "Carnivore": ba.Carnivore.amount()}
