import math
import textwrap
import random
import pytest
import scipy.stats as st

import biosim.island as bi
import biosim.animal as ba
import biosim.landscape as bl

SEED = 1234
ALPHA = 0.01

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


class Test_island():

    def test_check_if_consisent_rows_input(self):
        """
        Tests if the length of the rows are of same length in the given island map string.
        """

        island = """\
               WWWWWW
               WLHHH
               WLDDHW
               WWWWWW"""
        island = textwrap.dedent(island)
        pytest.raises(ValueError, bi._check_if_consistent_rows_input, island)

    @pytest.mark.parametrize("island", ["""\
                                           WWWWWW
                                           WLHHHW
                                           WLDDHW
                                           WWWWLW""", """\
                                                           WWWWLW
                                                           WLHHHW
                                                           WLDDHW
                                                           WWWWWW""", """\
                                                                           WWWWWW
                                                                           WLHHHW
                                                                           WLDDHH
                                                                           WWWWWW""", """\
                                                                                        WWWWWW
                                                                                        DLHHHW
                                                                                        WLDDHW
                                                                                        WWWWWW"""
                                                                                                ])
    def test_check_if_island(self, island):
        """
        Test to check if given island parameter is actaully determines an island.
        It should be surrounded with Water.
        """
        island = textwrap.dedent(island)
        pytest.raises(ValueError, bi._check_if_island, island)

    @pytest.fixture()
    def island_3x3(self):
        """Creates island"""
        self.island = bi._create_island("""\
               WWWWW
               WLLLW
               WLLLW
               WLLLW
               WWWWW""")

    """
    def test_cycle(self, mocker):
    """

    def test_migration_integration_test(self):
        """
        Adjusts parameters, runs cycle and uses chi-square test on how many animals live and
        move to adjacent cells to see if animal dynamics are as expected.
        """
        geogr = """\
                WWWWW
                WLLLW
                WLLLW
                WLLLW
                WWWWW"""

        geogr = textwrap.dedent(geogr)
        island = bi._create_island(geogr)

        # Sets parameters so that no animal procreates, kills or dies,
        # and every animal migrates every time
        bi._set_animal_parameters("herbivore", {"gamma": 0, "omega": 0, 'eta': 0, 'mu': math.inf})
        bi._set_animal_parameters("carnivore", {"gamma": 0, "omega": 0, 'eta': 0, 'mu': math.inf,
                                                                        'DeltaPhiMax': math.inf})

        spawn_loc = (3, 3)
        spawn_cell = island[spawn_loc]
        herb_amount = 50
        carn_amount = 50

        ini_herbs = [{'loc': spawn_loc,
                      'pop': [{'species': 'Herbivore',
                               'age': 5,
                               'weight': 40}
                              for _ in range(herb_amount)]}]
        ini_carns = [{'loc': spawn_loc,
                      'pop': [{'species': 'Carnivore',
                               'age': 5,
                               'weight': 60}
                              for _ in range(carn_amount)]}]

        bi._add_animal_to_island(ini_herbs + ini_carns)

        bi._cycle()

        adjacent_cells = spawn_cell.adjacent_cells
        # expects that all animals live, do not breed and migrate to the adjacent cells
        expected_distribution = [(herb_amount + carn_amount) / 4 for _ in range(4)]
        observed_distribution = [len(cell.herb_list + cell.carn_list) for cell in adjacent_cells]

        chisq, p = st.chisquare(observed_distribution, expected_distribution)

        assert p > ALPHA

    def test_no_water_migration(self):
        """
        Test that no animals move to migrating cells.
        """
        geogr = """\
                WWW
                WLW
                WWW"""

        geogr = textwrap.dedent(geogr)
        island = bi._create_island(geogr)

        # Sets parameters so that no animal procreates, kills or dies,
        # and every animal migrates every time
        bi._set_animal_parameters("herbivore", {"gamma": 0, "omega": 0, 'eta': 0, 'mu': math.inf})
        bi._set_animal_parameters("carnivore", {"gamma": 0, "omega": 0, 'eta': 0, 'mu': math.inf,
                                                                     'DeltaPhiMax': math.inf})

        spawn_loc = (2, 2)
        spawn_cell = island[spawn_loc]

        herb_amount = 50
        ini_herbs = [{'loc': spawn_loc,
                      'pop': [{'species': 'Herbivore',
                               'age': 5,
                               'weight': 40}
                              for _ in range(herb_amount)]}]
        carn_amount = 50
        ini_carns = [{'loc': spawn_loc,
                      'pop': [{'species': 'Carnivore',
                               'age': 5,
                               'weight': 60}
                              for _ in range(carn_amount)]}]

        total_amount_animals = herb_amount + carn_amount

        bi._add_animal_to_island(ini_herbs + ini_carns)

        bi._cycle()

        assert len(spawn_cell.herb_list) + len(spawn_cell.carn_list) == total_amount_animals

    def test_migration_herb(self, island_3x3):
        """
        Adjusts parameters, runs cycle and uses chi-square test on how many animals live and
        move to adjacent cells to see if animal dynamics are as expected.
        """

        spawn_loc = (3, 3)
        spawn_cell = self.island[spawn_loc]
        herb_amount = 400

        ini_herbs = [{'loc': spawn_loc,
                      'pop': [{'species': 'Herbivore',
                               'age': 5,
                               'weight': 200}
                              for _ in range(herb_amount)]}]

        fitness = ba.Herbivore(40, 5).fitness
        mu = ba.Herbivore.params["mu"]
        migration_probability = mu*fitness

        expected_amount_in_every_cell = migration_probability*herb_amount / 4

        bi._add_animal_to_island(ini_herbs)

        bi._migration_stage(bi._get_cells())

        adjacent_cells = spawn_cell.adjacent_cells

        expected_distribution = [expected_amount_in_every_cell for _ in range(4)]
        expected_distribution.append((1 - migration_probability) * herb_amount)

        observed_distribution = [len(cell.herb_list) for cell in adjacent_cells]
        observed_distribution.append(len(spawn_cell.herb_list))

        chisq, p = st.chisquare(observed_distribution, expected_distribution)

        assert p > ALPHA

    def test_migration_carn(self, island_3x3):
        """
        Adjusts parameters, runs cycle and uses chi-square test on how many animals live and
        move to adjacent cells to see if animal dynamics are as expected.
        """

        spawn_loc = (3, 3)
        spawn_cell = self.island[spawn_loc]
        carn_amount = 400

        ini_carns = [{'loc': spawn_loc,
                      'pop': [{'species': 'Carnivore',
                               'age': 5,
                               'weight': 200}
                              for _ in range(carn_amount)]}]

        fitness = ba.Carnivore(40, 5).fitness
        mu = ba.Carnivore.params["mu"]
        migration_probability = mu * fitness

        expected_amount_in_every_cell = migration_probability * carn_amount / 4

        bi._add_animal_to_island(ini_carns)

        bi._migration_stage(bi._get_cells())

        adjacent_cells = spawn_cell.adjacent_cells

        expected_distribution = [expected_amount_in_every_cell for _ in range(4)]
        expected_distribution.append((1 - migration_probability) * carn_amount)

        observed_distribution = [len(cell.carn_list) for cell in adjacent_cells]
        observed_distribution.append(len(spawn_cell.carn_list))

        chisq, p = st.chisquare(observed_distribution, expected_distribution)

        assert p > ALPHA

    @pytest.fixture()
    def cyclical_stages_setup(self, island_3x3):
        """Used to test the cyclical stages"""

        self.spawn_loc = (2, 2)

        herb_amount = 50
        carn_amount = 50

        ini_herbs = [{'loc': self.spawn_loc,
                      'pop': [{'species': 'Herbivore',
                               'age': 5,
                               'weight': 40}
                              for _ in range(herb_amount)]}]
        carn_amount = 50
        ini_carns = [{'loc': self.spawn_loc,
                      'pop': [{'species': 'Carnivore',
                               'age': 5,
                               'weight': 60}
                              for _ in range(carn_amount)]}]

        bi._add_animal_to_island(ini_herbs + ini_carns)

        self.all_animals = []
        for cell in self.island.values():
            for animal in cell.herb_list + cell.carn_list:
                self.all_animals.append(animal)

    def test_procreation_stage(self, cyclical_stages_setup, mocker):
        """Tests if all animals get checked for procreation once whenever _procreation_stage()
         is called"""

        spies = [mocker.spy(animal, 'calculate_procreation_probability')
                 for animal in self.all_animals]

        bi._procreation_stage(bi._get_cells())

        expected_call_amount = 1

        calls = [spy.call_count for spy in spies]

        assert all(calls) == expected_call_amount and calls[0] == expected_call_amount

    def test_migration_stage(self, cyclical_stages_setup, mocker):
        """Tests if all animals get checked for migration only once whenever _procreation_stage()
         is called"""

        spies = [mocker.spy(animal, 'migrate_or_not') for animal in self.all_animals]

        bi._migration_stage(bi._get_cells())

        expected_call_amount = 1

        calls = [spy.call_count for spy in spies]

        assert all(calls) and calls[0] == expected_call_amount

    def test_aging_stage(self, cyclical_stages_setup, mocker):
        """Tests if all animals age once when _aging_stage() is called"""

        spies = [mocker.spy(animal, 'aging') for animal in self.all_animals]

        bi._aging_stage(bi._get_cells())

        expected_call_amount = 1

        calls = [spy.call_count for spy in spies]

        assert all(calls) and calls[0] == expected_call_amount

    def test_weight_loss_stage(self, cyclical_stages_setup, mocker):
        """Tests if all animals get checked for migration only once whenever _procreation_stage()
        is called"""

        spies = [mocker.spy(animal, 'weight_loss') for animal in self.all_animals]

        bi._weight_loss_stage(bi._get_cells())

        expected_call_amount = 1

        calls = [spy.call_count for spy in spies]

        assert all(calls) and calls[0] == expected_call_amount

    def test_death_stage(self, cyclical_stages_setup, mocker):
        """Tests if all animals get checked for death once whenever _death_stage() is called"""
        mocker.patch("random.random", return_value=1)

        spies = [mocker.spy(animal, 'update_life_status') for animal in self.all_animals]

        bi._death_stage(bi._get_cells())

        expected_call_amount = 1

        calls = [spy.call_count for spy in spies]

        assert all(calls) and calls[0] == expected_call_amount

    def test_feed_herbivores_stage(self, cyclical_stages_setup, mocker):
        """Tests if all herbivores can eat once when _death_stage() is called"""
        bl.Lowland.set_params({"f_max": math.inf})

        spies = [mocker.spy(herbivore, 'eat') for
                 herbivore in self.island[self.spawn_loc].herb_list]

        bi._feed_herbivores_stage(bi._get_cells())

        expected_call_amount = 1

        calls = [spy.call_count for spy in spies]

        assert all(calls) and calls[0] == expected_call_amount

    def test_feed_carnivores_stage(self, cyclical_stages_setup, mocker):
        """Tests if all carnivoress will try eating each herbivore once if killing
        probability is 0%."""
        mocker.patch("random.random", return_value=1)

        spies = [mocker.spy(carnivore, 'killing_probability') for
                 carnivore in self.island[self.spawn_loc].carn_list]

        bi._feed_carnivores_stage(bi._get_cells())

        expected_call_amount = len(self.island[self.spawn_loc].herb_list)

        calls = [spy.call_count for spy in spies]

        assert all(calls) and calls[0] == expected_call_amount

    def test_feed_carnivores_stage_all_kills(self, cyclical_stages_setup, mocker):
        """Tests if all carnivoress eat once if killing probability is 100% and
         F is is equal to the herbivores' individual weight."""
        mocker.patch("random.random", return_value=0)
        F = 50
        spies = [mocker.spy(carnivore, 'killing_probability') for carnivore in
                 self.island[self.spawn_loc].carn_list]

        for carnivore in self.island[self.spawn_loc].carn_list:
            carnivore.weight = 80

        for herbivore in self.island[self.spawn_loc].herb_list:
            herbivore.weight = F

        bi._feed_carnivores_stage(bi._get_cells())

        expected_call_amount = 1

        calls = [spy.call_count for spy in spies]

        assert all(calls) and calls[0] == expected_call_amount
        assert len(self.island[self.spawn_loc].herb_list) == 0

    def test_add_animals_to_island(self, island_3x3):
        """Tests if ValueError is raised if the species is wrong."""
        ini_pop = [{'loc': (3, 3),
                      'pop': [{'species': 'Herbivor',
                               'age': 5,
                               'weight': 40}
                              for _ in range(2)]}]
        pytest.raises(ValueError, bi._add_animal_to_island, ini_pop)

    def test_add_animals_to_island_water(self, island_3x3):
        "Tests if ValueError is raised if animals are placed on a water cell."
        ini_pop = [{'loc': (1, 1),
                    'pop': [{'species': 'Herbivore',
                             'age': 5,
                             'weight': 40}
                            for _ in range(2)]}]
        pytest.raises(ValueError, bi._add_animal_to_island, ini_pop)

    def test_island_locations(self):
        """Tests that co-ordinates are correctly given"""
        island = "WW\nWW"
        island = bi._create_island(island)
        assert (1, 1) in island.keys() and (1, 2) in island.keys() \
               and (2, 1) in island.keys() and (2, 2) in island.keys()
        assert len(island.values()) == 4

    def test_get_animal_vitals(self, island_3x3):
        """Tests that _get_animal_vitals() returns animal vitals correctly."""
        xherb, yherb = (3, 3)
        herb_age = 5
        herb_weight = 40
        herb_amount = 3
        ini_herb = [{'loc': (xherb, yherb),
                    'pop': [{'species': 'Herbivore',
                             'age': herb_age,
                             'weight': herb_weight}
                            for _ in range(herb_amount)]}]

        xcarn, ycarn = (2, 2)
        carn_age = 1
        carn_weight = 55
        carn_amount = 2
        ini_carn = [{'loc': (xcarn, ycarn),
                    'pop': [{'species': 'Carnivore',
                             'age': carn_age,
                             'weight': carn_weight}
                            for _ in range(carn_amount)]}]

        bi._add_animal_to_island(ini_herb + ini_carn)

        vitals = bi._get_animal_vitals()

        assert len(vitals["age"]["Herbivore"]) == herb_amount
        assert all(vitals["age"]["Herbivore"]) and vitals["age"]["Herbivore"][0] == herb_age
        assert all(vitals["weight"]["Herbivore"]) and \
               vitals["weight"]["Herbivore"][0] == herb_weight
        assert len(vitals["age"]["Carnivore"]) == carn_amount
        assert all(vitals["age"]["Carnivore"]) and vitals["age"]["Carnivore"][0] == carn_age
        assert all(vitals["weight"]["Carnivore"]) and \
               vitals["weight"]["Carnivore"][0] == carn_weight
