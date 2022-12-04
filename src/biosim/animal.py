"""
Module containing the Animal class and its two subtypes: Herbivore and Carnivore.
This module makes up the bottom-most layer of the package.
"""

import math
import random


class Animal():
    """
    Animal class with object properties.
    """
    def __init__(self, weight=None, age=0):

        self.initiate_weight(weight)
        self.initiate_age(age)
        self.count_new()

    @classmethod
    def reset_counter(cls):
        cls.count = 0

    @classmethod
    def count_new(cls):
        cls.count += 1

    @classmethod
    def remove_one_count(cls):
        cls.count -= 1

    @classmethod
    def amount(cls):
        return cls.count

    @classmethod
    def set_params(cls, given_parameters):
        """ Applies the given parameters"""
        for param, value in given_parameters.items():
            if value < 0:
                raise ValueError(f"{param} cannot be negative")
            if param not in cls.params:
                raise ValueError(f'{str(param)} is not a recognized parameter')
            else:
                cls.params[param] = value

    @staticmethod
    def prob_true_or_false(prob):
        """Converts probability to True or False"""
        random_probability = random.random()
        if random_probability < prob:
            return True
        else:
            return False

    @property
    def fitness(self):
        """Calculates fitness based on age and weight."""
        if self.weight > 0:
            q_plus = 1 / (1 + (
                        math.e ** (self.params['phi_age'] * (self.age - self.params['a_half']))))
            q_minus = 1 / (1 + (math.e ** (
                        -self.params['phi_weight'] * (self.weight - self.params['w_half']))))
            return q_plus * q_minus
        else:
            return 0

    def die(self):
        self.remove_one_count()

    def initiate_weight(self, weight):
        r"""
        Assign the initial weight according to the gaussian distribution if weight at birth and
        sigma of birth.

        w ∼ N (w\ :sub:`birth`\, σ\ :sub:`birth`\)

        Parameters
        ----------
        weight: float
            initial weight

        Returns
        -------
        weight: float
            weight based on guassian distribution.
        """
        if weight is None:
            weight = random.gauss(self.params['w_birth'], self.params['sigma_birth'])
            while weight < 0:
                weight = random.gauss(self.params['w_birth'], self.params['sigma_birth'])
            self.weight = weight
        elif weight <= 0:
            raise ValueError("Weight must be positive")
        else:
            self.weight = weight

    def initiate_age(self, age):
        """Initialise the age at first."""
        if age < 0:
            raise ValueError("Age cannot be negative")
        else:
            self.age = age

    def aging(self):
        """Increases age every year and also updates the fitness."""
        self.age += 1

    def weight_loss(self):
        r"""Weight decreases by a factor of 'eta'.

        w = (1 - η)w
        """
        self.weight *= (1 - self.params["eta"])

    def update_life_status(self):
        """ Defines if the animal will die or not. Returns True if dead."""
        death_probability = self.params['omega'] * (1 - self.fitness)
        if self.prob_true_or_false(death_probability):
            self.die()
            return True
        else:
            return False

    def calculate_procreation_probability(self, N):
        r"""
        Calculates probability that an animal gives birth.

        `min(1, γ × Φ × (N − 1))`

        Parameters
        ----------
        N: int
            Amount of animals of same subtype in the cell

        Returns
        -------
        procreation_probability: float
        """
        procreation_probability = self.params["gamma"] * self.fitness * (N - 1)
        if procreation_probability > 1:
            procreation_probability = 1
        return self.prob_true_or_false(procreation_probability)

    def birth(self):
        r"""
        Gives birth to a new animal object.

                w ∼ N (w\ :sub:`birth`\, σ\ :sub:`birth`\)

                w_loss = w - `ηw`


        Returns
        -------
        weight: float
            updated weight of the birth weight
        """
        birth_weight = random.gauss(self.params['w_birth'], self.params['sigma_birth'])
        if birth_weight > 0:
            weight_loss = self.params["xi"] * birth_weight
            if self.weight >= weight_loss:
                self.weight -= weight_loss
                return type(self)(birth_weight, 0)

    def migrate_or_not(self):
        """
        Decides whether the animal migrates or not.

        Returns
        -------
        migrate: boolean
            Returns True if migrates otherwise returns False.
        """
        migration_probability = self.params["mu"] * self.fitness
        migrate = self.prob_true_or_false(migration_probability)
        return migrate

    def migration_direction(self):
        """
        Randomly selects the direction in which the animal migrates.

        Returns
        -------
        direction: int
        """
        return random.choice(range(4))

    def eat(self, feed):
        r"""
        Updates weight after the animal has eaten.
        Updates the fitness.

        w = w +`βF`

        Parameters
        ----------
        feed : float
            Amount of fodder that is eaten.
        """
        self.weight += self.params['beta'] * feed


class Herbivore(Animal):
    """
    Herbivore class with default parameters for herbivore animal.
    """
    params = {
        'zeta': 3.5,
        'a_half': 40.0,
        'w_birth': 8.0,
        'sigma_birth': 1.5,
        'beta': 0.9,
        'eta': 0.05,
        'phi_age': 0.6,
        'w_half': 10.0,
        'phi_weight': 0.1,
        'mu': 0.25,
        'gamma': 0.2,
        'xi': 1.2,
        'omega': 0.4,
        'F': 10.0,
    }
    default_params = {
        'zeta': 3.5,
        'a_half': 40.0,
        'w_birth': 8.0,
        'sigma_birth': 1.5,
        'beta': 0.9,
        'eta': 0.05,
        'phi_age': 0.6,
        'w_half': 10.0,
        'phi_weight': 0.1,
        'mu': 0.25,
        'gamma': 0.2,
        'xi': 1.2,
        'omega': 0.4,
        'F': 10.0,
    }
    count = 0

    def __init__(self, weight, age):
        super().__init__(weight, age)


class Carnivore(Animal):
    """
    Carnivore class with default parameters for carnivore animal.
    """
    params = {
        'zeta': 3.5,
        'a_half': 40.0,
        'w_birth': 6.0,
        'sigma_birth': 1.0,
        'beta': 0.75,
        'eta': 0.125,
        'phi_age': 0.3,
        'w_half': 4.0,
        'phi_weight': 0.4,
        'mu': 0.4,
        'gamma': 0.8,
        'xi': 1.1,
        'omega': 0.8,
        'F': 50.0,
        'DeltaPhiMax': 10.0
    }
    default_params = {
        'zeta': 3.5,
        'a_half': 40.0,
        'w_birth': 6.0,
        'sigma_birth': 1.0,
        'beta': 0.75,
        'eta': 0.125,
        'phi_age': 0.3,
        'w_half': 4.0,
        'phi_weight': 0.4,
        'mu': 0.4,
        'gamma': 0.8,
        'xi': 1.1,
        'omega': 0.8,
        'F': 50.0,
        'DeltaPhiMax': 10.0
    }
    count = 0

    def __init__(self, weight, age):
        super().__init__(weight, age)

    def killing_probability(self, prey):
        r"""
        Checks if carnivore can prey or not based on fitness of both the species.

            P = [carnivore\ :sub:`fitness`\ - herbivore\ :sub:`fitness`\]/ ΔΦ\ :sub:`max`\

        Parameters
        ----------
        prey: float

        Returns
        -------
        binary: boolean
            Returns True if carnivore can prey on herbivore, False if not.
        """
        fitness_disparity = self.fitness - prey.fitness
        if fitness_disparity <= 0:
            return False
        elif fitness_disparity < self.params["DeltaPhiMax"]:
            probability = fitness_disparity / self.params["DeltaPhiMax"]
            return self.prob_true_or_false(probability)
        else:
            return True
