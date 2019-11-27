# -----------------------------------------------------------------------------
#
#  Copyright (c) 2019, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
# -----------------------------------------------------------------------------
"""
Tests for the Range trait with value type int.
"""

import unittest
import warnings

from traits.api import (
    Any,
    BaseRange,
    Either,
    Float,
    HasTraits,
    Instance,
    Int,
    Range,
    TraitError,
)
from traits.testing.optional_dependencies import numpy, requires_numpy


class InheritsFromInt(int):
    """
    Object that's integer-like by virtue of inheriting from int.
    """

    pass


class IntLike(object):
    """
    Object that's integer-like by virtue of providing an __index__ method.
    """

    def __init__(self, value):
        self._value = value

    def __index__(self):
        return self._value


class BadIntLike(object):
    """
    Object whose __index__ method raises something other than TypeError.
    """

    def __index__(self):
        raise ZeroDivisionError("bogus error")


def ModelFactory(name, RangeFactory):
    """
    Helper function to create various similar model classes.

    Parameters
    ----------
    name : str
        Name to give the created class.
    RangeFactory : callable(*range_args, **range_kwargs) -> TraitType
        Callable with the same signature as Range; this will be used
        to create the model traits.

    Returns
    -------
    HasTraits subclass
        Subclass containing various Range-like traits, for testing.

    """

    class ModelWithRanges(HasTraits):
        """
        Model containing various Range-like traits.
        """

        # Simple integer range trait.
        percentage = RangeFactory(0, 100)

        # Traits that exercise the various possiblities for inclusion
        # or exclusion of the endpoints.
        open_closed = RangeFactory(0, 100, exclude_low=True)

        closed_open = RangeFactory(0, 100, exclude_high=True)

        open = RangeFactory(0, 100, exclude_low=True, exclude_high=True)

        closed = RangeFactory(0, 100)

        unbounded = RangeFactory(value_type=Int)

        unbounded_with_default = RangeFactory(value=50)

        # Traits for one-sided intervals
        steam_temperature = RangeFactory(low=100)

        ice_temperature = RangeFactory(high=0)

        # Trait with non-integer low and high values
        room_temperature = RangeFactory(low=IntLike(10), high=IntLike(30))

    ModelWithRanges.__name__ = name

    return ModelWithRanges


class DynamicRangesModel(HasTraits):

    # Dynamic low and high
    dynamic_int = Range(low="low_bound", high="high_bound", value_type=Int)

    dynamic_float = Range(low="low_bound", high="high_bound", value_type=Float)

    # Dynamic high value
    dynamic_high = Range(low=0, high="high_bound")

    # Dynamic low value
    dynamic_low = Range(low="low_bound", high=100)

    # Dynamic high, referring to a trait that doesn't exist.
    dynamic_high_nonexistent = Range(low=0, high="nonexistent")

    # Dynamic default
    dynamic_default = Range(low=0, high=100, value="default")

    # Dynamic everything (value type Int)
    full_dynamic_int = Range(
        low="low_bound", high="high_bound", value="default", value_type=Int,
    )

    # Dynamic everything (value type Float)
    full_dynamic_float = Range(
        low="low_bound", high="high_bound", value="default", value_type=Float,
    )

    # Trait providing the upper bound of a dynamic range.
    high_bound = Any(100)

    # Trait providing the lower bound of a dynamic range.
    low_bound = Any(0)

    # Trait providing the default value for a dynamic range.
    default = Any(50)


class Impossible(object):
    """
    Type that never gets instantiated.
    """

    def __init__(self):
        raise TypeError("Cannot instantiate this class")


# A trait type that has a fast validator but doesn't accept any values.
impossible = Instance(Impossible, allow_none=False)


def RangeCompound(*args, **kwargs):
    """
    Compound trait including a Range.
    """
    return Either(impossible, Range(*args, **kwargs))


def BaseRangeCompound(*args, **kwargs):
    """
    Compound trait including a BaseRange.
    """
    return Either(impossible, BaseRange(*args, **kwargs))


ModelWithRange = ModelFactory("ModelWithRange", RangeFactory=Range)

ModelWithBaseRange = ModelFactory("ModelWithBaseRange", RangeFactory=BaseRange)

ModelWithRangeCompound = ModelFactory(
    "ModelWithRangeCompound", RangeFactory=RangeCompound
)

ModelWithBaseRangeCompound = ModelFactory(
    "ModelWithBaseRangeCompound", RangeFactory=BaseRangeCompound,
)


class CommonRangeTests(object):
    def test_accepts_int(self):
        self.model.percentage = 35
        self.assertIs(type(self.model.percentage), int)
        self.assertEqual(self.model.percentage, 35)
        with self.assertRaises(TraitError):
            self.model.percentage = -1
        with self.assertRaises(TraitError):
            self.model.percentage = 101

    def test_accepts_bool(self):
        self.model.percentage = False
        self.assertIs(type(self.model.percentage), int)
        self.assertEqual(self.model.percentage, 0)

        self.model.percentage = True
        self.assertIs(type(self.model.percentage), int)
        self.assertEqual(self.model.percentage, 1)

    def test_rejects_bad_types(self):
        # A selection of things that don't count as integer-like.
        non_integers = [
            "not a number",
            "\N{GREEK CAPITAL LETTER SIGMA}",
            b"not a number",
            "3.5",
            "3",
            3 + 4j,
            0j,
            [1],
            (1,),
            [1.2],
            (1.2,),
            0.0,
            -27.8,
            35.0,
            None,
        ]

        for non_integer in non_integers:
            self.model.percentage = 73
            with self.assertRaises(TraitError):
                self.model.percentage = non_integer
            self.assertEqual(self.model.percentage, 73)

    @requires_numpy
    def test_accepts_numpy_types(self):
        numpy_values = [
            numpy.uint8(25),
            numpy.uint16(25),
            numpy.uint32(25),
            numpy.uint64(25),
            numpy.int8(25),
            numpy.int16(25),
            numpy.int32(25),
            numpy.int64(25),
        ]
        for numpy_value in numpy_values:
            self.model.percentage = numpy_value
            self.assertIs(type(self.model.percentage), int)
            self.assertEqual(self.model.percentage, 25)

    @requires_numpy
    def test_rejects_numpy_types(self):
        numpy_values = [
            numpy.float16(25),
            numpy.float32(25),
            numpy.float64(25),
        ]
        for numpy_value in numpy_values:
            self.model.percentage = 88
            with self.assertRaises(TraitError):
                self.model.percentage = numpy_value
            self.assertEqual(self.model.percentage, 88)

    def test_accepts_int_subclass(self):
        self.model.percentage = InheritsFromInt(44)
        self.assertIs(type(self.model.percentage), int)
        self.assertEqual(self.model.percentage, 44)
        with self.assertRaises(TraitError):
            self.model.percentage = InheritsFromInt(-1)
        with self.assertRaises(TraitError):
            self.model.percentage = InheritsFromInt(101)

    def test_accepts_int_like(self):
        self.model.percentage = IntLike(35)
        self.assertIs(type(self.model.percentage), int)
        self.assertEqual(self.model.percentage, 35)
        with self.assertRaises(TraitError):
            self.model.percentage = IntLike(-1)
        with self.assertRaises(TraitError):
            self.model.percentage = IntLike(101)

    def test_bad_int_like(self):
        # Check that the exception is propagated as expected.
        with self.assertRaises(ZeroDivisionError):
            self.model.percentage = BadIntLike()

    def test_endpoints(self):
        # point within the interior of the range
        self.model.open = self.model.closed = 50
        self.model.open_closed = self.model.closed_open = 50
        self.assertEqual(self.model.open, 50)
        self.assertEqual(self.model.closed, 50)
        self.assertEqual(self.model.open_closed, 50)
        self.assertEqual(self.model.closed_open, 50)

        # low endpoint
        self.model.closed = self.model.closed_open = 0
        self.assertEqual(self.model.closed, 0)
        self.assertEqual(self.model.closed_open, 0)
        with self.assertRaises(TraitError):
            self.model.open = 0
        with self.assertRaises(TraitError):
            self.model.open_closed = 0

        # high endpoint
        self.model.closed = self.model.open_closed = 100
        self.assertEqual(self.model.closed, 100)
        self.assertEqual(self.model.open_closed, 100)
        with self.assertRaises(TraitError):
            self.model.open = 100
        with self.assertRaises(TraitError):
            self.model.closed_open = 100

    def test_half_infinite(self):
        ice_temperatures = [-273, -100, -1]
        water_temperatures = [1, 50, 99]
        steam_temperatures = [101, 1000, 10 ** 100, 10 ** 1000]

        for temperature in steam_temperatures:
            self.model.steam_temperature = temperature
            self.assertEqual(self.model.steam_temperature, temperature)

        for temperature in ice_temperatures + water_temperatures:
            self.model.steam_temperature = 1729
            with self.assertRaises(TraitError):
                self.model.steam_temperature = temperature
            self.assertEqual(self.model.steam_temperature, 1729)

        for temperature in ice_temperatures:
            self.model.ice_temperature = temperature
            self.assertEqual(self.model.ice_temperature, temperature)

        for temperature in water_temperatures + steam_temperatures:
            self.model.ice_temperature = -1729
            with self.assertRaises(TraitError):
                self.model.ice_temperature = temperature
            self.assertEqual(self.model.ice_temperature, -1729)

    def test_integer_like_limits(self):
        self.model.room_temperature = 15
        self.assertIsExactInt(self.model.room_temperature, 15)
        self.model.room_temperature = IntLike(25)
        self.assertIsExactInt(self.model.room_temperature, 25)

        self.model.room_temperature = 27
        with self.assertRaises(TraitError):
            # Bad type.
            self.model.room_temperature = 13.0
        self.assertIsExactInt(self.model.room_temperature, 27)

        # Out-of-range values
        self.model.room_temperature = 27

        with self.assertRaises(TraitError):
            self.model.room_temperature = 5
        self.assertIsExactInt(self.model.room_temperature, 27)

        with self.assertRaises(TraitError):
            self.model.room_temperature = 33
        self.assertIsExactInt(self.model.room_temperature, 27)

    def test_bad_limits(self):
        non_integers = [
            3 + 4j,
            0j,
            [1],
            (1,),
            [1.2],
            (1.2,),
        ]

        for non_integer in non_integers:
            with self.assertRaises(TraitError):
                Range(low=0, high=non_integer)
            with self.assertRaises(TraitError):
                Range(low=non_integer, high=100)

    def test_unbounded_range_with_default(self):
        # For compound traits, default is None.
        if self.compound:
            self.assertIsNone(self.model.unbounded_with_default)
            return

        self.assertIsExactInt(self.model.unbounded_with_default, 50)

    def test_unbounded_range_no_default(self):
        # For compound traits, default is None.
        if self.compound:
            self.assertIsNone(self.model.unbounded)
            return

        self.assertIsExactInt(self.model.unbounded, 0)

    def assertIsExactInt(self, actual, expected):
        self.assertIs(type(actual), int)
        self.assertEqual(actual, expected)


class TestIntRange(CommonRangeTests, unittest.TestCase):
    def setUp(self):
        self.range_factory = Range
        self.model = ModelWithRange()
        self.compound = False


class TestIntBaseRange(CommonRangeTests, unittest.TestCase):
    def setUp(self):
        self.range_factory = BaseRange
        self.model = ModelWithBaseRange()
        self.compound = False


class TestIntRangeCompound(CommonRangeTests, unittest.TestCase):
    def setUp(self):
        self.range_factory = RangeCompound
        self.model = ModelWithRangeCompound()
        self.compound = True


class TestIntBaseRangeCompound(CommonRangeTests, unittest.TestCase):
    def setUp(self):
        self.range_factory = BaseRangeCompound
        self.model = ModelWithBaseRangeCompound()
        self.compound = True


def as_integer(value):
    """
    Integer conversion matching the behaviour of the Int trait.
    """
    return Int().validate(None, "dummy", value)


class TestRangeTypeInference(unittest.TestCase):
    def test_static_case(self):
        float_range_traits = [
            Range(low=0.0, high=10.0, value=5.0),
            Range(low=0.0, high=10.0, value=5),
            Range(low=0.0, high=10.0, value=None),
            Range(low=0.0, high=10, value=5.0),
            Range(low=0.0, high=10, value=5),
            Range(low=0.0, high=10, value=None),
            Range(low=0.0, high=None, value=5.0),
            Range(low=0.0, high=None, value=5),
            Range(low=0.0, high=None, value=None),
            Range(low=0, high=10.0, value=5.0),
            Range(low=0, high=10.0, value=5),
            Range(low=0, high=10.0, value=None),
            Range(low=0, high=10, value=5.0),
            Range(low=0, high=None, value=5.0),
            Range(low=None, high=10.0, value=5.0),
            Range(low=None, high=10.0, value=5),
            Range(low=None, high=10.0, value=None),
            Range(low=None, high=10, value=5.0),
            Range(low=None, high=None, value=5.0),
        ]

        int_range_traits = [
            Range(low=0, high=10, value=5),
            Range(low=0, high=10, value=None),
            Range(low=0, high=None, value=5),
            Range(low=0, high=None, value=None),
            Range(low=None, high=10, value=5),
            Range(low=None, high=10, value=None),
            Range(low=None, high=None, value=5),
        ]

        # XXX Not ideal, since it's testing implementation rather
        # than behaviour. Better way? Embed the trait in a model class?
        for range_trait in float_range_traits:
            self.assertIs(range_trait._vtype, float)

        for range_trait in int_range_traits:
            self.assertIs(range_trait._vtype, int)

    def test_bad_value_type(self):
        with self.assertRaises(TraitError):
            Range(value_type=int)
        with self.assertRaises(TraitError):
            Range(value_type=str)

    def test_deprecated_case(self):
        # Case where no type can be inferred, and we drop
        # back to Float.
        with warnings.catch_warnings(record=True) as warn_msgs:
            warnings.simplefilter("always", DeprecationWarning)
            range_traits = [
                Range(low=None, high=None, value=None),
                Range(low="low", high=None, value=None),
                Range(low="low", high="high", value=None),
                Range(low=None, high="high", value=None),
            ]

        for range_trait in range_traits:
            self.assertIs(range_trait._vtype, float)

        # Expect one warning for each of our range traits.
        self.assertEqual(len(warn_msgs), len(range_traits))

        for warn_msg in warn_msgs:
            message = str(warn_msg.message)
            self.assertIn("Unable to infer the value type", message)


class TestDynamicRange(unittest.TestCase):
    def setUp(self):
        self.model = DynamicRangesModel()

    def test_dynamic_high(self):
        self.check_trait_set(dynamic_high=50)
        self.check_trait_set(dynamic_high=IntLike(50))
        self.check_trait_set(dynamic_high=InheritsFromInt(50))
        self.check_trait_set(dynamic_high=100)

        self.check_trait_error(dynamic_high=120)
        self.check_trait_error(dynamic_high=-20)

        self.model.high_bound = 200
        self.check_trait_set(dynamic_high=120)

        # Setting a new high that puts the value out of bounds
        # resets the value.
        self.model.high_bound = 60
        self.assertEqual(self.model.dynamic_high, 60)

    def test_dynamic_high_default(self):
        self.assertEqual(self.model.dynamic_high, 0)

    def test_dynamic_high_none(self):
        self.model.high_bound = None
        self.check_trait_set(dynamic_high=50)
        self.check_trait_set(dynamic_high=500)
        self.check_trait_set(dynamic_high=10 ** 1000)

        self.check_trait_error(dynamic_high=-20)

    def test_dynamic_high_float(self):
        # Retrieving the value involves comparing with the low
        # and high, which can raise if those have the wrong type.
        self.model.high_bound = 100.0
        with self.assertRaises(TraitError):
            self.model.dynamic_high

    def test_dynamic_high_int_like(self):
        self.model.high_bound = IntLike(60)
        self.check_trait_set(dynamic_high=60)
        self.check_trait_error(dynamic_high=61)

    def test_dynamic_high_nonexistent(self):
        with self.assertRaises(AttributeError):
            self.model.dynamic_high_nonexistent

    def test_dynamic_low_int(self):
        self.model.low_bound = 20
        self.assertEqual(self.model.dynamic_low, 20)

    def test_dynamic_low_int_like(self):
        self.model.low_bound = IntLike(20)
        self.assertEqual(self.model.dynamic_low, 20)
        self.check_trait_set(dynamic_low=25)
        self.check_trait_error(dynamic_low=19)

    def test_dynamic_low_float(self):
        self.model.low_bound = 20.0
        with self.assertRaises(TraitError):
            self.model.dynamic_low

    def test_dynamic_default(self):
        self.model.default = 27
        self.assertIs(type(self.model.dynamic_default), int)
        self.assertEqual(self.model.dynamic_default, 27)

    def test_bad_dynamic_default(self):
        self.model.default = 27.0
        with self.assertRaises(TraitError):
            self.model.dynamic_default

    def test_dynamic_no_default(self):
        self.model.low_bound = None
        self.model.high_bound = None
        self.assertIs(type(self.model.dynamic_int), int)
        self.assertEqual(self.model.dynamic_int, 0)

        self.assertIs(type(self.model.dynamic_float), float)
        self.assertEqual(self.model.dynamic_float, 0.0)

    def test_dynamic_default_all_none(self):
        self.model.low_bound = None
        self.model.high_bound = None
        self.model.default = None

        self.assertIs(type(self.model.full_dynamic_int), int)
        self.assertEqual(self.model.full_dynamic_int, 0)

        self.assertIs(type(self.model.full_dynamic_float), float)
        self.assertEqual(self.model.full_dynamic_float, 0.0)

    def check_trait_set(self, **kwargs):
        # Check the result of setting an integer range trait.
        for name, value in kwargs.items():
            setattr(self.model, name, value)
            retrieved_value = getattr(self.model, name)
            self.assertIs(type(retrieved_value), int)
            self.assertEqual(retrieved_value, as_integer(value))

    def check_trait_error(self, **kwargs):
        for name, value in kwargs.items():
            original_value = getattr(self.model, name)
            with self.assertRaises(TraitError):
                setattr(self.model, name, value)
            # Check that the value is unchanged.
            self.assertEqual(getattr(self.model, name), original_value)