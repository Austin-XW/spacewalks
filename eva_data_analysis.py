"""
Analyse spacewalk (EVA) records: read a JSON file, save it as CSV, and plot the
cumulative time spent in space.

Usage (run from the project folder):
    python eva_data_analysis.py
    python eva_data_analysis.py input.json output.csv
"""
import sys

import matplotlib.pyplot as plt
import pandas as pd


def read_json_to_dataframe(input_file):
    """
    Read the data from a JSON file into a Pandas dataframe.
    Clean the data by removing any incomplete rows.

    Args:
        input_file (str): The path to the JSON file.

    Returns:
         eva_df (pd.DataFrame): The cleaned data as a dataframe structure
    """
    print(f'Reading JSON file {input_file}')
    # Parse 'date' as dates so the rows can be sorted and plotted over time
    eva_df = pd.read_json(input_file, convert_dates=['date'], encoding='ascii')
    eva_df['eva'] = eva_df['eva'].astype(float)
    # Drop rows without a duration or date: they cannot be plotted
    eva_df.dropna(axis=0, subset=['duration', 'date'], inplace=True)
    return eva_df


def write_dataframe_to_csv(df, output_file):
    """
    Write the dataframe to a CSV file.

    Args:
        df (pd.DataFrame): The input dataframe.
        output_file (str): The path to the output CSV file.

    Returns:
        None
    """
    print(f'Saving to CSV file {output_file}')
    # utf-8 avoids encoding errors on Windows
    df.to_csv(output_file, index=False, encoding='utf-8')


def text_to_duration(duration):
    """
    Convert a text format duration "HH:MM" to duration in hours.

    Args:
        duration (str): The text format duration.

    Returns:
        duration_hours (float): The duration in hours.
    """
    # e.g. "1:30" -> 1 + 30/60 = 1.5 hours
    hours, minutes = duration.split(":")
    duration_hours = int(hours) + int(minutes)/60
    return duration_hours


def add_duration_hours(df):
    """
    Add a duration_hours column to a copy of the dataframe.

    Args:
        df (pd.DataFrame): The input dataframe.

    Returns:
        df_copy (pd.DataFrame): A copy of df with the duration_hours column added.
    """
    # Copy, so the caller's dataframe is not changed
    df_copy = df.copy()
    df_copy["duration_hours"] = df_copy["duration"].apply(text_to_duration)
    return df_copy


def plot_cumulative_time_in_space(df, graph_file):
    """
    Plot the cumulative time spent in space over years.

    Calculate cumulative sum of durations.
    Generate a plot of cumulative time spent in space over years and
    save it to the specified location.

    Args:
        df (pd.DataFrame): The input dataframe.
        graph_file (str): The path to the output graph file.

    Returns:
        None
    """
    print(f'Plotting cumulative spacewalk duration and saving to {graph_file}')
    df = add_duration_hours(df)
    # Running total; assumes df is already sorted by date (see main)
    df['cumulative_time'] = df['duration_hours'].cumsum()
    plt.plot(df['date'], df['cumulative_time'], 'ko-')
    plt.xlabel('Year')
    plt.ylabel('Total time spent in space to date (hours)')
    plt.tight_layout()
    # Save before show(): the figure may be empty after the window is closed
    plt.savefig(graph_file)
    plt.show()


def main(input_file, output_file, graph_file):
    """
    Run the whole analysis: read the data, save it as CSV, and plot it.

    Args:
        input_file (str): The path to the input JSON file.
        output_file (str): The path to the output CSV file.
        graph_file (str): The path to the output graph file.

    Returns:
        None
    """
    print("--START--")

    eva_data = read_json_to_dataframe(input_file)
    write_dataframe_to_csv(eva_data, output_file)

    # Sort by date before the running total is calculated in the plot
    eva_data.sort_values('date', inplace=True)

    plot_cumulative_time_in_space(eva_data, graph_file)

    print("--END--")


# Run only when executed directly, not when imported (e.g. by the tests)
if __name__ == "__main__":

    # sys.argv[0] is the script name, so fewer than 3 items = no file names given
    if len(sys.argv) < 3:
        input_file = 'data/eva-data.json'
        output_file = 'results/eva-data.csv'
        print('Using default input and output filenames')
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        print('Using custom input and output filenames')

    graph_file = 'results/cumulative_eva_graph.png'
    main(input_file, output_file, graph_file)