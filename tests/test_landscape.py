import math
import pytest
import random
import biosim.animal as ba
import biosim.landscape as bl

SEED = 1234
ALPHA = 0.01  # for statistical testing


random.seed(SEED)


@pytest.fixture(autouse=True)
def reset_params():
    """Resets params to default values"""
    yield
    bl.Lowland.set_params(bl.Lowland.default_params)
    bl.Highland.set_params(bl.Highland.default_params)
    bl.Desert.set_params(bl.Desert.default_params)
    bl.Water.set_params(bl.Water.default_params)
    ba.Herbivore.set_params(ba.Herbivore.default_params)
    ba.Carnivore.set_params(ba.Carnivore.default_params)


@pytest.mark.parametrize("cell", [bl.Lowland(), bl.Highland(), bl.Desert(), bl.Water()])
class Test_all_landscape_types:

    @pytest.fixture(autouse=True)
    def add_animals(self, cell):
        """
        Adds animal species to their respective species list.
        """
        cell.herb_list = [ba.Herbivore(10, 10)
                          for _ in range(10)]
        cell.carn_list = [ba.Carnivore(10, 10)
                          for _ in range(10)]

    @pytest.mark.parametrize("value", [200 * i for i in range(5)])
    def test_set_params(self, cell, value):
        """
        Tests the assignment of parameter is correct.
        """
        type(cell).set_params({"f_max": value})
        assert cell.params["f_max"] == value

    def test_set_params_negative_value(self, cell):
        """Tests if ValueError is raise for negative fodder given."""
        pytest.raises(ValueError, type(cell).set_params, {"f_max": -1})

    def test_set_params_non_existent_param(self, cell):
        """Tests if ValueError is raise for negative fodder given."""
        pytest.raises(ValueError, type(cell).set_params, {"non-existent-parameter": 10})

    def test_set_animal_parameters_non_existent_species(self, cell):
        """Tests if ValueError is raise for negative fodder given."""
        pytest.raises(ValueError, bl.set_animal_parameters, "Herbicarn", {"F": 70})

    def test_set_fodder(self, cell):
        """
        Tests the available fodder is assigned correctly.
        """
        initial_fodder = 50
        cell.available_fodder = initial_fodder
        cell.set_fodder()
        assert cell.available_fodder == type(cell).params["f_max"]

    def test_sort_fitness_decending(self, cell):
        """
        Tests if _sort_fitness() sorts animals by fitness in descending order."""
        cell._sort_fitness()
        decending_fitness = True
        for i in range(len(cell.herb_list) - 1):
            herbivore1 = cell.herb_list[i]
            herbivore2 = cell.herb_list[i + 1]
            if herbivore2.fitness > herbivore1.fitness:
                decending_fitness is False
        assert decending_fitness

    def test_sort_fitness_acending(self, cell):
        """Tests if _sort_fitness() sorts animals by fitness in ascending order."""
        cell._sort_fitness(descending=False)
        acending_fitness = True
        for i in range(len(cell.herb_list) - 1):
            herbivore1 = cell.herb_list[i]
            herbivore2 = cell.herb_list[i + 1]
            if herbivore2.fitness < herbivore1.fitness:
                acending_fitness is False
        assert acending_fitness

    def test_remove_animal_if_dead_herbivore(self, cell):
        """
        Tests if remove_animal_if_dead, successfully removes herbivore if dead.
        """
        herbivore = cell.herb_list[0]
        cell.remove_animal_if_dead(True, herbivore)
        herbivore_removed = True
        if herbivore in cell.herb_list:
            herbivore_removed = False
        assert herbivore_removed

    def test_remove_animal_if_dead_carnivore(self, cell):
        """
        Tests if remove_animal_if_dead, successfully removes carnivore if dead.
        """
        carnivore = cell.carn_list[0]
        cell.remove_animal_if_dead(True, carnivore)
        carnivore_removed = True
        if carnivore in cell.carn_list:
            carnivore_removed = False
        assert carnivore_removed

    def test_get_animal_list_herbivore(self, cell):
        """
        Tests if the function retrieves the correct herb_list.
        """
        herbivore = ba.Herbivore(100, 10)
        desired_list = cell.herb_list
        assert cell.get_animal_list(herbivore) == desired_list

    def test_get_animal_list_carnivore(self, cell):
        """
        Tests if the function retrieves the correct herb_list.
        """
        carnivore = ba.Carnivore(100, 10)
        desired_list = cell.carn_list
        assert cell.get_animal_list(carnivore) == desired_list

    def test_feed_herbivore_scarcity(self, cell, mocker):
        """Tests to see if feed_herbivore() correctly limits the amount of herbivores that eat."""
        fodder = 50
        cell.available_fodder = fodder
        spy = mocker.spy(ba.Animal, "eat")
        desired_eat_calls = fodder / ba.Herbivore.params["F"]
        cell.feed_herbivores()

        assert spy.call_count == desired_eat_calls

    def test_feed_herbivore_fodder_reduction(self, cell):
        """Tests to see if feed_herbivore() correctly reduced the amount of available fodder"""
        initial_fodder = 500
        cell.available_fodder = initial_fodder
        cell.feed_herbivores()
        expected_available_amount = initial_fodder - len(cell.herb_list) * ba.Herbivore.params["F"]

        assert cell.available_fodder == expected_available_amount

    def test_facilitate_hunting_fullness(self, cell, mocker):
        "Tests if a carnivore stop eating after it has eaten fodder F."
        ba.Carnivore.set_params({"DeltaPhiMax": 0.001, "F": 5})
        cell.carn_list = [cell.carn_list[0]]  # tests on one carnivore
        spy = mocker.spy(ba.Animal, "eat")
        herb_weight = 1
        for herb in cell.herb_list:
            herb.weight = herb_weight

        expected_eat_calls = math.ceil(ba.Carnivore.params["F"] / herb_weight)
        cell.facilitate_hunting()

        assert spy.call_count == expected_eat_calls

    def test_facilitate_hunting_one_try(self, cell, mocker):
        "Tests if a carnivore stops eating after it has tried preying on all herbivores in a cell."

        ba.Carnivore.set_params({"DeltaPhiMax": 0.001, "F": math.inf})

        spy = mocker.spy(ba.Animal, "eat")
        cell.carn_list = cell.carn_list[:1]
        for herb in cell.herb_list:
            herb.initiate_weight(0.00001)

        expected_eat_calls = len(cell.herb_list)
        cell.facilitate_hunting()

        assert spy.call_count == expected_eat_calls

    def test_procreate_herbivores(self, cell, mocker):
        """
        Uses mocker.patch to test if herbivore procreates when birth takes place everytime.
        """
        mocker.patch('random.random', return_value=0)  # assumes birth every time
        spy = mocker.spy(ba.Animal, 'birth')
        expected_amount_of_calls = len(cell.herb_list)
        for herb in cell.herb_list:
            herb.initiate_weight(100)
        cell.procreate_herbivores()
        assert spy.call_count == expected_amount_of_calls
        assert len(cell.herb_list) == expected_amount_of_calls * 2

    def test_procreate_herbivores_assumes_no_birth(self, cell, mocker):
        """
        Uses mocker.patch to test if herbivore procreates when no birth takes place.
        """
        mocker.patch('random.random', return_value=1)  # assumes no birth
        initial_amount_of_herbivores = len(cell.herb_list)
        cell.procreate_herbivores()
        second_amount_of_herbivores = len(cell.herb_list)
        assert initial_amount_of_herbivores == second_amount_of_herbivores

    def test_procreate_carnivores(self, cell, mocker):
        """
        Uses mocker.patch to test if carnivore procreates when birth takes place everytime.
        """
        mocker.patch('random.random', return_value=0)  # assumes birth everytime
        spy = mocker.spy(ba.Animal, 'birth')
        expected_amount_of_calls = len(cell.carn_list)
        cell.procreate_carnivores()
        assert spy.call_count == expected_amount_of_calls
        assert len(cell.carn_list) == expected_amount_of_calls * 2

    def test_procreate_carnivores_no_birth(self, cell, mocker):
        """
        Uses mocker.patch to test if herbivore procreates when no birth takes place.
        """
        mocker.patch('random.random', return_value=1)  # assumes no birth
        initial_amount_of_carnivores = len(cell.carn_list)
        cell.procreate_carnivores()
        second_amount_of_carnivores = len(cell.carn_list)
        assert initial_amount_of_carnivores == second_amount_of_carnivores

    def test_get_animals(self, cell):
        """Tests if it gets animal_list which has both herbivore and carnivaore."""
        assert cell.herb_list + cell.carn_list == [animal for animal in cell.get_animals()]

    def test_age_animals(self, cell, mocker):
        """
        Tests that aging() runs on all animals in cell when age_animals() is called.
        """
        expected_amount_of_calls = 1
        spies = [mocker.spy(animal, 'aging') for animal in cell.get_animals()]
        cell.age_animals()
        assert all([spy.call_count for spy in spies]) == expected_amount_of_calls

    def test_update_life_status_of_animals(self, cell, mocker):
        """Tests that update_fitness runs on all animals in cell when update_fitness_of_animals()
        is called"""
        mocker.patch("random.random", return_value=1)
        expected_amount_of_calls = 1
        spies = [mocker.spy(animal, 'update_life_status') for animal in cell.get_animals()]
        cell.update_life_status_of_animals()
        assert all([spy.call_count for spy in spies]) == expected_amount_of_calls

    def test_animals_lose_weight(self, cell, mocker):
        """
        Tests that weight_loss() runs on all animals in cell when animals_lose_weight() is called.
        """
        expected_amount_of_calls = 1
        spies = [mocker.spy(animal, 'weight_loss') for animal in cell.get_animals()]
        cell.animals_lose_weight()
        assert all([spy.call_count for spy in spies]) == expected_amount_of_calls
