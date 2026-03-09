# ------------------------------------------------------------------------------
#  (c) Crown copyright Met Office. All rights reserved.
#  The file LICENCE, distributed with this code, contains details of the terms
#  under which the code may be used.
# ------------------------------------------------------------------------------
from dataclasses import dataclass
import sys
import numpy as np
from pathlib import Path
from typing import Optional

class VernierCaliper():
    """Class to hold data for a single Vernier caliper, including arrays for each metric."""

    self_time: np.ndarray
    total_time: np.ndarray
    time_percent: np.ndarray
    cumul_time: np.ndarray
    n_calls: np.ndarray
    name: str

    def __init__(self, name: str, n_ranks: int):

        self.name = name
        self.time_percent = np.zeros(n_ranks)
        self.cumul_time = np.zeros(n_ranks)
        self.self_time = np.zeros(n_ranks)
        self.total_time = np.zeros(n_ranks)
        self.n_calls = np.zeros(n_ranks)

        return

    def reduce(self) -> list:
        """Reduces the data for this caliper to a single row of summary data."""

        return [
            self.name.replace('@0', ''), # caliper name
            round(self.total_time.mean(), 5), # mean total time across calls
            round(self.self_time.mean(), 5), # mean self time across calls
            round(self.cumul_time.mean(), 5), # mean cumulative time across calls
            int(self.n_calls[0])    , # number of calls (should be the same for all entries, so just take the first)
            round(self.time_percent.mean(), 5), # mean percentage of time across calls
            round(self.total_time.mean() / self.n_calls[0], 5) # mean time per call
        ]

    def __lt__(self, other):
        """Comparison method for sorting calipers by self time."""
        return self.self_time.sum() < other.self_time.sum()

    def __eq__(self, other):
        """Equality method for comparing calipers by self time."""
        return self.self_time.sum() == other.self_time.sum()

    def __gt__(self, other):
        """Comparison method for sorting calipers by self time."""
        return self.self_time.sum() > other.self_time.sum()


class VernierData():
    """Class to hold Vernier data in a structured way, and provide methods for filtering and outputting the data."""

    def __init__(self):

        self.data = {}

        return


    def add_caliper(self, caliper_key: str, n_ranks: int):
        """Adds a new caliper to the data structure, with empty arrays for each metric."""

        # Create empty data arrays
        self.data[caliper_key] = VernierCaliper(caliper_key, n_ranks)


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
        for caliper in self.data.keys():
            txt_table.append(self.data[caliper].reduce())
        txt_table = sorted(txt_table, key=lambda x: x[2], reverse=True) # sort by self time, descending

        txt_table.insert(0, ["Routine", "Total time (s)", "Self (s)", "Cumul time (s)", "No. calls", "% time", "Time per call (s)"])

        max_caliper_len = max([len(line[0]) for line in txt_table])

        # Write to stdout if no path provided, otherwise write to file
        if txt_path is None:
            out = sys.stdout
        else:
            out = open(txt_path, 'w')

        for row in txt_table:
            out.write('| {:>{}} | {:>14} | {:>12} | {:>14} | {:>9} | {:>8} | {:>17} |\n'.format(row[0], max_caliper_len, *row[1:]))

        if txt_path is not None:
            out.close()

def aggregate(vernier_data_list: list[VernierData], internal_consistency: bool = True) -> VernierData:
    """
    Aggregates a list of VernierData objects into a single VernierData object,
    by concatenating the data for each caliper across the input objects.
    """

    aggregated = VernierData()

    if internal_consistency:
        # Check that all input VernierData objects have the same set of calipers
        caliper_sets = [set(vernier_data.data.keys()) for vernier_data in vernier_data_list]
        if not all(caliper_set == caliper_sets[0] for caliper_set in caliper_sets):
            raise ValueError("Input VernierData objects do not have the same set of calipers, " \
                             "but internal_consistency is set to True.")

    for i, vernier_data in enumerate(vernier_data_list):
        n_datasets = len(vernier_data_list)
        for caliper in vernier_data.data.keys():
            if not caliper in aggregated.data:
                len_dataset = len(vernier_data.data[caliper].self_time)
                aggregated.add_caliper(caliper, n_datasets * len_dataset)

            data_begin = i*len_dataset
            data_end = (i+1)*len_dataset
            aggregated.data[caliper].time_percent[data_begin:data_end] = vernier_data.data[caliper].time_percent
            aggregated.data[caliper].cumul_time[data_begin:data_end] = vernier_data.data[caliper].cumul_time
            aggregated.data[caliper].self_time[data_begin:data_end] = vernier_data.data[caliper].self_time
            aggregated.data[caliper].total_time[data_begin:data_end] = vernier_data.data[caliper].total_time
            aggregated.data[caliper].n_calls[data_begin:data_end] = vernier_data.data[caliper].n_calls

    return aggregated
