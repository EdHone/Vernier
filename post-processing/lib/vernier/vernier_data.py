from dataclasses import dataclass
import numpy as np
from pathlib import Path
from typing import Optional

@dataclass(order=True)
class VernierCaliper():
    """Class to hold data for a single Vernier caliper, including arrays for each metric."""

    total_time: list[float]
    time_percent: list[float]
    self_time: list[float]
    cumul_time: list[float]
    n_calls: list[int]
    name: str

    def __init__(self, name: str):

        self.name = name
        self.time_percent = []
        self.cumul_time = []
        self.self_time = []
        self.total_time = []
        self.n_calls = []

        return

    def reduce(self) -> list[str]:
        """Reduces the data for this caliper to a single row of summary data."""

        return [
            self.name.replace('@0', ''), # caliper name
            round(np.mean(self.total_time), 5), # mean total time across calls
            round(np.mean(self.self_time), 5), # mean self time across calls
            round(np.mean(self.cumul_time), 5), # mean cumulative time across calls
            self.n_calls[0], # number of calls (should be the same for all entries, so just take the first)
            round(np.mean(self.time_percent), 5), # mean percentage of time across calls
            round(np.mean(self.total_time) / self.n_calls[0], 5) # mean time per call
        ]

    @classmethod
    def labels(self):
        return ["Routine", "Total time (s)", "Self (s)", "Cumul time (s)",
                "No. calls", "% time", "Time per call (s)"]


class VernierData():
    """
    Class to hold Vernier data from a single instrumented job in a structured way.
    Provides methods for filtering and outputting the data.

    """

    def __init__(self):

        self.data = {}

        return


    def add_caliper(self, caliper_key):
        """Adds a new caliper to the data structure, with empty arrays for each metric."""

        # Create empty data arrays
        self.data[caliper_key] = VernierCaliper(caliper_key)

    def filter(self, caliper_keys: list[str]):
        """Filters the Vernier data to include only calipers matching the provided keys.
        The filtering is done in a glob-like fashion, so an input key of "timestep"
        will match any caliper with "timestep" in its name."""

        filtered_data = VernierData()

        # Filter data for a given caliper key
        for timer in self.data.keys():
            if any(caliper_key in timer for caliper_key in caliper_keys):
                filtered_data.data[timer] = self.data[timer]

        if len(filtered_data.data) == 0:
            raise ValueError(f"No calipers found matching the provided keys: {caliper_keys}")

        return filtered_data


    def write_txt_output(self, txt_path: Optional[Path] = None):
        """Writes the Vernier data to a text output in a human-readable table format.
        If an output path is provided, the table is written to that file. Otherwise,
        it is printed to the terminal."""

        txt_table = []
        txt_table.append(VernierCaliper.labels())
        for caliper in self.data.keys():
            txt_table.append(self.data[caliper].reduce())

        max_caliper_len = max([len(line[0]) for line in txt_table])
        if txt_path is None:
            for row in txt_table:
                print('| {:>{}} | {:>14} | {:>8} | {:>14} | {:>9} | {:>7} | {:>17} |'.format(row[0], max_caliper_len, *row[1:]))
            print("\n")
        else:
            with open(txt_path, 'w') as f:
                for row in txt_table:
                    f.write('| {:>{}} | {:>14} | {:>8} | {:>14} | {:>9} | {:>7} | {:>17} |\n'.format(row[0], max_caliper_len, *row[1:]))


class VernierDataAggregation():
    """
    Class to hold an aggregation of VernierData instances.
    Instances are asserted to be consistent in terms enforced by the
    interal_consistency method.

    """
    def __init__(self):
        self.vernier_data = {}
        return

    def add_data(self, label, vernier_data):
        if label in self.vernier_data:
            raise ValueError(f'The label {label} already exists in this aggregation. '
                             'please use a different label or remove the existing entry.')
        if not isinstance(vernier_data, VernierData):
            raise TypeError(f'The provided vernier_data is not a VernierData object.')
        self.vernier_data[label] = vernier_data

    def remove_data(self, label):
        if label not in self.vernier_data:
            raise ValueError(f'The label {label} does not exist in this aggregation. ')
        discarded = self.vernier_data.pop(label)

    def internal_consistency(self):
        # NotImplemented
        return true

    def caliper_list(self):
        result = []

        for k, vdata in self.vernier_data.items():
            loop_calipers = sorted(list(vdata.data.keys()))
            if len(result) == 0:
                result = loop_calipers
            else:
                if loop_calipers != result:
                    raise ValueError('inconsistent calipers in contents')
        result.sort()
        return result


    def get(self, caliper_key):
        """Return an array of all the data from all aggregation members"""
        results = VernierCaliper(caliper_key)
        for akey, vdata in self.vernier_data.items():
            results.total_time += vdata.data[caliper_key].total_time
            results.time_percent += vdata.data[caliper_key].time_percent
            results.self_time += vdata.data[caliper_key].self_time
            results.cumul_time += vdata.data[caliper_key].cumul_time
            results.n_calls += vdata.data[caliper_key].n_calls

        return results

