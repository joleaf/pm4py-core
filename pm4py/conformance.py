__doc__ = """
Conformance checking is a techniques to compare a process model with an event log of the same process. The goal is to check if the event log conforms to the model, and, vice versa.

* Procedural models
    * Conformance Checking diagnostics
        * `Token-Based Replay (TBR)`_
        * `Alignments`_
        * `Footprints`_
    * Evaluation
        * Fitness
            * `Fitness TBR`_
            * `Fitness Alignments`_
            * `Fitness Footprints`_
        * Precision
            * `Precision TBR`_
            * `Precision Alignments`_
            * `Precision Footprints`_
* Declarative models
    * `Conformance diagnostics using the Log Skeleton`_
* Time-infused models
    * `Conformance checking using the Temporal Profile`_

.. _Token-Based Replay (TBR): pm4py.html#pm4py.conformance.conformance_diagnostics_token_based_replay
.. _Alignments: pm4py.html#pm4py.conformance.conformance_diagnostics_alignments
.. _Footprints: pm4py.html#pm4py.conformance.conformance_diagnostics_footprints
.. _Fitness TBR: pm4py.html#pm4py.conformance.fitness_token_based_replay
.. _Fitness Alignments: pm4py.html#pm4py.conformance.fitness_alignments
.. _Fitness Footprints: pm4py.html#pm4py.conformance.fitness_footprints
.. _Precision TBR: pm4py.html#pm4py.conformance.precision_token_based_replay
.. _Precision Alignments: pm4py.html#pm4py.conformance.precision_alignments
.. _Precision Footprints: pm4py.html#pm4py.conformance.precision_footprints
.. _Conformance diagnostics using the Log Skeleton: pm4py.html#pm4py.conformance.conformance_log_skeleton
.. _Conformance checking using the Temporal Profile: pm4py.html#pm4py.conformance.conformance_temporal_profile

"""

import warnings
from typing import List, Dict, Any, Union, Optional, Tuple, Set

from pm4py.objects.log.obj import EventLog, Trace, Event, EventStream
from pm4py.objects.petri_net.obj import PetriNet, Marking
from collections import Counter
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util import xes_constants
from pm4py.utils import get_properties, __event_log_deprecation_warning
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns
import pandas as pd
import deprecation


def conformance_diagnostics_token_based_replay(log: Union[EventLog, pd.DataFrame], petri_net: PetriNet, initial_marking: Marking,
                                               final_marking: Marking, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> List[Dict[str, Any]]:
    """
    Apply token-based replay for conformance checking analysis.
    The methods return the full token-based-replay diagnostics.

    Parameters
    --------------
    log
        Event log
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    --------------
    replay_results
        A list of replay results for each trace of the log (in the same order as the traces in the event log)
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
    return token_replay.apply(log, petri_net, initial_marking, final_marking, parameters=properties)


def conformance_diagnostics_alignments(log: Union[EventLog, pd.DataFrame], *args, multi_processing: bool = False, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> List[Dict[str, Any]]:
    """
    Apply the alignments algorithm between a log and a process model.
    The methods return the full alignment diagnostics.

    Parameters
    -------------
    log
        Event log
    args
        Specification of the process model
    multi_processing
        Boolean value that enables the multiprocessing (default: False)
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    -------------
    aligned_traces
        A list of alignments for each trace of the log (in the same order as the traces in the event log)
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if len(args) == 3:
        if type(args[0]) is PetriNet:
            # Petri net alignments
            from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
            if multi_processing:
                return alignments.apply_multiprocessing(log, args[0], args[1], args[2], parameters=properties)
            else:
                return alignments.apply(log, args[0], args[1], args[2], parameters=properties)
        elif type(args[0]) is dict or type(args[0]) is Counter:
            # DFG alignments
            from pm4py.algo.conformance.alignments.dfg import algorithm as dfg_alignment
            return dfg_alignment.apply(log, args[0], args[1], args[2], parameters=properties)
    elif len(args) == 1:
        if type(args[0]) is ProcessTree:
            # process tree alignments
            from pm4py.algo.conformance.alignments.process_tree.variants import search_graph_pt
            if multi_processing:
                return search_graph_pt.apply_multiprocessing(log, args[0], parameters=properties)
            else:
                return search_graph_pt.apply(log, args[0], parameters=properties)
    # try to convert to Petri net
    import pm4py
    from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
    net, im, fm = pm4py.convert_to_petri_net(*args)
    if multi_processing:
        return alignments.apply_multiprocessing(log, net, im, fm, parameters=properties)
    else:
        return alignments.apply(log, net, im, fm, parameters=properties)


def fitness_token_based_replay(log: Union[EventLog, pd.DataFrame], petri_net: PetriNet, initial_marking: Marking, final_marking: Marking, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> \
        Dict[
            str, float]:
    """
    Calculates the fitness using token-based replay.
    The fitness is calculated on a log-based level.

    Parameters
    ---------------
    log
        Event log
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    ---------------
    fitness_dictionary
        dictionary describing average fitness (key: average_trace_fitness) and the percentage of fitting traces (key: percentage_of_fitting_traces)
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.evaluation.replay_fitness import algorithm as replay_fitness
    return replay_fitness.apply(log, petri_net, initial_marking, final_marking,
                                variant=replay_fitness.Variants.TOKEN_BASED, parameters=properties)


def fitness_alignments(log: Union[EventLog, pd.DataFrame], petri_net: PetriNet, initial_marking: Marking, final_marking: Marking, multi_processing: bool = False, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> \
        Dict[str, float]:
    """
    Calculates the fitness using alignments

    Parameters
    --------------
    log
        Event log
    petri_net
        Petri net object
    initial_marking
        Initial marking
    final_marking
        Final marking
    multi_processing
        Boolean value that enables the multiprocessing (default: False)
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    ---------------
    fitness_dictionary
        dictionary describing average fitness (key: average_trace_fitness) and the percentage of fitting traces (key: percentage_of_fitting_traces)
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.evaluation.replay_fitness import algorithm as replay_fitness
    parameters = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters["multiprocessing"] = multi_processing
    return replay_fitness.apply(log, petri_net, initial_marking, final_marking,
                                variant=replay_fitness.Variants.ALIGNMENT_BASED, parameters=parameters)


def precision_token_based_replay(log: Union[EventLog, pd.DataFrame], petri_net: PetriNet, initial_marking: Marking,
                                 final_marking: Marking, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> float:
    """
    Calculates the precision precision using token-based replay

    Parameters
    --------------
    log
        Event log
    petri_net
        Petri net object
    initial_marking
        Initial marking
    final_marking
        Final marking
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    --------------
    precision
        float representing the precision value
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
    return precision_evaluator.apply(log, petri_net, initial_marking, final_marking,
                                     variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN, parameters=properties)


def precision_alignments(log: Union[EventLog, pd.DataFrame], petri_net: PetriNet, initial_marking: Marking,
                         final_marking: Marking, multi_processing: bool = False, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> float:
    """
    Calculates the precision of the model w.r.t. the event log using alignments

    Parameters
    --------------
    log
        Event log
    petri_net
        Petri net object
    initial_marking
        Initial marking
    final_marking
        Final marking
    multi_processing
        Boolean value that enables the multiprocessing (default: False)
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    --------------
    precision
        float representing the precision value
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
    parameters = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters["multiprocessing"] = multi_processing
    return precision_evaluator.apply(log, petri_net, initial_marking, final_marking,
                                     variant=precision_evaluator.Variants.ALIGN_ETCONFORMANCE,
                                     parameters=parameters)

@deprecation.deprecated("2.3.0", "3.0.0", "conformance checking using footprints will not be exposed in a future release")
def __convert_to_fp(*args) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Internal method to convert the provided event log / process model argument
    to footprints (using footprints discovery)

    Parameters
    ----------------
    args
        Event log / process model

    Returns
    ---------------
    fp
        Footprints
    """
    import pm4py
    while type(args) is tuple:
        if len(args) == 1:
            args = args[0]
        else:
            fp = pm4py.discover_footprints(*args)
            return fp
    if type(args) is list or type(args) is dict:
        return args
    fp = pm4py.discover_footprints(args)
    return fp


@deprecation.deprecated("2.3.0", "3.0.0", "conformance checking using footprints will not be exposed in a future release")
def conformance_diagnostics_footprints(*args) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Provide conformance checking diagnostics using footprints

    Parameters
    ----------------
    args
        Provided argument:
        - The first argument is supposed to be an event log (or the footprints discovered from the event log)
        - The other arguments are supposed to be the process model (or the footprints discovered from the process model)

    Returns
    ----------------
    fps
        Footprints of the event log / process model
    """
    fp1 = __convert_to_fp(args[0])
    fp2 = __convert_to_fp(args[1:])
    from pm4py.algo.conformance.footprints import algorithm as footprints_conformance
    if isinstance(fp1, list):
        return footprints_conformance.apply(fp1, fp2, variant=footprints_conformance.Variants.TRACE_EXTENSIVE)
    else:
        return footprints_conformance.apply(fp1, fp2, variant=footprints_conformance.Variants.LOG_EXTENSIVE)


@deprecation.deprecated("2.3.0", "3.0.0", "conformance checking using footprints will not be exposed in a future release")
def fitness_footprints(*args) -> Dict[str, float]:
    """
    Calculates fitness using footprints

    Parameters
    ----------------
    args
        Provided argument:
        - The first argument is supposed to be an event log (or the footprints discovered from the event log)
        - The other arguments are supposed to be the process model (or the footprints discovered from the process model)

    Returns
    ----------------
    fitness_dict
        A dictionary containing two keys:
        - perc_fit_traces => percentage of fit traces (over the log)
        - log_fitness => the fitness value over the log
    """
    fp_conf = conformance_diagnostics_footprints(*args)
    fp1 = __convert_to_fp(args[0])
    fp2 = __convert_to_fp(args[1:])
    from pm4py.algo.conformance.footprints.util import evaluation
    return evaluation.fp_fitness(fp1, fp2, fp_conf)


@deprecation.deprecated("2.3.0", "3.0.0", "conformance checking using footprints will not be exposed in a future release")
def precision_footprints(*args) -> float:
    """
    Calculates precision using footprints

    Parameters
    ----------------
    args
        Provided argument:
        - The first argument is supposed to be an event log (or the footprints discovered from the event log)
        - The other arguments are supposed to be the process model (or the footprints discovered from the process model)

    Returns
    ----------------
    precision
        The precision of the process model (as a number between 0 and 1)
    """
    fp1 = __convert_to_fp(args[0])
    fp2 = __convert_to_fp(args[1:])
    from pm4py.algo.conformance.footprints.util import evaluation
    return evaluation.fp_precision(fp1, fp2)


@deprecation.deprecated("2.3.0", "3.0.0", details="this method will be removed in a future release.")
def __check_is_fit_process_tree(trace, tree):
    """
    Check if a trace object is fit against a process tree model

    Parameters
    -----------------
    trace
        Trace
    tree
        Process tree

    Returns
    -----------------
    is_fit
        Boolean value (True if the trace fits; False if the trace does not)
    """
    __event_log_deprecation_warning(trace)

    from pm4py.discovery import discover_footprints
    log = EventLog()
    log.append(trace)
    fp_tree = discover_footprints(tree)
    fp_log = discover_footprints(log)
    fp_conf_res = conformance_diagnostics_footprints(fp_log, fp_tree)[0]
    # CHECK 1) if footprints already say is not fit, then return False
    # (if they say True, it might be a false positive)
    if not fp_conf_res["is_footprints_fit"]:
        return False
    else:
        from pm4py.convert import convert_to_petri_net
        net, im, fm = convert_to_petri_net(tree)
        tbr_conf_res = conformance_diagnostics_token_based_replay(log, net, im, fm)[0]
        # CHECK 2) if TBR says that is fit, then return True
        # (if they say False, it might be a false negative)
        if tbr_conf_res["trace_is_fit"]:
            return True
        else:
            # CHECK 3) alignments definitely say if the trace is fit or not if the previous methods fail
            align_conf_res = conformance_diagnostics_alignments(log, tree)[0]
            return align_conf_res["fitness"] == 1.0


@deprecation.deprecated("2.3.0", "3.0.0", details="this method will be removed in a future release.")
def __check_is_fit_petri_net(trace, net, im, fm, activity_key=xes_constants.DEFAULT_NAME_KEY):
    """
    Checks if a trace object is fit against Petri net object

    Parameters
    ----------------
    trace
        Trace
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    activity_key
        Activity key (optional)

    Returns
    -----------------
    is_fit
        Boolean value (True if the trace fits; False if the trace does not)
    """
    __event_log_deprecation_warning(trace)

    # avoid checking footprints on Petri net (they are too slow)
    activities_model = set(trans.label for trans in net.transitions if trans.label is not None)
    activities_trace = set([x[activity_key] for x in trace])
    diff = activities_trace.difference(activities_model)
    if diff:
        # CHECK 1) there are activities in the trace that are not in the model
        return False
    else:
        log = EventLog()
        log.append(trace)
        tbr_conf_res = conformance_diagnostics_token_based_replay(log, net, im, fm)[0]
        # CHECK 2) if TBR says that is fit, then return True
        # (if they say False, it might be a false negative)
        if tbr_conf_res["trace_is_fit"]:
            return True
        else:
            # CHECK 3) alignments definitely say if the trace is fit or not if the previous methods fail
            align_conf_res = conformance_diagnostics_alignments(log, net, im, fm)[0]
            return align_conf_res["fitness"] == 1.0


@deprecation.deprecated("2.3.0", "3.0.0", details="this method will be removed in a future release.")
def check_is_fitting(*args, activity_key=xes_constants.DEFAULT_NAME_KEY):
    """
    Checks if a trace object is fit against a process model

    Parameters
    -----------------
    trace
        Trace object (trace / variant)
    model
        Model (process tree, Petri net, BPMN, ...)
    activity_key
        Activity key (optional)

    Returns
    -----------------
    is_fit
        Boolean value (True if the trace fits; False if the trace does not)
    """
    from pm4py.util import variants_util
    from pm4py.convert import convert_to_process_tree, convert_to_petri_net

    trace = args[0]
    model = args[1:]

    try:
        model = convert_to_process_tree(*model)
    except:
        # the model cannot be expressed as a process tree, let's say if at least can be expressed as a Petri net
        model = convert_to_petri_net(*model)

    if not isinstance(trace, Trace):
        activities = variants_util.get_activities_from_variant(trace)
        trace = Trace()
        for act in activities:
            trace.append(Event({activity_key: act}))

    if isinstance(model, ProcessTree):
        return __check_is_fit_process_tree(trace, model)
    elif isinstance(model, tuple) and isinstance(model[0], PetriNet):
        return __check_is_fit_petri_net(trace, model[0], model[1], model[2], activity_key=activity_key)


def conformance_temporal_profile(log: Union[EventLog, pd.DataFrame], temporal_profile: Dict[Tuple[str, str], Tuple[float, float]], zeta: float = 1.0, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> List[List[Tuple[float, float, float, float]]]:
    """
    Performs conformance checking on the provided log with the provided temporal profile.
    The result is a list of time-based deviations for every case.

    Parameters
    -----------------
    log
        Log object
    temporal_profile
        Temporal profile. E.g., if the log has two cases:

        A (timestamp: 1980-01)   B (timestamp: 1980-03)    C (timestamp: 1980-06)
        A (timestamp: 1990-01)   B (timestamp: 1990-02)    D (timestamp: 1990-03)

        The temporal profile will contain:
        {('A', 'B'): (1.5 months, 0.5 months), ('A', 'C'): (5 months, 0), ('A', 'D'): (2 months, 0)}
    zeta
        Number of standard deviations allowed from the average. E.g. zeta=1 allows every timestamp between
        AVERAGE-STDEV and AVERAGE+STDEV

    Returns
    ----------------
    temp_conf_results
        Results of conformance based on the temporal profile.
        This is a list of deviations for every case.

        E.g. if the log on top of which the conformance is applied is the following (1 case):

        A (timestamp: 2000-01)    B (timestamp: 2002-01)

        The difference between the timestamps of A and B is two years. If the temporal profile:

        {('A', 'B'): (1.5 months, 0.5 months), ('A', 'C'): (5 months, 0), ('A', 'D'): (2 months, 0)}

        is specified, and zeta is set to 1, then the aforementioned case would be deviating
        (considering the couple of activities ('A', 'B')), because 2 years > 1.5 months + 0.5 months.
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    properties["zeta"] = zeta

    from pm4py.algo.conformance.temporal_profile import algorithm as temporal_profile_conformance
    return temporal_profile_conformance.apply(log, temporal_profile, parameters=properties)


def conformance_log_skeleton(log: Union[EventLog, pd.DataFrame], log_skeleton: Dict[str, Any], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> List[Set[Any]]:
    """
    Performs conformance checking using the log skeleton

    Reference paper:
    Verbeek, H. M. W., and R. Medeiros de Carvalho. "Log skeletons: A classification approach to process discovery." arXiv preprint arXiv:1806.08247 (2018).

    Parameters
    ------------------
    log
        Log object
    log_skeleton
        Log skeleton object, expressed as dictionaries of the six constraints (never_together, always_before ...)
        along with the discovered rules.

        A log skeleton is a declarative model which consists of six different constraints:
        - "directly_follows": specifies for some activities some strict bounds on the activities directly-following. For example,
                            'A should be directly followed by B' and 'B should be directly followed by C'.
        - "always_before": specifies that some activities may be executed only if some other activities are executed somewhen before
                            in the history of the case.
                            For example, 'C should always be preceded by A'
        - "always_after": specifies that some activities should always trigger the execution of some other activities
                            in the future history of the case.
                            For example, 'A should always be followed by C'
        - "equivalence": specifies that a given couple of activities should happen with the same number of occurrences inside
                            a case.
                            For example, 'B and C should always happen the same number of times'.
        - "never_together": specifies that a given couple of activities should never happen together in the history of the case.
                            For example, 'there should be no case containing both C and D'.
        - "activ_occurrences": specifies the allowed number of occurrences per activity:
                            E.g. A is allowed to be executed 1 or 2 times, B is allowed to be executed 1 or 2 or 3 or 4 times.
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    -----------------
    log_skel_conf_res
        List containing, for every case of the log, all the constraints that were violated by such case.
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.conformance.log_skeleton import algorithm as log_skeleton_conformance
    return log_skeleton_conformance.apply(log, log_skeleton, parameters=properties)
