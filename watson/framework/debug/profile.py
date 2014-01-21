# -*- coding: utf-8 -*-

import cProfile
import pstats


def execute(func, sort_order='cumulative', max_results=20, *args, **kwargs):
    """Profiles a specific function and returns a dict of relevant timings.

    Args:
        sort_order (string): The order by which to sort
        max_results (int): The maximum number of results to display

    Example:

    .. code-block:: python

        def func_to_profile():
            # do something

        response, stats = profile.execute(func_to_profile)
    """
    profiler = cProfile.Profile()
    response = profiler.runcall(func, *args, **kwargs)
    p = pstats.Stats(profiler)
    p.sort_stats(sort_order)
    f = '{0:.3f}'
    stats = {
        'function_calls': p.total_calls,
        'primative_calls': p.prim_calls,
        'total_time': f.format(p.total_tt),
        'times': []
    }
    list = p.fcn_list
    if list:
        for func in list[:max_results]:
            cc, nc, tt, ct, callers = p.stats[func]
            c = str(nc)
            if nc != cc:
                c = c + '/' + str(cc)
            stats['times'].append({
                'number_calls': c,
                'total_time': f.format(tt),
                'per_call': f.format(tt / nc),
                'cumulative_time': f.format(ct),
                'per_call2': f.format(ct / cc),
                'function_name': func[2],
                'line': func[1],
                'file': func[0]
            })
    return response, stats
