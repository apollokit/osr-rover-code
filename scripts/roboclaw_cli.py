"""Basic command line functions for interacting with a roboclaw motor
controller

Works with python 2.7, but doesn't work with python 3 because the roboclaw
library is old
"""

import logging
import math

import click

from roboclaw import Roboclaw

logger = logging.getLogger(__name__)

form = "%(asctime)s %(levelname)-8s %(funcName)-15s %(message)s"
logging.basicConfig(format=form,
                    datefmt="%H:%M:%S")

def velocity2qpps(velocity, ticks_per_rev, gear_ratio):
    """
    Convert the given velocity to quadrature pulses per second

    :param velocity: rad/s
    :param ticks_per_rev:
    :param gear_ratio:
    :return: int
    """
    return int(velocity * gear_ratio * ticks_per_rev / (2 * math.pi))

@click.group()
@click.option('--device', type=str, default="/dev/serial0", 
    help='The serial device used to connect to the motor controller')
@click.option('--baud_rate', type=int, default=115200, 
    help='The baud rate for the serial connection to the motor controller')
@click.option('--address', type=int, default=130, 
    help='The address of the motor controller. Default 130 is RC3.')
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
@click.pass_context
def cli(ctx,
        device,
        baud_rate,
        address,
        verbosity
    ):
    """This function is necessary for the click CLI to work."""
    ctx.obj['device'] = device
    ctx.obj['baud_rate'] = baud_rate
    ctx.obj['address'] = address
    # set verbosity. Do it jankily because life is too short.
    eval("logger.setLevel(logging.{})".format(verbosity)) #pylint: disable=eval-used

@cli.command()
@click.pass_context
def liveness(ctx):
    device = ctx.obj['device']
    baud_rate = ctx.obj['baud_rate']
    address = ctx.obj['address']

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
        # roboclaw.ReadEncM1(address)
        # logger.info("Roboclaw version for address '{}': '{}'".format(address, version_response[1]))

@cli.command()
@click.option('--channel', default='M2', 
    type=click.Choice([
        'M1',
        'M2']),
    help='The motor controller channel to use. M2 with address 130 is front'
    ' left motor')
@click.option('--ticks_per_rev', type=int, default=28, 
    help='Ticks per revolution for the motor. Default is for pololu motors')
@click.option('--gear_ratio', type=int, default=26.9, 
    help='Gear ratio of the motor. Default is for pololu motors')
@click.option('--velocity', type=float, default=0, 
    help='Velocity in radians per second to drive the motor at. Default will'
    ' stop the motor')
@click.option('--accel_rate', type=float, default=0.5, 
    help='Acceleration rate for motor')
@click.pass_context
def run_drive_motor(ctx,
        channel,
        ticks_per_rev,
        gear_ratio,
        velocity,
        accel_rate
    ):
    ## DOESN'T WORK! i think it's something to do with the python environment
    # that i'm running this in. I'm using all the same code as in the roboclaw
    # wrapper, but I can't get the motor to move. I do see the current go up
    # though. Weird.
    # todo: figure out what the difference is between the python environment
    # for running this, and the one running in ROS. 

    device = ctx.obj['device']
    baud_rate = ctx.obj['baud_rate']
    address = ctx.obj['address']

    rc = Roboclaw(device, baud_rate)
    rc.Open()

    # rc.ResetEncoders(address)
    # rc.WriteNVM(address)
    rc.ForwardM1(address, 0)

    # initialize connection status to successful
    logger.info("Attempting to command motor velocity...")
    
    # target_qpps = velocity2qpps(velocity, ticks_per_rev, gear_ratio)
    target_qpps = 364

    accel_max = 2**15-1
    # drive_accel = int(accel_max * accel_rate)
    drive_accel = 16383

    rate = 8
    import time

    while True:
        if channel == "M1":
            rc.SpeedAccelM1(address, drive_accel, target_qpps)
        elif channel == "M2":
            rc.SpeedAccelM2(address, drive_accel, target_qpps)
        time.sleep(1.0/rate)

        logger.info("Commanded motor {}, channel {}: to {} rad/s".format(
            address, channel, velocity))

@cli.command()
@click.pass_context
def stop_motor(ctx,
    ):
    device = ctx.obj['device']
    baud_rate = ctx.obj['baud_rate']
    address = ctx.obj['address']

    rc = Roboclaw(device, baud_rate)
    rc.Open()

    # initialize connection status to successful
    logger.info("Attempting to stop motor...")
    
    rc.ForwardM1(address, 0)
    rc.ForwardM2(address, 0)

    logger.info("Stopped motor {}".format(address))

if __name__ == '__main__':
    cli(obj={}) #pylint: disable=unexpected-keyword-arg,no-value-for-parameter