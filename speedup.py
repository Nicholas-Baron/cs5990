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
    pyplot.plot(
        data.keys(),
        data.values(),
    )
    pyplot.title(filename)
    pyplot.ylabel(x_axis)
    pyplot.xlabel("Number of MPI processes")
    pyplot.savefig(filename)


plot("Twitter Time", "Time in seconds", twitter)
