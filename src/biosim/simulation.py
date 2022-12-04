"""
Module containing the BioSim class, which acts as the user interface of the package.
"""

# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2021 Hans Ekkehard Plesser / NMBU


import os
import pickle
import random
import sys
import time
import biosim.island as bi
from biosim.visualisation import Graphics


class BioSim:
    def __init__(self, island_map, ini_pop, seed,
                 vis_years=1, ymax_animals=None, cmax_animals=None, hist_specs=None,
                 img_dir=None, img_base=None, img_fmt=None, img_years=None,
                 log_file=None):

        """
        :param island_map: Multi-line string specifying island geography
        :param ini_pop: List of dictionaries specifying initial population
        :param seed: Integer used as random number seed
        :param ymax_animals: Number specifying y-axis limit for graph showing animal numbers
        :param cmax_animals: Dict specifying color-code limits for animal densities
        :param hist_specs: Specifications for histograms, see below
        :param vis_years: years between visualization updates (if 0, disable graphics)
        :param img_dir: String with path to directory for figures
        :param img_base: String with beginning of file name for figures
        :param img_fmt: String with file type for figures, e.g. 'png'
        :param img_years: years between visualizations saved to files (default: vis_years)
        :param log_file: If given, write animal counts to this file

        If ymax_animals is None, the y-axis limit should be adjusted automatically.
        If cmax_animals is None, sensible, fixed default values should be used.
        cmax_animals is a dict mapping species names to numbers, e.g.,
           {'Herbivore': 50, 'Carnivore': 20}

        hist_specs is a dictionary with one entry per property for which a histogram shall be shown.
        For each property, a dictionary providing the maximum value and the bin width must be
        given, e.g.,
            {'weight': {'max': 80, 'delta': 2}, 'fitness': {'max': 1.0, 'delta': 0.05}}
        Permitted properties are 'weight', 'age', 'fitness'.

        If img_dir is None, no figures are written to file. Filenames are formed as

            f'{os.path.join(img_dir, img_base)}_{img_number:05d}.{img_fmt}'

        where img_number are consecutive image numbers starting from 0.

        img_dir and img_base must either be both None or both strings.
        """

        if img_base is None or img_dir is None:
            self._img_base = None
            self._img_dir = None

        self._img_base = img_base
        self._img_dir = img_dir
        self._img_years = img_years
        self._vis_years = vis_years
        self._img_fmt = img_fmt
        self.island_map = island_map
        self.hist_specs = hist_specs
        self.cmax_animals = cmax_animals
        self.y_max_animals = ymax_animals
        self._graphics = Graphics(self._img_dir, self._img_base, self._img_fmt, self.y_max_animals)
        self.log_file = log_file

        self.set_seed(seed)
        self.reset_counter()
        self.years = 0
        self.island = bi._create_island(island_map)
        bi._add_animal_to_island(ini_pop)

    def set_seed(self, seed):
        """Sets the seed for random number generator."""
        random.seed(seed)

    def set_animal_parameters(self, species, params):
        """
        Set parameters for animal species.
        Parameters
        ---------
        species: String
            Name of animal species
        params: Dict
            Valid parameter specification for species
        """
        bi._set_animal_parameters(species, params)

    def set_landscape_parameters(self, landscape, params):
        """
        Set parameters for landscape type.

        Parameters
        ---------
        landscape: String
            Code letter for landscape
        params: Dict
            Valid parameter specification for landscape
        """
        bi._set_landscape_parameters(landscape, params)

    def add_population(self, population):
        """
        Add population to the island.
        Parameters
        ----------
        population: list
            List of dictionaries specifying population.
        """
        bi._add_animal_to_island(population)

    def reset_counter(self):
        """
        Call reset counter function of island class.
        """
        bi._reset_counter()

    @property
    def year(self):
        """Last year simulated.
        Returns
        -------
        year: int
            Last simulated year.
        """
        return self.years

    @property
    def num_animals(self):
        """
        Calls num_animal function that returns total number of animals on island.
        Returns
        -------
        num_animals: int
            total number of animal object
        """
        return bi._num_animals()

    @property
    def num_animals_per_species(self):
        """
        Number of animals per species in island, as dictionary.
        Returns
        -------
        _num_animals_per_species: int
            total number of animal object per species
        """
        num_animals_per_species = bi._num_animals_per_species()
        return num_animals_per_species

    def simulate(self, num_years, vis_years=None, img_steps=None):
        """
        Run simulation while visualizing the result.

        Parameters
        --------
        num_years: int
            number of simulation steps to execute
        vis_years: int
            interval between visualization updates
        img_steps: int
            interval between visualizations saved to files
                          (default: vis_steps)

        """
        start_time = time.time()
        if vis_years is None:
            vis_years = self._vis_years

        if img_steps is None:
            if self._img_years is None:
                img_steps = vis_years
            else:
                img_steps = self._img_years

        if vis_years != 0 and img_steps % vis_years != 0:
            raise ValueError('img_steps must be multiple of vis_steps')

        self._final_year = self.years + num_years

        if vis_years != 0:
            self._graphics.setup(self._final_year, img_steps, self.island_map, self.log_file)

        while self.years < self._final_year:
            bi._cycle()
            self.years += 1
            if vis_years > 0:
                if self.years % vis_years == 0:
                    self._graphics.update(self.years,
                                          bi._get_animal_distributions(),
                                          self.cmax_animals,
                                          self.num_animals_per_species,
                                          bi._get_animal_vitals(),
                                          self.hist_specs)

        finish_time = time.time()
        print("Elapsed time: {:.6} seconds".format(finish_time - start_time))

    def make_movie(self, movie_fmt=None):
        """
        Creates MPEG4 movie from visualization images saved.

        .. :note:
            Requires ffmpeg for MP4 and magick for GIF

        The movie is stored as img_base + movie_fmt.
        """

        self._graphics.make_movie(movie_fmt)

    def save(self, file_dir, file_name="island_state_save"):
        """Saves Biosim object in its current state to a specified file.
        WARNING: sets recursion limit to 1500 during execution"""
        _initial_rec_lim = sys.getrecursionlimit()
        sys.setrecursionlimit(1500)
        path = os.path.join(file_dir, file_name)
        with open(path, 'wb') as file:
            pickle.dump(self, file)
        sys.setrecursionlimit(_initial_rec_lim)

    @classmethod
    def load(cls, filepath):
        """Opens a saved BioSim object"""
        with open(filepath, 'rb') as file:
            return pickle.load(file)
