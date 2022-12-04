"""
Module containing all variables and functions related to the upper-most layer of the simulation,
 namely the island
 """

import numpy as np
import textwrap
import biosim.animal as ba
import biosim.landscape as bl

type_dict = {"H": bl.Highland, "L": bl.Lowland, "D": bl.Desert, "W": bl.Water}
direction_dict = {"up": (-1, 0), "right": (0, 1), "down": (1, 0),  "left": (0, -1)}
island = {}
island_shape = []


def _create_island(landscape_string):
    """
    Creates Island from textgrid.

    Parameters
    ----------
    landscape_string: str

    Returns
    --------
    island: dict
    """

    landscape_string = textwrap.dedent(landscape_string)
    _check_if_consistent_rows_input(landscape_string)
    _find_island_shape(landscape_string)
    _check_if_island(landscape_string)
    island.clear()
    for x, line in enumerate(landscape_string.split("\n")):
        for y, letter in enumerate(line):
            island[(x + 1, y + 1)] = _create_cell(letter)
    _insert_adjacent_cells()
    return island


def _insert_adjacent_cells():
    """
    Finds every cell's adjacent cells and inserts them into the adjacent_cells list.
    """

    for (x, y), cell in island.items():
        for (dx, dy) in direction_dict.values():
            newx, newy = x + dx, y + dy
            if (newx, newy) in island:
                cell.adjacent_cells.append(island[(newx, newy)])
            else:
                cell.adjacent_cells.append(None)


def _find_island_shape(landscape_string):
    """Returns shape of island"""

    text_split = landscape_string.splitlines()
    x = len(text_split)
    y = len(text_split[0])
    island_shape.clear()
    island_shape.append((x, y))
    return island_shape


def _check_if_island(landscape_string):
    """
    Checks if given landscape string is an island i.e. it must be surrounded by water.
    Parameters
    ----------
    landscape_string: string
    """
    for row_nr, line in enumerate(landscape_string.splitlines()):
        for column_nr, letter in enumerate(line):
            if row_nr == 0 or row_nr == len(landscape_string.splitlines()) - 1\
                    or column_nr == 0 or column_nr == len(line) - 1:
                if letter != "W":
                    raise ValueError("Island must be surrounded by water")


def _check_if_consistent_rows_input(landscape_string):
    """
    Checks if the island has same number of row length
    Parameters
    ----------
    landscape_string: string
    """

    rows = landscape_string.split("\n")
    for i in range(len(rows) - 1):
        if len(rows[i]) != len(rows[i + 1]):
            raise ValueError("Island input must have consistent row length")


def _create_cell(landscape):
    """
    Creates a cell (an instance of landscape) of the subtype given in the text code. Uses type_dict.
    Parameters
    ----------
    landscape: string
        Island cell type

    Returns
    -------
    cell: instance of the given subtype
    """
    try:
        cell = type_dict[landscape]()
    except KeyError:
        raise ValueError(f"The following input is not a valid landscape code: '{landscape}'")
    return cell


def _get_cells():
    """
    Returns all inhabitable cells on Island
    Returns
    -------
    _cells: list
        all cell objects
    """
    cells = [cell for cell in island.values() if cell.accessability]
    return cells


def _cycle():
    """
    Iterates through all habitable cells and sets off all cyclical process.
    """
    # 1a, feed Herbivore
    cells = _get_cells()
    _feed_herbivores_stage(cells)

    # 1b, feed Carnivore
    _feed_carnivores_stage(cells)

    # 2, procreation
    _procreation_stage(cells)

    # 3, migration

    _migration_stage(cells)

    # 4, Animal aging
    _aging_stage(cells)

    # 5, lose weight
    _weight_loss_stage(cells)

    # 6, die
    _death_stage(cells)


def _add_animal_to_island(entries):
    """
    Adds animals to the cells specified.
    Raises error if the animal object is put in Water cell.
    Parameters
    ----------
    entries: list
    """
    for cell in entries:
        if island[cell["loc"]].accessability:
            for animal in cell['pop']:
                if animal["species"] == "Herbivore":
                    herbivore = ba.Herbivore(animal["weight"], animal["age"])
                    island[cell["loc"]].herb_list.append(herbivore)
                elif animal["species"] == "Carnivore":
                    carnivore = ba.Carnivore(animal["weight"], animal["age"])
                    island[cell["loc"]].carn_list.append(carnivore)
                else:
                    raise ValueError("'Herbivore' and 'Carnivore' are the only accepted species.")
        else:
            raise ValueError(
                f"{cell['loc']} is a water cell. Animals cannot be placed in water cell.")


def _set_landscape_parameters(landscape, parameters):
    """
    Sets landscape parameters according to the landscape type.
    Parameters
    ----------
    landscape
    parameters
    """
    type_dict[landscape].set_params(parameters)


def _set_animal_parameters(species, parameters):
    """
    Sets animal parameters according to the animal parameter.
    Parameters
    ----------
    species
    parameters
    """
    bl.set_animal_parameters(species, parameters)


def _num_animals():
    """
    Total number of animal object
    Returns
    -------
    _num_animals: int
        total number of animal object
    """
    per_species = _num_animals_per_species()
    num_animals = sum([num for num in per_species.values()])
    return num_animals


def _num_animals_per_species():
    """
    Total number of animal object per species
    Returns
    -------
    _num_animals_per_species: int
        total number of animal object per species
    """
    return bl.num_animals_per_species()


def _feed_herbivores_stage(cells):
    """
    Sets the fodder and feeds the herbivore in a cell.
    Parameters
    ----------
    cells

    """
    for cell in cells:
        cell.set_fodder()
        cell.feed_herbivores()


def _feed_carnivores_stage(cells):
    """
    Feed the carnivore in the cell.
    Parameters
    ----------
    cells
    """
    for cell in cells:
        cell.facilitate_hunting()


def _procreation_stage(cells):
    """
    Updates the fitness of the animal.
    Procreation process for herbivore and carnivore.
    Parameters
    ----------
    cells
    """
    for cell in cells:
        cell.procreate_herbivores()
        cell.procreate_carnivores()


def _migration_stage(cells):
    """
    Migrates the animal in the cell if they migrate.
    Parameters
    ----------
    cells
    """
    for cell in cells:
        cell.migrate_herbivores()
        cell.migrate_carnivores()


def _aging_stage(cells):
    """
    The age of the animal object is increased by one every year.
    Parameters
    ----------
    cells

    """
    for cell in cells:
        cell.age_animals()


def _weight_loss_stage(cells):
    """
    The weight of the animal object is decreased.
    Parameters
    ----------
    cells
    """
    for cell in cells:
        cell.animals_lose_weight()


def _death_stage(cells):
    """
    If death is true. The animal is eliminated from the list and the cell.
    Parameters
    ----------
    cells: list
        list of Landscape objects
    """
    for cell in cells:
        cell.update_life_status_of_animals()


def _reset_counter():
    """
    Resets the counter of carnivore and herbivore count.
    """
    ba.Herbivore.reset_counter()
    ba.Carnivore.reset_counter()


def _get_animal_distributions():
    """
    Creates two-dimensional arrays denoting each cell's amount of herbivores and carnivore
    Returns
    -------
    dist_dict: dict
        Dictionary containing each of the species distribution.
    """
    distribution_herb = np.zeros(island_shape[0])
    distribution_carn = np.zeros(island_shape[0])
    for (x, y), cell in island.items():
        distribution_herb[x - 1, y - 1] = len(cell.herb_list)
        distribution_carn[x - 1, y - 1] = len(cell.carn_list)
    dist_dict = {"Herbivore": distribution_herb, "Carnivore": distribution_carn}

    return dist_dict


def _get_animal_vitals():
    vitals = {"age": {"Herbivore": [], "Carnivore": []},
              "weight": {"Herbivore": [], "Carnivore": []},
              "fitness": {"Herbivore": [], "Carnivore": []}}

    for cell in _get_cells():
        vitals["age"]["Herbivore"] += cell.get_age()[0]
        vitals["weight"]["Herbivore"] += cell.get_weight()[0]
        vitals["fitness"]["Herbivore"] += cell.get_fitness()[0]

        vitals["age"]["Carnivore"] += cell.get_age()[1]
        vitals["weight"]["Carnivore"] += cell.get_weight()[1]
        vitals["fitness"]["Carnivore"] += cell.get_fitness()[1]

    return vitals
