"""Basic command line functions for interacting with a roboclaw motor
controller

Works with python 2.7, but doesn't work with python 3 because the roboclaw
library is old
"""

import logging

import click

from roboclaw import Roboclaw

logger = logging.getLogger(__name__)

form = "%(asctime)s %(levelname)-8s %(funcName)-15s %(message)s"
logging.basicConfig(format=form,
                    datefmt="%H:%M:%S")

@click.group()
def cli():
    """This function is necessary for the click CLI to work."""

@cli.command()
@click.option('--device', type=str, default="/dev/serial0", 
    help='The serial device used to connect to the motor controller')
@click.option('--baud_rate', type=int, default=115200, 
    help='The baud rate for the serial connection to the motor controller')
@click.option('--address', type=int, default=128, 
    help='The address of the motor controller')
@click.option('--address', type=int, default=128, 
    help='The address of the motor controller')
@click.option('--verbosity', '-v',
    default='INFO', 
    type=click.Choice([
        'CRITICAL',
        'ERROR',
        'WARNING',
        'INFO',
        'DEBUG',
        'NOTSET']),
    help='Logging verbosity level.')
def go(
        device,
        baud_rate,
        address,
        verbosity
    ):
    # logger.info('hey')

    # set verbosity. Do it jankily because life is too short.
    eval("logger.setLevel(logging.{})".format(verbosity)) #pylint: disable=eval-used

    rc = Roboclaw(device, baud_rate)
    rc.Open()

    # initialize connection status to successful
    logger.info("Attempting to talk to motor controller '{}'".format(address))
    version_response = rc.ReadVersion(address)
    connected = bool(version_response[0])
    if not connected:
        logger.info("Unable to connect to roboclaw at '{}'".format(address))
    else:
        logger.info("Roboclaw version for address '{}': '{}'".format(address, version_response[1]))

if __name__ == '__main__':
    cli()