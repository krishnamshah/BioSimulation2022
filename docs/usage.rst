Usage
==================================

Setting up your BioSim Project on GitLab
-----------------------------------------
You need to setup virtual environment with the *inf200_conda_env.yml* from
<https://gitlab.com/nmbu.no/emner/inf200/h2021/inf200-course-materials/-/tree/main/technical>

1. Clone the repository to your system.
2. Setup the virtual environment. Activate the virtual environment

.. note::
   Make sure that you have activated the right environment.

How do I run it?
----------------------------------

Simulation can be run by executing *check_sim.py* located inside reference_example folder.

.. code-block:: python

    python -m check_sim.py

Testing
----------------------------------
Unittest test cases are supported by pytest. Writing pytest test cases is where pytest really shines. Test cases in
pytest are a set of functions in a Python file that begin with the letter *test_*.
Tests can be run using pytest. And all the test will run automatically.

Tox is an application that automates testing in multiple environments.

.. code-block:: python

    tox

Just run the above code from the home directory of the project. All the tests are inside the folder *tests*.

