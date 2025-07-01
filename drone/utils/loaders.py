"""
This module contains functions for loading data for running a 
simulation.
"""

from pathlib import Path

import csv
import json
import os
import numpy as np

from pypetal.utils import parsers

def get_log_file_path(
    file_name:str,
    config:dict
) -> str:
    """
    Get the path to the log file.
    """

    log_file_path = os.path.join(
            config['output_directory'],
            file_name
        )

    return log_file_path

def add_entry_to_log(
    log_file_path:str,
    entry:str
) -> None:
    """
    Add an entry to the log file.
    """

    entry = "\n" + entry

    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(
            entry
        )

    return None

def create_log_file(
    start_time:str,
    log_file_path:str
) -> None:
    """
    Create a log file.
    """

    with open(log_file_path, 'w', encoding='utf-8') as log_file:
        log_file.write(
            f"{start_time}: Log file created.\n"
        )

    print(f"\nLog file saved to {log_file_path}\n")

    return None

def create_directory_with_config(
    config:dict
) -> None:
    """
    Create a directory given a configuration file.
    """

    output_directory = config['output_directory']

    if os.path.exists(output_directory):
        os.system(f"rm -rf {output_directory}")

    path = Path(
        output_directory
    )

    path.mkdir(
        parents=True,
        exist_ok=True
    )

    return None

def create_directory_with_path(
    path:str,
    dir_name:str
) -> None:
    """
    Create a directory given a path.
    """

    full_path \
        = os.path.join(
            path,
            dir_name
        )

    os.makedirs(
        full_path,
        exist_ok=True
    )

def load_csv(
    path: Path
) -> np.ndarray:
    """
    Load a CSV file and return it as a NumPy array.
    """

    with open(path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        data = [row for row in reader]

    return np.array(data)

def load_json(
    path: Path
) -> dict:
    """
    Load a JSON file.
    """

    with open(file=path, mode='r', encoding='utf-8') as f:
        data = json.load(
            fp=f
        )

    return data

def write_json(
    path: Path,
    data: dict
) -> None:
    """
    Write a JSON file.
    """

    with open(file=path, mode='w', encoding='utf-8') as f:
        json.dump(
            obj=data,
            fp=f,
            indent=4
        )

def get_no_flow_rates() -> dict:
    """
    Get the zero flow rates in case when there is no extraction or 
    permeation.
    """

    no_flow_rate_dict = {
            "start_time_point":{
                "value": 0,
                "unit": "h"
            },
            "end_time_point":{
                "value": 0,
                "unit": "h"
            },
            "volume":{
                "value": 0.0,
                "unit": "mL"
            },
            "events":{
                "enabled": False,
                "value": np.nan,
                "unit": np.nan
            }
        }

    return no_flow_rate_dict

def load_config(
    config_path: Path
) -> dict:
    """
    Load the configuration file.
    """

    # Check if the configuration file exists.
    try:
        config = load_json(
            path=config_path
        )

    except Exception as exc:
        print('Config file not found.')
        raise FileNotFoundError from exc

    return config

def _get_simulation_parameters(
    config: dict
) -> dict:
    """
    Get the simulation parameters.
    """

    # Check if the path for the simulation parameters is defined.
    try:
        sim_params_path = config['parameters']['path']

        params = load_json(
            path=sim_params_path
        )

        config['parameters'] = params

    except Exception as exc:
        print('Simulation parameters not defined.')
        raise FileNotFoundError from exc

    return config

def _get_initial_conditions_from_json(
    config: dict
) -> dict:
    """
    Get the initial conditions.
    """

    # Check if the path for the initial conditions is defined.
    try:
        init_cond_path = config['initial_conditions']['path']

        init_cond = load_json(
            path=init_cond_path
        )

        config['initial_conditions'] = init_cond['initial_conditions']

    except Exception as exc:
        raise ValueError('Initial conditions must be defined.') from exc

    return config

def _get_feed_schedule(
    config: dict
) -> dict:
    """
    Get the feed schedule.
    """

    # Check if the path for the feed schedule is defined.
    try:
        feed_schedule_path \
            = config['stream_model']['feed_schedule']['path']

        feed_schedule =  load_json(
            path=feed_schedule_path
        )

        config['stream_model']['feed_schedule'] \
            = feed_schedule['feed_schedule']

    except Exception as exc:
        raise ValueError('\nFeed schedule must be defined.\n') from exc

    return config

def _get_extr_schedule(
    config: dict
) -> dict:
    """
    Get the extraction schedule.
    """

    # Check if the path for the extraction schedule is defined.
    try:
        extract_schedule_path \
            = config['stream_model']['extract_schedule']['path']

        extr_schedule = load_json(
            path=extract_schedule_path
        )

        config['stream_model']['extract_schedule'] \
            = extr_schedule['extr_schedule']

    except (KeyError, TypeError) as e:
        message = (f'\nStream Model: Extraction schedule not defined. '
            f'No samples will be extracted.\n{e}')
        print(message)

        config['stream_model']['extract_schedule'] = {}

    return config

def _get_perm_schedule(
    config: dict
) -> dict:
    """
    Get the permeate schedule.
    """

    # Check if the path for the permeate schedule is defined.
    try:
        permeate_schedule_path \
            = config['stream_model']['permeate_schedule']['path']

        perm_schedule = load_json(
            path=permeate_schedule_path
        )

        config['stream_model']['permeate_schedule'] \
            = perm_schedule['perm_schedule']

    except (KeyError, TypeError):
        message = ('\nStream Model: Permeate schedule not defined.\n'
            'No permeation will happen.\n')
        print(message)

        config['stream_model']['permeate_schedule'] = {}

    return config

def _get_natural_constants(
    config: dict
) -> dict:
    """
    Get the natural constants.
    """

    natural_constants \
        = load_config(
        config_path=Path('data/natural_constants.json')
    )

    config['natural_constants'] = natural_constants

    return config

def _get_experimental_data(
    config: dict
) -> dict:
    """
    Get the experimental data.
    """

    try:
        exp_data_path = config['experimental_data_path']

        exp_data = load_json(
            path=exp_data_path
        )

        config['experimental_data'] = exp_data

        del config['experimental_data_path']

    except (KeyError, TypeError) as e:
        print('\nExperimental data not provided. '
            'No experimental data will be plotted.\n'
            f'{e}')

        config['experimental_data'] = None

    return config

def _get_metabolism_data(
    config: dict
) -> dict:
    """
    Get the metabolism data matrix.
    """

    try:
        config = parsers.setup_flux_balance_analysis(
            config=config,
            metabolism_path=config['metabolism_path']
        )

    except (KeyError, TypeError) as e:
        print('\nMetabolism data not provided. '
            'No stoichiometric layer will be simulated.\n'
            f'{e}')

    return config

def load_data(
    config_path: Path
) -> dict:
    """
    Load the data for running a simulation.
    """

    config = load_config(
        config_path=config_path
    )

    if config['workflow'] == 'estimation':
        simulation_config_path \
            = Path(config['simulation_config_path'])

        sim_config = load_data(
            config_path=simulation_config_path
        )

        config['simulation_config'] = sim_config
        config.pop('simulation_config_path')

        historical_parameter_set_path \
            = Path(config['historical_parameter_set_path'])

        historical_parameter_set \
            = load_json(
            path=historical_parameter_set_path
        )

        config['historical_parameter_set'] = historical_parameter_set
        config.pop('historical_parameter_set_path')

        return config

    config = _get_simulation_parameters(
        config=config
    )

    config = _get_natural_constants(
        config=config
    )

    config = _get_initial_conditions_from_json(
        config=config
    )

    config = _get_metabolism_data(
        config=config
    )

    config = _get_feed_schedule(
        config=config
    )

    config = _get_extr_schedule(
        config=config
    )

    config = _get_perm_schedule(
        config=config
    )

    config = _get_experimental_data(
        config=config
    )

    return config
