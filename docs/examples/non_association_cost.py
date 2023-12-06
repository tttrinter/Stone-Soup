"""
Using OneToOneAssociator with an Association Threshold
===============================================
Nada
"""

import datetime
import plotly

from stonesoup.dataassociator.general import OneToOneAssociator, GreedyAssociator
from stonesoup.measures.multi import StateSequenceMeasure, MeanMeasure
from stonesoup.measures.base import BaseMeasure, SetComparisonMeasure
from stonesoup.dataassociator.tracktotrack import OneToOneTrackAssociator
from stonesoup.measures import Euclidean
from stonesoup.plotter import Plotterly
from stonesoup.types.state import State
from stonesoup.types.track import Track


# %%
# Helper Functions
def print_results(assocs, unassocs_a, unassocs_b, measure):
    assoc_dict = {association.objects[0]: association.objects[1]
                  for association in assocs}

    print("Associations:\t\t\t", assoc_dict)
    print("Unassocaited objects from a:\t", unassocs_a)
    print("Unassocaited objects from b:\t", unassocs_b)

    total = sum(measure(*an_assoc.objects) for an_assoc in assocs.associations)
    print(f"Total Measure:\t\t\t {total}")


def break_down_association_measure(associations, measure):
    for association in associations:
        print(f"{list(association.objects)} : {measure(*association.objects)}")


class NumericDifference(BaseMeasure):
    def __call__(self, item1: float, item2: float) -> float:
        """ Returns absolute difference between two floats"""
        if item1 == item2:
            return float('nan')
        else:
            return abs(item1-item2)


# %%
# Using OneToOneAssociator with an Association Threshold
# -------------------------------------------------------
# The :class:`~.OneToOneAssociator uses :func:`~scipy.optimize.linear_sum_assignment` which
# provides the optimal score when pairing all objects. When an association threshold is applied not
# every pairing is possible, :func:`~scipy.optimize.linear_sum_assignment` alone is no longer
# suitable for the problem. This is demonstrated in the following example:

# %%
# Scenario 1
# ^^^^^^^^^^
# The goal is to pair numbers together, minimising the difference in the pairs. The numbers are
# (0, 4, 9) and (3, 8, 50).
numbers_a = (0, 4, 9)
numbers_b = (3, 8, 50)
measure = NumericDifference()

associator = OneToOneAssociator(measure=NumericDifference(),
                                maximise_measure=False)

# %%
# No Threshold
# """"""""""""
associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# Every number is associated to another number. A break-down of the total measure shows that `9`
# and `50` pair contribute the majority of the total measure.

break_down_association_measure(associations, measure=NumericDifference())

# %%
# Only Post-Processing
# """"""""""""""""""""
# It is decided that the distance `9` and `50` is
# too large. So an association threshold of `10` should be applied.
# With only post-processing, the pair 9 and 50 would be removed. However this isn’t optimal.
# The total cost would be lower if 3 was associated with 4 and 8 was associated with 9.

association_threshold = 10

# %%
# This non-optimal behaviour can be seen if you set the ``non_association_cost=None``. This
# is not recommended and is only kept for legacy reasons.

associator = OneToOneAssociator(measure=measure,
                                maximise_measure=False,
                                association_threshold=association_threshold,
                                non_association_cost=None)

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# The :func:`~scipy.optimize.linear_sum_assignment` function needs pre-processing to be suitable
# for a scenario with an association threshold. The :class:`~.OneToOneAssociator` will alter the
# distance matrix input into the :func:`~scipy.optimize.linear_sum_assignment` function. Any value
# that is equal or beyond the :attr:`~.GeneralAssociator.association_threshold` is set equal to the
# :attr:`~.OneToOneAssociator.non_association_cost`.

# %%
#

associator = OneToOneAssociator(measure=measure,
                                maximise_measure=False,
                                association_threshold=association_threshold,
                                non_association_cost=float('inf'))

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# **Note**: although infinity is used as the `non_association_cost`, `linear_sum_assignment` cannot
# cope with very large numbers because very large number + 1 == very large number.
very_large_number = 1e20
print(f"Does very large number + 1 == very large number: "
      f"{very_large_number + 1 == very_large_number}.")
# Instead `non_association_cost` is reduced internally by the `OneToOneAssociator` before being
# passed to the `linear_sum_assignment` function. This reduced value is ±
# :attr:`~.OneToOneAssociator.measure_fail_magnitude`
# to See
# :meth:`OneToOneAssociator.individual_weighting` function for detail.

# %%
# The default behaviour of the OneToOneAssociator is to set non_association_cost=``nan``.

associator = OneToOneAssociator(measure=measure,
                                maximise_measure=False,
                                association_threshold=association_threshold)

print(f"Default value of the OneToOneAssociator is: {associator.non_association_cost}")

# %%
#

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# From the


# %%
# Fail with sys.float_info.max
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

import numpy as np
import sys
from scipy.optimize import linear_sum_assignment

no = sys.float_info.max
distance_matrix = (np.array([[-no, -no, -no, -no],
                             [no, no, no, no],
                             [-no, -no, -no, -no],
                             [16, 16, 16, 16]]))

try:
    row_ind, col_ind = linear_sum_assignment(distance_matrix, True)
    print([distance_matrix[i, j] for i, j in zip(row_ind, col_ind)])
except ValueError as e:
    print(e)


no = 1e10
distance_matrix = (np.array([[-no, -no, -no, -no],
                             [no, no, no, no],
                             [-no, -no, -no, -no],
                             [16, 16, 16, 16]]))

try:
    row_ind, col_ind = linear_sum_assignment(distance_matrix, True)
    print([distance_matrix[i, j] for i, j in zip(row_ind, col_ind)])
except ValueError as e:
    print(e)

























# %%
# Old
# -------------------------------------------------------


# %%
# The :class:`~.OneToOneAssociator` uses :func:`~scipy.optimize.linear_sum_assignment` which is
# optimal when there is no association requirement. It is no longer optimal when some associations
# may be restricted. This section demonstrates how the
# :attr:`~.GeneralAssociator.association_threshold` and
# :attr:`~.OneToOneAssociator.non_association_cost` attributes effect the output of the
# :class:`~.OneToOneAssociator`.

# %%
# Options for :attr:`~.OneToOneAssociator.non_association_cost`:
#
#  a. ``nan`` - If the goal is to maximise the number of associations
#  b. ``None`` - If you want to simply cut off associations that don’t reach the threshold use
#  c. ``0`` - To maximise the total measure
#  d. :attr:`~.GeneralAssociator.association_threshold` ± <small_number> - To minimise the total
#     measure

# %%
# To avoid :func:`~scipy.optimize.linear_sum_assignment` choosing associations that won't pass the
# threshold, a high :attr:`~.OneToOneAssociator.non_association_cost` will be used instead of the
# value of the measure function.

# %%
# **Note**: although infinity is used as the `non_association_cost`, `linear_sum_assignment` cannot
# cope with very large numbers (because very large number + 1 == very large number). Very large
# `non_association_cost` are reduced internally by the `OneToOneAssociator` class before being
# passed to the `linear_sum_assignment` function. See
# :meth:`OneToOneAssociator.individual_weighting` function for detail.

# %%
# This function print the results of the association output.
def print_results(assocs, unassocs_a, unassocs_b, measure):
    assoc_dict = {association.objects[0]: association.objects[1]
                  for association in assocs}

    # print(assoc_dict, "\t", unassocs_a, "\t", unassocs_b)

    total = sum(measure(*an_assoc.objects) for an_assoc in assocs.associations)
    percent_assoc = len(assocs.associations)*2 / \
                    (len(assocs.associations)*2 + len(unassocs_a) + len(unassocs_b))
    print(f"Total Measure={total} ({percent_assoc*100})", end="\t")


class SquareNumericDifference(BaseMeasure):

    def __call__(self, item1: float, item2: float) -> float:
        """ Returns absolute difference between two floats"""
        return (item1-item2)**2


# %%
# The measure is the ``NumericDifference`` (the absolute difference between the numbers).
class NumericDifference(BaseMeasure):
    def __call__(self, item1: float, item2: float) -> float:
        """ Returns absolute difference between two floats"""
        if item1 == item2:
            return float('nan')
        else:
            return abs(item1-item2)


class SquareNumeric(BaseMeasure):
    def __call__(self, item1: float, item2: float) -> float:
        if item1 == item2:
            return float('nan')
        return item1*item2


def associate_and_print(associator, numbers_a, numbers_b, measure):
    associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
    print_results(associations, unassociated_a, unassociated_b, measure=measure)


def do_all(measure, maximise_measure, association_threshold, numbers_a, numbers_b, name):
    if maximise_measure:
        print("\nMaximise")
    else:
        print("\nMinimise")

    print(f"{name}\tNo Threshold", end="\t")
    associator = OneToOneAssociator(measure=measure,
                                    maximise_measure=maximise_measure,
                                    association_threshold=None)
    associate_and_print(associator, numbers_a, numbers_b, measure)
    print(f"\t{name}\tNo Threshold")

    print(f"{name}\tOption A - nan", end="\t")
    associator = OneToOneAssociator(measure=measure,
                                    maximise_measure=maximise_measure,
                                    association_threshold=association_threshold,
                                    non_association_cost=float('nan'))
    associate_and_print(associator, numbers_a, numbers_b, measure)
    print(f"{name}\tOption A - nan")

    print(f"{name}\tOption B - None", end="\t")
    associator = OneToOneAssociator(measure=measure,
                                    maximise_measure=maximise_measure,
                                    association_threshold=association_threshold,
                                    non_association_cost=None)
    associate_and_print(associator, numbers_a, numbers_b, measure)
    print(f"{name}\tOption B - None")

    print(f"{name}\tOption C - 0", end="\t")
    associator = OneToOneAssociator(measure=measure,
                                    maximise_measure=maximise_measure,
                                    association_threshold=association_threshold,
                                    non_association_cost=0)
    associate_and_print(associator, numbers_a, numbers_b, measure)
    print(f"{name}\tOption C - 0")

    print(f"{name}\tOption D - Threshold", end="\t")
    if maximise_measure:
        non_association_cost = association_threshold - 0.01
    else:
        non_association_cost = association_threshold + 0.01
    associator = OneToOneAssociator(measure=measure,
                                    maximise_measure=maximise_measure,
                                    association_threshold=association_threshold,
                                    non_association_cost=non_association_cost)
    associate_and_print(associator, numbers_a, numbers_b, measure)
    print(f"{name}\tOption D - Threshold")


# %%
# Scenario 1
# ^^^^^^^^^^
do_all(measure=NumericDifference(),
       maximise_measure=False,
       association_threshold=10,
       numbers_a=(0, 4, 9),
       numbers_b=(3, 8, 50),
       name="1")

# %%
# Scenario 2
# ^^^^^^^^^^
do_all(measure=SquareNumeric(),
       maximise_measure=True,
       association_threshold=5,
       numbers_a=(1, 2, 3, 5),
       numbers_b=(1, 2, 4, 7),
       name="2")

# %%
# Scenario 3
# ^^^^^^^^^^
do_all(measure=SquareNumeric(),
       maximise_measure=False,
       association_threshold=6.95,
       numbers_a=(1, 2, 3, 6, 10),
       numbers_b=(1.1, 1.2, 1.3, 2.2, 7),
       name="3")

# %%
# Scenario 4
# ^^^^^^^^^^
do_all(measure=SquareNumericDifference(),
       maximise_measure=True,
       association_threshold=5,
       numbers_a=(0, 2, 5, 7),
       numbers_b=(6, 7, 8),
       name="4")

# %%
# Scenario 5
# ^^^^^^^^^^
do_all(measure=SquareNumeric(),
       maximise_measure=False,
       association_threshold=20,
       numbers_a=(2, 3, 5, 8),
       numbers_b=(1, 4, 7, 10),
       name="5")

# %%
# Scenario 6
# ^^^^^^^^^^
do_all(measure=SquareNumeric(),
       maximise_measure=False,
       association_threshold=21,
       numbers_a=(2, 3, 5, 8),
       numbers_b=(1, 4, 7, 10),
       name="6")

# %%
# Scenario 7
# ^^^^^^^^^^
do_all(measure=SquareNumeric(),
       maximise_measure=True,
       association_threshold=21,
       numbers_a=(2, 3, 5, 8),
       numbers_b=(1, 4, 7, 10),
       name="7")

raise NotImplementedError


# %%
# No Association Threshold
# """""""""""""""""""""""""""""""""""""
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=None)

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# Every number is associated to another number. The distance `9` and `50` is too large. So an
# association threshold of `10` is applied.

# %%
# Option B
# """""""""""""""""""""
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=association_threshold,
                                non_association_cost=None)

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# These results are not optimal. The total cost would be lower if `3` was associated with `4` and
# `8` was associated with `9`.

# %%
# Option A
# """""""""""""""""""""
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=association_threshold,
                                non_association_cost=float('nan'))

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# Option C
# """""""""""""""""""""
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=association_threshold,
                                non_association_cost=0)

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# Option D
# """""""""""""""""""""
if maximise_measure:
    non_association_cost = association_threshold + 0.01
else:
    non_association_cost = association_threshold - 0.01
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=association_threshold,
                                non_association_cost=non_association_cost)

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# Scenario 3
# ^^^^^^^^^^
#
numbers_a = (1, 2, 3, 6, 10)
numbers_b = (1.1, 1.2, 1.3, 2.2, 7)
association_threshold = 6.95
measure = SquareNumeric()
maximise_measure = False


# %%
# No Association Threshold
# """""""""""""""""""""""""""""""""""""
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=None)

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# Every number is associated to another number. The distance `9` and `50` is too large. So an
# association threshold of `10` is applied.

# %%
# Option B
# """""""""""""""""""""
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=association_threshold,
                                non_association_cost=None)

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# These results are not optimal. The total cost would be lower if `3` was associated with `4` and
# `8` was associated with `9`.

# %%
# Option A
# """""""""""""""""""""
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=association_threshold,
                                non_association_cost=float('nan'))

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# Option C
# """""""""""""""""""""
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=association_threshold,
                                non_association_cost=0)

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# Option D
# """""""""""""""""""""
if maximise_measure:
    non_association_cost = association_threshold - 0.01
else:
    non_association_cost = association_threshold + 0.01
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=association_threshold,
                                non_association_cost=non_association_cost)

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# Scenario 4
# ^^^^^^^^^^
#
numbers_a = (0, 2, 5, 7)
numbers_b = (6, 7, 8)
association_threshold = 5
measure = SquareNumericDifference()
maximise_measure = True


# %%
# No Association Threshold
# """""""""""""""""""""""""""""""""""""
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=None)

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# Every number is associated to another number. The distance `9` and `50` is too large. So an
# association threshold of `10` is applied.

# %%
# Option B
# """""""""""""""""""""
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=association_threshold,
                                non_association_cost=None)

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# These results are not optimal. The total cost would be lower if `3` was associated with `4` and
# `8` was associated with `9`.

# %%
# Option A
# """""""""""""""""""""
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=association_threshold,
                                non_association_cost=float('nan'))

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# Option C
# """""""""""""""""""""
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=association_threshold,
                                non_association_cost=0)

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# Option D
# """""""""""""""""""""
if maximise_measure:
    non_association_cost = association_threshold - 0.01
else:
    non_association_cost = association_threshold + 0.01
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=association_threshold,
                                non_association_cost=non_association_cost)

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)


# %%
# Scenario 5
# ^^^^^^^^^^
#
numbers_a = (2, 3, 5, 8)
numbers_b = (1, 4, 7, 10)
association_threshold = 20
measure = SquareNumeric()
maximise_measure = False


# %%
# No Association Threshold
# """""""""""""""""""""""""""""""""""""
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=None)

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# Every number is associated to another number. The distance `9` and `50` is too large. So an
# association threshold of `10` is applied.

# %%
# Option B
# """""""""""""""""""""
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=association_threshold,
                                non_association_cost=None)

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# These results are not optimal. The total cost would be lower if `3` was associated with `4` and
# `8` was associated with `9`.

# %%
# Option A
# """""""""""""""""""""
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=association_threshold,
                                non_association_cost=float('nan'))

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# Option C
# """""""""""""""""""""
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=association_threshold,
                                non_association_cost=0)

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# Option D
# """""""""""""""""""""
if maximise_measure:
    non_association_cost = association_threshold - 0.01
else:
    non_association_cost = association_threshold + 0.01
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=association_threshold,
                                non_association_cost=non_association_cost)

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)


# %%
# Scenario 6
# ^^^^^^^^^^
#
numbers_a = (2, 3, 5, 8)
numbers_b = (1, 4, 7, 10)
association_threshold = 21
measure = SquareNumeric()
maximise_measure = False


# %%
# No Association Threshold
# """""""""""""""""""""""""""""""""""""
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=None)

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# Every number is associated to another number. The distance `9` and `50` is too large. So an
# association threshold of `10` is applied.

# %%
# Option B
# """""""""""""""""""""
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=association_threshold,
                                non_association_cost=None)

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# These results are not optimal. The total cost would be lower if `3` was associated with `4` and
# `8` was associated with `9`.

# %%
# Option A
# """""""""""""""""""""
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=association_threshold,
                                non_association_cost=float('nan'))

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# Option C
# """""""""""""""""""""
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=association_threshold,
                                non_association_cost=0)

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)

# %%
# Option D
# """""""""""""""""""""
if maximise_measure:
    non_association_cost = association_threshold - 0.01
else:
    non_association_cost = association_threshold + 0.01
associator = OneToOneAssociator(measure=measure,
                                maximise_measure=maximise_measure,
                                association_threshold=association_threshold,
                                non_association_cost=non_association_cost)

associations, unassociated_a, unassociated_b = associator.associate(numbers_a, numbers_b)
print_results(associations, unassociated_a, unassociated_b, measure=measure)