"""
:mod:`randvis.graphics` provides graphics support for RandVis.

.. note::
   * This module requires the program ``ffmpeg`` or ``convert``
     available from `<https://ffmpeg.org>` and `<https://imagemagick.org>`.
   * You can also install ``ffmpeg`` using ``conda install ffmpeg``
   * You need to set the  :const:`_FFMPEG_BINARY` and :const:`_CONVERT_BINARY`
     constants below to the command required to invoke the programs
   * You need to set the :const:`_DEFAULT_FILEBASE` constant below to the
     directory and file-name start you want to use for the graphics output
     files.

"""

import os
import subprocess

import matplotlib.pyplot as plt
import numpy as np

""" Update these variables to point to your ffmpeg and convert binaries
If you installed ffmpeg using conda or installed both softwares in
standard ways on your computer, no changes should be required."""
_FFMPEG_BINARY = 'ffmpeg'
_MAGICK_BINARY = 'magick'

"""update this to the directory and file-name beginning for the graphics files"""
_DEFAULT_GRAPHICS_DIR = os.path.join('../..', 'data')
_DEFAULT_GRAPHICS_NAME = 'dv'
_DEFAULT_IMG_FORMAT = 'png'
_DEFAULT_MOVIE_FORMAT = 'mp4'  # alternatives: mp4, gif


class Graphics:
    """Provides graphics support for RandVis."""

    def __init__(self, img_dir=None, img_name=None, img_fmt=None, y_max=None):
        """
        Parameters
        --------

        img_dir: str
            directory for image files; no images if None

        img_name: str
            beginning of name for image files
        img_fmt: str
            image file format suffix
        """
        try:
            plt.rcParams.update({
                "text.usetex": True})
        except:
            pass

        if img_name is None:
            img_name = _DEFAULT_GRAPHICS_NAME

        if img_dir is not None:
            self._img_base = os.path.join(img_dir, img_name)
        else:
            self._img_base = None

        self._img_fmt = img_fmt if img_fmt is not None else _DEFAULT_IMG_FORMAT

        self._img_ctr = 0
        self._img_step = 1

        # the following will be initialized by _setup_graphics
        self._fig = None
        self._map_ax = None
        self._img_axis = None
        self._animal_counts_ax = None
        self._herbivore_line = None
        self._carnivore_line = None
        self._year_counter = None
        self._herbivore_dist_ax = None
        self._carnivore_dist_ax = None
        self._age_ax = None
        self._weight_ax = None
        self._fitness_ax = None
        self._log_file = None

        self._mid_ax = None
        self._phase_line = None

        self.y_max = y_max

    def make_movie(self, movie_fmt=None):
        """
        Creates MPEG4 movie from visualization images saved.
        The movie is stored as img_base + movie_fmt.

        Parameters
        --------
        movie_fmt: str
            format of the movie output.


        #note:Requires ffmpeg for MP4 and magick for GIF
        """

        if self._img_base is None:
            raise RuntimeError("No filename defined.")

        if movie_fmt is None:
            movie_fmt = _DEFAULT_MOVIE_FORMAT

        if movie_fmt == 'mp4':
            try:
                # Parameters chosen according to http://trac.ffmpeg.org/wiki/Encode/H.264,
                # section "Compatibility"
                subprocess.check_call([_FFMPEG_BINARY,
                                       '-i', '{}_%05d.png'.format(self._img_base),
                                       '-y',
                                       '-profile:v', 'baseline',
                                       '-level', '3.0',
                                       '-pix_fmt', 'yuv420p',
                                       '{}.{}'.format(self._img_base, movie_fmt)])
            except subprocess.CalledProcessError as err:
                raise RuntimeError('ERROR: ffmpeg failed with: {}'.format(err))
        elif movie_fmt == 'gif':
            try:
                subprocess.check_call([_MAGICK_BINARY,
                                       '-delay', '1',
                                       '-loop', '0',
                                       '{}_*.png'.format(self._img_base),
                                       '{}.{}'.format(self._img_base, movie_fmt)])
            except subprocess.CalledProcessError as err:
                raise RuntimeError('ERROR: convert failed with: {}'.format(err))
        else:
            raise ValueError('Unknown movie format: ' + movie_fmt)

    def setup(self, final_step, img_step, island_map, log_file=None):
        """
        Prepare graphics.

        Call this before calling :meth:`update()` for the first time after
        the final time step has changed.

        Parameters
        --------
        final_step: int
            last time step to be visualised (upper limit of x-axis)
        img_step: int
            interval between saving image to file
        island_map: str
            string of island
        log_file
        """

        self._img_step = img_step

        # create new figure window
        if self._fig is None:
            self._fig = plt.figure(figsize=(8, 8))
            # self._fig.tight_layout()

        # Add left subplot for images created with imshow().
        # We cannot create the actual ImageAxis object before we know
        # the size of the image, so we delay its creation.
        if self._map_ax is None:
            self._map_ax = self._fig.add_subplot(3, 3, 2)
            self._map_ax.set_title("Island")
        self._setup_map(island_map)

        if self._year_counter is None:
            self._year_counter = self._fig.add_subplot(3, 3, 5)
            self._year_counter.axis("off")
            self._annotation = None

        # Add right subplot for line graph of mean.
        if self._animal_counts_ax is None:
            self._animal_counts_ax = self._fig.add_subplot(3, 3, 3)
            if self.y_max is not None:
                self._animal_counts_ax.set_ylim(0, self.y_max)
            self._animal_counts_ax.set_title("Amount of animals")
        self._animal_counts_ax.set_xlim(0, final_step + 1)

        if self._herbivore_line is None:
            mean_plot = self._animal_counts_ax.plot(np.arange(0, final_step + 1),
                                                    np.full(final_step + 1, np.nan))
            self._herbivore_line = mean_plot[0]
        else:
            x_data, y_data = self._herbivore_line.get_data()
            x_new = np.arange(x_data[-1] + 1, final_step + 1)
            if len(x_new) > 0:
                y_new = np.full(x_new.shape, np.nan)
                self._herbivore_line.set_data(np.hstack((x_data, x_new)),
                                              np.hstack((y_data, y_new)))

        if self._carnivore_line is None:
            mean_plot_1 = self._animal_counts_ax.plot(np.arange(0, final_step + 1),
                                                      np.full(final_step + 1, np.nan), color='red')
            self._carnivore_line = mean_plot_1[0]
        else:
            x_data, y_data = self._carnivore_line.get_data()
            x_new = np.arange(x_data[-1] + 1, final_step + 1)
            if len(x_new) > 0:
                y_new = np.full(x_new.shape, np.nan)
                self._carnivore_line.set_data(np.hstack((x_data, x_new)),
                                              np.hstack((y_data, y_new)))

        if self._herbivore_dist_ax is None:
            self._herbivore_dist_ax = self._fig.add_subplot(3, 2, 3)
            self._herbivore_dist_ax.axis("off")
            self._herbivore_dist_ax.set_title("Herbivore distribution")
            self._herb_axis = None

        if self._mid_ax is None:
            self._mid_ax = self._fig.add_subplot(3, 3, 1)
            self._mid_ax.set_title("Carnivore vs Herbivore count")

        if self._phase_line is None:
            plot = self._mid_ax.plot(np.full(final_step + 1, 0),
                                     np.full(final_step + 1, np.nan))
            self._phase_line = plot[0]
        else:
            x_data, y_data = self._phase_line.get_data()
            shape = np.arange(len(y_data), final_step + 1)
            if len(shape) > 0:
                x_new = np.full(shape.shape, np.nan)
                y_new = np.full(shape.shape, np.nan)
                self._phase_line.set_data(np.hstack((x_data, x_new)),
                                          np.hstack((y_data, y_new)))

        if self._carnivore_dist_ax is None:
            self._carnivore_dist_ax = self._fig.add_subplot(3, 2, 4)
            self._carnivore_dist_ax.axis("off")
            self._carnivore_dist_ax.set_title("Carnivore distribution")
            self._carn_axis = None

        if self._age_ax is None:
            self._age_ax = self._fig.add_subplot(3, 3, 7)
            self._age_ax.set_title("Age")

        if self._weight_ax is None:
            self._weight_ax = self._fig.add_subplot(3, 3, 8)
            self._weight_ax.set_title("Weight")

        if self._fitness_ax is None:
            self._fitness_ax = self._fig.add_subplot(3, 3, 9)
            self._fitness_ax.set_title("Fitness")

        if log_file is not None and self._log_file is None:
            self._log_file = f"{log_file}"

            with open(self._log_file, "a") as file:
                file.write("Year,Herbivore count,Carnivore count\n")

        # set the spacing between subplots
        plt.subplots_adjust(left=0.1,
                            bottom=0.1,
                            right=0.9,
                            top=0.9,
                            wspace=0.4,
                            hspace=0.5)

    def _setup_map(self, island_map):
        """
        Setup the island to 2D image.
        Parameters
        ----------
        island_map: str
            strings of island cell values
        """
        #                   R    G    B
        rgb_value = {'W': (0.0, 0.0, 1.0),  # blue
                     'L': (0.0, 0.6, 0.0),  # dark green
                     'H': (0.5, 1.0, 0.5),  # light green
                     'D': (1.0, 1.0, 0.5)}  # light yellow

        map_rgb = [[rgb_value[column] for column in row]
                   for row in island_map.splitlines()]

        self._map_ax.imshow(map_rgb)

        self._map_ax.set_xticks([nr - 0.5 for nr in range(1, len(map_rgb[0]) + 1, 5)])
        self._map_ax.set_xticklabels([nr for nr in range(1, len(map_rgb[0]) + 1, 5)])
        self._map_ax.set_yticks([nr - 0.5 for nr in range(1, len(map_rgb) + 1, 4)])
        self._map_ax.set_yticklabels([nr for nr in range(1, len(map_rgb) + 1, 4)])

    def update(self, year, animal_distribution, cmax, animal_counts, animal_vitals, hist_specs):
        """
        Updates graphics with current data and save to file if necessary.
        Parameters
        ----------
        year: int
            year
        animal_distribution: dict
            dictionary containing numpy.arrays
        cmax: dict
             no. of herbivore and carnivore.
        animal_counts: int
             animal count
        animal_vitals : _getitem_
        hist_specs
        """
        self._update_year(year)
        self._update_color_mesh(animal_distribution, cmax)
        self._update_animal_count_graph(year, animal_counts)
        self._update_histograms(animal_vitals, hist_specs)
        self._write_to_log_file(year, animal_counts)
        self._fig.canvas.flush_events()  # ensure every thing is drawn
        plt.pause(1e-6)  # pause required to pass control to GUI

        self._save_graphics(year)

    def _update_year(self, year):
        if self._annotation is not None:
            self._annotation.set_text(f"year: {year}")
        else:
            self._annotation = self._year_counter.annotate(f"year: {year}", (0.4, 0.5))  # x = 0.365

    def _update_color_mesh(self, distribution, cmax):
        """
        Updates color meshes that display the distribution of herbivores and carnivores.
        Parameters
        ----------
        distribution
        cmax: dict
            maps species to maximum value on the colorbars
        """
        herb_distribution, carn_distribution = distribution["Herbivore"], distribution["Carnivore"]

        if cmax is not None:
            max_herb, max_carn = cmax["Herbivore"], cmax["Carnivore"]
        else:
            max_herb, max_carn = 200, 100

        if self._herb_axis is not None:
            self._herb_axis.set_data(herb_distribution)
        else:
            self._herb_axis = self._herbivore_dist_ax.imshow(herb_distribution,
                                                             interpolation='nearest',
                                                             vmin=-0.25, vmax=0.25)
            plt.colorbar(self._herb_axis, ax=self._herbivore_dist_ax,
                         orientation='vertical', location="left")
            self._herb_axis.set_clim(0, max_herb)

        if self._carn_axis is not None:
            self._carn_axis.set_data(carn_distribution)
        else:
            self._carn_axis = self._carnivore_dist_ax.imshow(carn_distribution,
                                                             interpolation='nearest',
                                                             vmin=-0.25, vmax=0.25)
            plt.colorbar(self._carn_axis, ax=self._carnivore_dist_ax,
                         orientation='vertical', location='right')
            # if cmax is not None:
            self._carn_axis.set_clim(0, max_carn)

    def _update_animal_count_graph(self, year, animal_counts):
        """
        Updates the animal counts on graph.
        Parameters
        ----------
        year: int
            Current time step
        animal_counts: int
            Animal count
        """
        herbivore, carnivore = animal_counts["Herbivore"], animal_counts["Carnivore"]

        y_data_herb = self._herbivore_line.get_ydata()
        y_data_herb[year] = herbivore
        self._herbivore_line.set_ydata(y_data_herb)

        y_data_carn = self._carnivore_line.get_ydata()
        y_data_carn[year] = carnivore
        self._carnivore_line.set_ydata(y_data_carn)

        y_data_herb[0] = 0
        y_data_carn[0] = 0

        if self.y_max is None:
            self._animal_counts_ax.set_ylim(1, 1.1 * max(max(y_data_herb) + 1,
                                                         1.1 * max(y_data_carn) + 1))

        self._mid_ax.set_xlim(0, 1.1 * max(y_data_herb))

        self._mid_ax.set_ylim(0, 1.1 * max(y_data_herb) + 1)

        self._phase_line.set_xdata(y_data_herb)
        self._phase_line.set_ydata(y_data_carn)

    def _update_histograms(self, animal_vitals, hist_specs):
        """
        Updates the histogram of the fitness, age, and weight of the animal.
        Parameters
        ----------
        animal_vitals
        hist_specs: hist
            histogram
        """
        if hist_specs is not None:
            age_specs, weight_specs, fitness_specs = hist_specs["age"], \
                                                     hist_specs["weight"], \
                                                     hist_specs["fitness"]
        else:
            age_specs, weight_specs, fitness_specs = {"max": 70, "delta": 2}, \
                                                     {"max": 70, "delta": 2}, \
                                                     {"max": 1, "delta": 0.05}

        ages, weights, fitnesses = animal_vitals["age"],\
                                   animal_vitals["weight"],\
                                   animal_vitals["fitness"]
        self._age_ax.cla()
        self._age_ax.set_title("Age")
        self._age_hist = self._age_ax.hist(ages["Herbivore"],
                                           bins=int(age_specs["max"] / age_specs["delta"]),
                                           range=(0, age_specs["max"]), alpha=0.5)
        self._age_hist = self._age_ax.hist(ages["Carnivore"],
                                           bins=int(age_specs["max"] / age_specs["delta"]),
                                           range=(0, age_specs["max"]), alpha=0.5, color='red')

        self._weight_ax.cla()
        self._weight_ax.set_title("Weight")
        self._weight_hist = self._weight_ax.hist(weights["Herbivore"], bins=int(
            weight_specs["max"] / weight_specs["delta"]),
                                                 range=(0, weight_specs["max"]), alpha=0.5)
        self._weight_hist = self._weight_ax.hist(weights["Carnivore"], bins=int(
            weight_specs["max"] / weight_specs["delta"]),
                                                 range=(0, weight_specs["max"]), alpha=0.5,
                                                 color='red')

        self._fitness_ax.cla()
        self._fitness_ax.set_title("Fitness")
        self._fitness_hist = self._fitness_ax.hist(fitnesses["Herbivore"],
                                                   bins=int(fitness_specs["max"]
                                                            / fitness_specs["delta"]),
                                                   range=(0, fitness_specs["max"]), alpha=0.5)
        self._fitness_hist = self._fitness_ax.hist(fitnesses["Carnivore"],
                                                   bins=int(fitness_specs["max"]
                                                            / fitness_specs["delta"]),
                                                   range=(0, fitness_specs["max"]), alpha=0.5,
                                                   color='red')

    def _write_to_log_file(self, year, animal_counts):
        """Writes each year's animal counts to a given file"""
        if self._log_file is not None:
            with open(self._log_file, "a") as file:
                file.write(f"{year},{animal_counts['Herbivore']},{animal_counts['Carnivore']}\n")

    def _save_graphics(self, step):
        """Saves graphics to file if file name given."""

        if self._img_base is None or step % self._img_step != 0:
            return

        plt.savefig('{base}_{num:05d}.{type}'.format(base=self._img_base,
                                                     num=self._img_ctr,
                                                     type=self._img_fmt))
        self._img_ctr += 1
