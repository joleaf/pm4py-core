'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''

import numpy as np
from scipy.optimize import linprog, OptimizeResult
from typing import Optional, Dict, Any, List
from enum import Enum
from pm4py.util import exec_utils


class Parameters:
    INTEGRALITY = "integrality"


def apply(c: list, Aub: np.ndarray, bub: np.matrix, Aeq: np.matrix, beq: np.matrix,
          parameters: Optional[Dict[Any, Any]] = None) -> OptimizeResult:
    if parameters is None:
        parameters = {}

    integrality = exec_utils.get_param_value(Parameters.INTEGRALITY, parameters, None)
    sol = linprog(c, A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=beq, method="revised simplex", integrality=integrality)
    return sol


def get_prim_obj_from_sol(sol: OptimizeResult, parameters: Optional[Dict[Any, Any]] = None) -> int:
    return round(sol.fun)


def get_points_from_sol(sol: OptimizeResult, parameters: Optional[Dict[Any, Any]] = None) -> List[int]:
    return [round(y) for y in sol.x]
