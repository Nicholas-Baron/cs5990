#!/usr/bin/python3

from matplotlib import pyplot
from typing import Dict, Union, Mapping

facebook = {
    1: 415,
    2: 485,
    4: 125,
    8: 96,
    16: 130,
}

twitter = {
    1: 244796,
    2: 4481,
    4: 6983,
    8: 11859,
    16: 41218,
}


def calc_speedup(times: Mapping[int, Union[int, float]]) -> Dict[int, float]:
    serial_time = times[1]
    return {procs: serial_time / time for procs, time in times.items()}


def plot(filename: str, x_axis: str, data: Mapping[int, Union[int, float]]):
    # Clear the previous run
    pyplot.clf()
    pyplot.cla()

    # Plot the input data
    pyplot.plot(data.keys(), data.values())
    pyplot.title(filename)
    pyplot.ylabel(x_axis)
    pyplot.xlabel("Number of MPI processes")
    pyplot.savefig(filename, bbox_inches="tight")


plot("Facebook Time", "Time in seconds", facebook)
plot("Twitter Time", "Time in seconds", twitter)
plot("Facebook Speedup", "Speedup relative to serial", calc_speedup(facebook))
plot("Twitter Speedup", "Speedup relative to serial", calc_speedup(twitter))
