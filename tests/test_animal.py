import math
import statistics
import random
import pytest
from scipy import stats
from scipy.stats import truncnorm

import biosim.animal as ba

SEED = 1234
ALPHA = 0.01  # for statistical testing

random.seed(SEED)


@pytest.fixture(autouse=True)
def reset_params():
    """Resets params to default values"""
    yield
    ba.Herbivore.set_params(ba.Herbivore.default_params)
    ba.Carnivore.set_params(ba.Carnivore.default_params)


@pytest.mark.parametrize("animal", [ba.Herbivore(100, 10), ba.Carnivore(100, 10)])
class Test_both_animals():
    all_params = [[param, random.randrange(1, 10)] for param in ba.Herbivore.params]

    @pytest.mark.parametrize("param, value", all_params)
    def test_set_params(self, animal, param, value):
        """
        Tests if the value assigned to the parameter is actually assigned to the parameter or not.
        Parameters
        ----------
        animal
        param
        value
        """
        type(animal).set_params({param: value})
        assert animal.params[param] == value

    @pytest.mark.parametrize("param", [param_value[0] for param_value in all_params])
    def test_set_params_negative(self, animal, param):
        """Tests if a ValueError is raised when a negative parameter is given"""
        pytest.raises(ValueError, type(animal).set_params, {param: -1})

    def test_set_params_wrong_param(self, animal):
        """Tests if a ValueError is raised when a non-existent parameter is given"""
        pytest.raises(ValueError, type(animal).set_params, {"non_existent parameter": 1})

    def test_initiate_age_negative(self, animal):
        """Tests if a ValueError is raised when a negative age is given"""
        pytest.raises(ValueError, animal.initiate_age, -1)

    def test_initiate_age(self, animal):
        """Tests if age is successfully initiated"""
        given_age = 5
        animal.initiate_age(given_age)
        assert animal.age == given_age

    def test_initiate_weight_negative(self, animal):
        """Tests if a ValueError is raised when a negative age is given"""
        pytest.raises(ValueError, animal.initiate_weight, -1)

    def test_initiate_weight(self, animal):
        """Tests if weight is successfully initiated"""
        given_weight = 5
        animal.initiate_weight(given_weight)
        assert animal.weight == given_weight

    def test_initiate_weight_none(self, animal, mocker):
        """Tests if weight is successfully initiated by random.gauss() if weight is None"""
        birth_weight = 1
        mocker.patch('random.gauss', return_value=birth_weight)
        animal.initiate_weight(None)
        assert animal.weight == birth_weight

    def test_aging(self, animal):
        """
        Tests if the aging method properly adjusts the age of the animal.
        """
        initial_age = animal.age
        years_passed = 10
        for _ in range(years_passed):
            animal.aging()
        assert animal.age == initial_age + years_passed

    def test_weight_loss(self, animal):
        """
        Tests whether the weight loss is done by the formula - animal.params["mu"] * animal.weight.
        """
        first_weight = 100
        animal.initiate_weight(first_weight)
        assumed_weight_loss = animal.params["eta"] * animal.weight
        animal.weight_loss()
        second_weight = animal.weight
        assert second_weight == first_weight - assumed_weight_loss

    def test_update_life_status_return(self, animal, mocker):
        """
        Tests if dead, function updates the animal as dead or not dead if otherwise.
        """
        mocker.patch('random.random', return_value=0)
        assert animal.update_life_status()

    def test_update_life_status_die(self, animal, mocker):
        """
        Uses mocker.spy to test if dead, decrease the animal count.
        """
        mocker.patch('random.random', return_value=0)
        spy = mocker.spy(ba.Animal, 'die')
        animal.update_life_status()
        assert spy.call_count == 1

    @pytest.mark.parametrize("age, weight",
                             [[random.randrange(1, 100), random.randrange(1, 100)] for _ in
                              range(5)])
    def test_update_fitness(self, animal, age, weight):
        """
        Tests if the formula of calculating fitness based on age and weight works correctly.
        """
        q_plus = 1 / (1 + (
                math.e ** (animal.params['phi_age'] * (age - animal.params['a_half']))))
        q_minus = 1 / (1 + (math.e ** (
                -animal.params['phi_weight'] * (weight - animal.params['w_half']))))
        theoretical_fitness = q_plus * q_minus

        animal.initiate_age(age)
        animal.initiate_weight(weight)

        assert theoretical_fitness == animal.fitness

    @pytest.mark.parametrize("weight", [0, -1])
    def test_update_fitness_non_positive_weight(self, animal, weight):
        """
        Tests the fitness of non-positive weight is always zero.
        """
        theoretical_fitness = 0

        animal.weight = weight

        assert theoretical_fitness == animal.fitness

    @pytest.mark.parametrize("N", [2, 3, 5, 10])
    def test_calculate_procreation_probability(self, animal, N):
        """
        Uses Z-test for proportions to test if the procreation probability is calculated correctly
        Parameters
        ----------
        animal: (instance of Animal class)
        N: (int)
            number of animals of same subclass in a cell
        """
        theoretical_procreation_probability = min(1,
                                                  animal.params["gamma"] * animal.fitness * (N - 1))
        sample_size = 200
        true_counter = 0
        for _ in range(sample_size):
            if animal.calculate_procreation_probability(N):
                true_counter += 1
        p_hat = true_counter / sample_size
        standard_error = (p_hat * (1 - p_hat) / sample_size) ** 0.5
        if standard_error != 0:  # To avoid division by 0 error
            Z = (p_hat - theoretical_procreation_probability) / standard_error
            p_value = stats.norm.cdf(Z)

            assert p_value > ALPHA

    def test_calculate_procreation_probability_one_N(self, animal):
        """
        Uses Z-test for proportions to test if the procreation probability is calculated correctly
        when there's only one animal in a cell.
        Parameters
        ----------
        animal: (instance of Animal class)
        """
        N = 1
        procreation_probability = animal.calculate_procreation_probability(N)
        assert procreation_probability == 0

    def test_birth(self, animal, mocker):
        """
        Tests that birth method returns a new instance of the animal.
        Parameters
        ----------
        animal: instance of Animal class
        mocker
        """
        arbitrary_positive_value = 1
        mocker.patch("random.gauss", return_value=arbitrary_positive_value)
        animal.weight = math.inf
        new_animal = animal.birth()
        assert isinstance(new_animal, type(animal))

    def test_birth_weight_too_great(self, animal, mocker):
        """
        Tests that birth method does not return an animal or alter the mother's weight
         if the birth weight leads to weight loss greater than the mother's weight.
        Parameters
        ----------
        animal (instance of Animal class)
        mocker
        """
        arbitrary_positive_birth_weight = 1
        mocker.patch("random.gauss", return_value=arbitrary_positive_birth_weight)
        initial_animal_weight = 0.5
        animal.weight = initial_animal_weight
        new_animal = animal.birth()
        assert new_animal is None and animal.weight == initial_animal_weight

    def test_birth_weight_loss_equal_mother_weight(self, animal, mocker):
        """
        Tests that birth method executes as expected when the weight loss is equal to the mother's
         weight.
        Parameters
        ----------
        animal (instance of Animal class)
        mocker
        """
        arbitrary_positive_birth_weight = 1
        mocker.patch("random.gauss", return_value=arbitrary_positive_birth_weight)
        animal.weight = arbitrary_positive_birth_weight * animal.params["xi"]
        new_animal = animal.birth()
        assert animal.weight == 0 and new_animal is not None

    def test_birth_weight_mean(self, animal):
        """
        Z test testing the birth weight mean. Uses truncnorm from scipy.stats to find the actual
        theoretical mean, given that the normal distribution has a cut-off at 0.
        """

        normal_mean = animal.params['w_birth']
        normal_sd = animal.params['sigma_birth']
        clip_value = 0
        clip_value_standardized = (clip_value - normal_mean) / normal_sd
        truncated_mean_standarized = truncnorm.stats(clip_value_standardized, math.inf, moments='m')
        truncated_mean = truncated_mean_standarized * normal_sd + normal_mean
        animal.weight = math.inf  # assures that mother can birth

        sample_size = 200
        weight_list = []
        for _ in range(sample_size):
            new_animal = animal.birth()
            if new_animal is not None:
                weight_list.append(new_animal.weight)

        mean_estimate = statistics.mean(weight_list)
        sd_estimate = statistics.stdev(weight_list)
        standard_error = sd_estimate / (sample_size ** 0.5)
        Z = (mean_estimate - truncated_mean) / standard_error
        p_value = stats.norm.cdf(Z)

        assert p_value > ALPHA

    def test_migration_or_not(self, animal):
        """
        Uses Z-test for proportions to test if the migration probability is calculated correctly.
        """
        sample_size = 200
        theoretical_migration_probability = animal.params["mu"] * animal.fitness
        true_counter = 0
        for _ in range(sample_size):
            if animal.migrate_or_not():
                true_counter += 1
        p_hat = true_counter / sample_size
        standard_error = (p_hat * (1 - p_hat) / sample_size) ** 0.5
        if standard_error != 0:  # To avoid division by 0 error
            Z = (p_hat - theoretical_migration_probability) / standard_error
            p_value = stats.norm.cdf(Z)

            assert p_value > ALPHA

    def test_migration_direction(self, animal):
        """
        Uses a chi-square test to see if migration_direction is uniformly distributed, treats
        direction as a categorical variable"""

        sample_size = 200
        observed_distribution = [0 for _ in range(4)]
        for _ in range(sample_size):
            observed_distribution[animal.migration_direction()] += 1

        chisq, p_value = stats.chisquare(observed_distribution)

        assert p_value > ALPHA


class Test_herbivores():
    @pytest.fixture(autouse=True)
    def create_herbivore(self):
        """
        Creates list of herbivore.
        """
        self.herbivore = ba.Herbivore(100, 10)

    @pytest.mark.parametrize("beta_value", [0, 0.75, 1, 1.25])
    def test_eat(self, beta_value):
        """
        Tests that the herbivore gains weight in correct proportion with the beta value and fodder.
        """
        ba.Herbivore.set_params({"beta": beta_value})
        fodder = 70
        theoretical_weight_gain = self.herbivore.params["beta"] * fodder

        first_weight = self.herbivore.weight
        self.herbivore.eat(fodder)
        second_weight = self.herbivore.weight

        assert second_weight == first_weight + theoretical_weight_gain


class Test_carnivores():
    @pytest.fixture(autouse=True)
    def create_carnivore(self):
        self.carnivore = ba.Carnivore(100, 10)

    @pytest.mark.parametrize("beta_value", [0, 0.75, 1, 1.25])
    def test_eat(self, beta_value):
        """
        Tests that the carnivore gains weight in correct proportion with the beta value and weight
        of prey."""
        ba.Carnivore.set_params({"beta": beta_value})
        weight_of_prey = 50
        theoretical_weight_gain = self.carnivore.params["beta"] * weight_of_prey

        first_weight = self.carnivore.weight
        self.carnivore.eat(weight_of_prey)
        second_weight = self.carnivore.weight

        assert second_weight == first_weight + theoretical_weight_gain

    def test_killing_probability_worst(self):
        """Tests killing probability output when the fitness disparity is negative"""
        carnivore = ba.Carnivore(1, 0)
        herbivore = ba.Herbivore(80, 40)
        kill = carnivore.killing_probability(herbivore)
        assert kill is False

    @pytest.mark.parametrize("denominator", [1.01, 1.2, 4, 8, 100])
    def test_killing_probability_average(self, denominator):
        """
        Uses Z-test for proportions to test if the killing probability is calculated correctly when
        the fitness disparity is between zero and DeltaPhiMax.
        """
        herbivore = ba.Herbivore(1, 0)

        fitness_disparity = self.carnivore.fitness - herbivore.fitness
        theoretical_killing_probability = fitness_disparity / self.carnivore.params["DeltaPhiMax"]

        sample_size = 200
        true_counter = 0
        for _ in range(sample_size):
            if self.carnivore.killing_probability(herbivore):
                true_counter += 1
        p_hat = true_counter / sample_size
        standard_error = (p_hat * (1 - p_hat) / sample_size) ** 0.5
        if standard_error != 0:  # To avoid division by 0 error
            Z = (p_hat - theoretical_killing_probability) / standard_error
            p_value = stats.norm.cdf(Z)

            assert p_value > ALPHA

    @pytest.mark.parametrize("DeltaPhiMax", [0.2, 0.3, 0.4, 0.5, 0.6])
    def test_killing_probability_positive_best(self, DeltaPhiMax):
        """
        Tests killing probability output when the fitness disparity is greater than DeltaPhiMax.
        """
        ba.Carnivore.set_params({"DeltaPhiMax": DeltaPhiMax})
        herbivore = ba.Herbivore(1, 0)
        kill = self.carnivore.killing_probability(herbivore)
        assert kill
