"""
run.py : Run a simulation for the quad rotor model of a drone or design
a quad rotor drone based on the model and its parameters.
"""

import sys
import argparse
from pathlib import Path
from drone.studies.simulation import (

)
from drone.studies.design import (

)
from drone.utils import loaders
from drone.utils import plotters
from drone.utils import timers
from drone.utils import printers

def get_config_path() -> Path:
    """
    Get the path to the configuration file.
    """

    if len(sys.argv) < 2:
        print("Please provide a path to the configuration file.")
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Process Simulation or Parameter Estimation."
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to a configuration file."
    )

    return Path(parser.parse_args().config)

def get_config() -> dict:
    """
    Parse command line arguments.
    """

    config_path = get_config_path()

    config = loaders.load_data(
        config_path=config_path
    )

    return config

def get_simulation_study(
    config:dict
):
    """
    Get the simulation study.
    """

    workflow = config['workflow']

    if workflow == 'simulation':
        log_path = loaders.get_log_file_path(
            file_name='simulation.log',
            config=config
        )

        timers.start_logging(
            log_path=log_path,
            purpose='running a simulation'
        )

        warning = True

    else:
        log_path = None
        warning = False

    study = ProcessSimulation(
        config=config,
        warning=warning,
        log_path=log_path
    )

    return study

def run_simulation(
    config:dict
) -> tuple:
    """
    Run a simulation.
    """

    study = get_simulation_study(
        config=config
    )

    return study.__execute__()

def get_estimation_study(
    config:dict
):
    """
    Get the estimation study.
    """

    log_path \
        = loaders.get_log_file_path(
            file_name='parameter_estimation.log',
            config=config
        )

    gradient_based \
        = optimizers.get_gradient_based(
            config=config
        )

    if gradient_based:
        study = GradientBasedParameterEstimation(
            config=config,
            log_path=log_path
        )

    else:
        study = DirectSearchParameterEstimation(
            config=config,
            log_path=log_path
        )

    return study

def run_estimation(
    config:dict
) -> tuple:
    """
    Run a model parameter estimation workflow.
    """

    study = get_estimation_study(
        config=config
    )

    return study.__execute__()

def main(
    config:dict
) -> None:
    """
    Main function for running a simulation.
    """

    workflow = config['workflow']

    if workflow == 'simulation':
        loaders.create_directory_with_config(
            config=config
        )

        results, data, compute_times, flags \
            = run_simulation(
                config=config
            )

        if results is None:
            log_path = loaders.get_log_file_path(
                file_name='simulation.log',
                config=config
            )

            msg = "Simulation failed. Please check the log file. \n"

            printers.no_print_but_log(
                log_path=log_path,
                msg=msg
            )

            msg = ""

            for key, value in flags.items():
                issue = f"{key}: {value}"
                msg = msg + " " + issue + " \n"

            printers.no_print_but_log(
                log_path=log_path,
                msg=msg
            )

            sys.exit(1)

        plotters.plot_simulation_results(
            results=results,
            data=data,
            compute_times=compute_times,
            config=config
        )

    elif workflow == 'estimation':
        loaders.create_directory_with_config(
            config=config
        )

        results, compute_times \
            = run_estimation(
                config=config
            )

        plotters.plot_and_save_estimation_results(
            results=results,
            compute_times=compute_times,
            config=config
        )

    else:
        print("Please select a workflow: simulation or estimation.")
        sys.exit(1)

if __name__ == "__main__":

    config_data = get_config()

    main(
        config=config_data
    )
