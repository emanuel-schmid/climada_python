"""Calibration Base Classes and Interfaces"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, InitVar
from typing import Callable, Mapping, Optional, Tuple, Union, Any, Dict
from numbers import Number

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, NonlinearConstraint

from climada.hazard import Hazard
from climada.entity import Exposures, ImpactFuncSet
from climada.engine import Impact, ImpactCalc

ConstraintType = Union[LinearConstraint, NonlinearConstraint, Mapping]


@dataclass
class Input:
    """Define the static input for a calibration task

    Attributes
    ----------
    hazard : climada.Hazard
        Hazard object to compute impacts from
    exposure : climada.Exposures
        Exposures object to compute impacts from
    data : pandas.Dataframe
        The data to compare computed impacts to. Index: Event IDs matching the IDs of
        ``hazard``. Columns: Arbitrary columns.
    cost_func : Callable
        Function that takes an ``Impact`` object and a ``pandas.Dataframe`` as argument
        and returns a single number. The optimization algorithm will try to minimize this
        number. See this module for a suggestion of cost functions.
    impact_func_gen : Callable
        Function that takes the parameters as keyword arguments and returns an impact
        function set. This will be called each time the optimization algorithm updates
        the parameters.
    bounds : Mapping (str, {Bounds, tuple(float, float)}), optional
        The bounds for the parameters. Keys: parameter names. Values:
        ``scipy.minimize.Bounds`` instance or tuple of minimum and maximum value.
        Unbounded parameters need not be specified here. See the documentation for
        the selected optimization algorithm on which data types are supported.
    constraints : Constraint or list of Constraint, optional
        One or multiple instances of ``scipy.minimize.LinearConstraint``,
        ``scipy.minimize.NonlinearConstraint``, or a mapping. See the documentation for
        the selected optimization algorithm on which data types are supported.
    impact_calc_kwds : Mapping (str, Any), optional
        Keyword arguments to :py:meth:`climada.engine.impact_calc.ImpactCalc.impact`.
        Defaults to ``{"assign_centroids": False}`` (by default, centroids are assigned
        here via the ``align`` parameter, to avoid assigning them each time the impact is
        calculated).
    align : bool, optional
        Match event IDs from ``hazard`` and ``data``, and assign the centroids from
        ``hazard`` to ``exposure``. Defaults to ``True``.
    """

    hazard: Hazard
    exposure: Exposures
    data: pd.DataFrame
    cost_func: Callable[[Impact, pd.DataFrame], Number]
    impact_func_gen: Callable[..., ImpactFuncSet]
    bounds: Optional[Mapping[str, Union[Bounds, Tuple[Number, Number]]]] = None
    constraints: Optional[Union[ConstraintType, list[ConstraintType]]] = None
    impact_calc_kwds: Mapping[str, Any] = field(
        default_factory=lambda: {"assign_centroids": False}
    )
    align: InitVar[bool] = True

    def __post_init__(self, align):
        """Prepare input data"""
        if align:
            event_diff = np.setdiff1d(self.data.index, self.hazard.event_id)
            if event_diff.size > 0:
                raise RuntimeError(
                    "Event IDs in 'data' do not match event IDs in 'hazard': \n"
                    f"{event_diff}"
                )
            self.hazard = self.hazard.select(event_id=self.data.index.tolist())
            self.exposure.assign_centroids(self.hazard)


@dataclass
class Output:
    """Generic output of a calibration task

    Attributes
    ----------
    params : Mapping (str, Number)
        The optimal parameters
    target : Number
        The target function value for the optimal parameters
    """

    params: Mapping[str, Number]
    target: Number


@dataclass
class Optimizer(ABC):
    """Abstract base class (interface) for an optimization

    This defines the interface for optimizers in CLIMADA. New optimizers can be created
    by deriving from this class and overriding at least the :py:meth:`run` method.

    Attributes
    ----------
    input : Input
        The input object for the optimization task. See :py:class:`Input`.
    """

    input: Input

    def _target_func(self, impact: Impact, data: pd.DataFrame) -> Number:
        """Target function for the optimizer

        The default version of this function simply returns the value of the cost
        function evaluated on the arguments.

        Parameters
        ----------
        impact : climada.engine.Impact
            The impact object returned by the impact calculation.
        data : pandas.DataFrame
            The data used for calibration. See :py:attr:`Input.data`.

        Returns
        -------
        The value of the target function for the optimizer.
        """
        return self.input.cost_func(impact, data)

    def _kwargs_to_impact_func_gen(self, *_, **kwargs) -> Dict[str, Any]:
        """Define how the parameters to :py:meth:`_opt_func` must be transformed

        Optimizers may implement different ways of representing the parameters (e.g.,
        key-value pairs, arrays, etc.). Depending on this representation, the parameters
        must be transformed to match the syntax of the impact function generator used,
        see :py:attr:`Input.impact_func_gen`.

        In this default version, the method simply returns its keyword arguments as
        mapping. Override this method if the optimizer used *does not* represent
        parameters as key-value pairs.

        Parameters
        ----------
        kwargs
            The parameters as key-value pairs.

        Returns
        -------
        The parameters as key-value pairs.
        """
        return kwargs

    def _opt_func(self, *args, **kwargs) -> Number:
        """The optimization function iterated by the optimizer

        This function takes arbitrary arguments from the optimizer, generates a new set
        of impact functions from it, computes the impact, and finally calculates the
        target function value and returns it.

        Parameters
        ----------
        args, kwargs
            Arbitrary arguments from the optimizer, including parameters

        Returns
        -------
        Target function value for the given arguments
        """
        params = self._kwargs_to_impact_func_gen(*args, **kwargs)
        impf_set = self.input.impact_func_gen(**params)
        impact = ImpactCalc(
            exposures=self.input.exposure,
            impfset=impf_set,
            hazard=self.input.hazard,
        ).impact(**self.input.impact_calc_kwds)
        return self._target_func(impact, self.input.data)

    @abstractmethod
    def run(self, **opt_kwargs) -> Output:
        """Execute the optimization"""
