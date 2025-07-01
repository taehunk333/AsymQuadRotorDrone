"""
This module contains the functions for handling times.
"""

import time
from datetime import datetime
import numpy as np
from pypetal.utils import loaders

def get_time() -> float:
    """
    Get the current time.
    """

    return time.time()

def get_readable_time(
    timestamp:float
) -> str:
    """
    Get the readable time.
    """

    readable_time \
        = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    return readable_time

def start_logging(
    log_path:str,
    purpose:str
) -> float:
    """
    This method starts the logging for a given purpose.
    """

    start_time = get_time()
    start_time_str = get_readable_time(
        timestamp=start_time
    )

    loaders.create_log_file(
        start_time=start_time_str,
        log_file_path=log_path
    )

    loaders.add_entry_to_log(
        log_file_path=log_path,
        entry=f'{start_time_str}: Starting ' + purpose + '.\n'
    )

    return start_time

def geometric_mean_rows(
    data: np.ndarray
) -> tuple:
    """
    Calculates the geometric mean of each row in a 2D array,
    ignoring zeros.
    """

    geometric_means = []
    max_val = -np.inf

    for row in data:
        row_no_zeros = row[row != 0]

        if row_no_zeros.size > 0:
            geometric_means.append(np.exp(np.mean(np.log(row_no_zeros))))
            max_val = max(np.append(row_no_zeros, max_val))

        else:
            geometric_means.append(np.nan)

    return np.array(geometric_means), max_val

def update_parameter_estimation_log_direct_search(
    start_time: float,
    log_path: str,
    n_gen: int,
    solution_set: list,
    duration: float
) -> float:
    """
    This method updates the log file with a given start_time, and 
    returns an updated start_time.
    """

    geometric_means, max_val \
        = geometric_mean_rows(
            data=np.array(solution_set)
        )
    min_geometric_mean \
        = np.nanmin(geometric_means)
    max_geometric_mean \
        = np.nanmax(geometric_means)

    curr_time = get_time()
    curr_time_str = get_readable_time(
        timestamp=curr_time
    )

    elapsed_time = curr_time - start_time

    log_info = f'{curr_time_str}: \n' \
        + "Generation number: " + str(n_gen) + ". \n" \
        + "Generation clock time: " + str(elapsed_time) + " seconds. \n" \
        + "Overall clock time: " + str(duration) + " seconds.\n" \
        + "Min. geometric mean: " + str(min_geometric_mean) + ".\n" \
        + "Max. geometric mean: " + str(max_geometric_mean) + ".\n" \
        + "Max. signal value: " + str(max_val) + ".\n"

    loaders.add_entry_to_log(
        log_file_path=log_path,
        entry=log_info
    )

    return curr_time

def get_duration(
    start_time: float,
) -> float:
    """
    This method returns the duration from a known start time.
    """

    return get_time() - start_time
