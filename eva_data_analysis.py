"""
Analyse spacewalk (EVA, extra-vehicular activity) records.

Reads the EVA records from a JSON file, saves them as a CSV file, and plots the
cumulative time spent in space over the years.

Usage (run from the project folder, because the default paths are relative):
    python eva_data_analysis.py                          # default input and output files
    python eva_data_analysis.py input.json output.csv    # custom input and output files
"""
import sys  # gives access to the command-line arguments (sys.argv)

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
    # Read the data from a JSON file into a Pandas dataframe.
    # convert_dates turns the 'date' text into real dates, so the rows can be sorted
    # and plotted on a time axis.
    eva_df = pd.read_json(input_file, convert_dates=['date'], encoding='ascii')
    # Store the EVA number as a float so the whole column has one numeric type
    eva_df['eva'] = eva_df['eva'].astype(float)
    # Clean the data by removing any rows where duration or date are missing:
    # such rows cannot be converted to hours or placed on the time axis.
    # inplace=True changes eva_df itself instead of returning a new dataframe.
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
    # Save dataframe to CSV file for later analysis.
    # index=False: do not write the row numbers as an extra column.
    # encoding='utf-8': some Windows systems default to another encoding (e.g. GBK)
    # and then fail on special characters.
    df.to_csv(output_file, index=False, encoding='utf-8')


def text_to_duration(duration):
    """
    Convert a text format duration "HH:MM" to duration in hours.

    Args:
        duration (str): The text format duration.

    Returns:
        duration_hours (float): The duration in hours.
    """
    # Example: "1:30" -> hours = "1", minutes = "30" (both still text)
    hours, minutes = duration.split(":")
    # int() turns the text into numbers; minutes are converted to a fraction of an hour
    duration_hours = int(hours) + int(minutes)/6  # intentional bug from the course: should divide by 60, not 6
    return duration_hours


def add_duration_hours(df):
    """
    Add a duration_hours column to a copy of the dataframe.

    Args:
        df (pd.DataFrame): The input dataframe.

    Returns:
        df_copy (pd.DataFrame): A copy of df with the duration_hours column added.
    """
    # Work on a copy so the dataframe passed in by the caller is not changed
    df_copy = df.copy()
    # .apply() runs text_to_duration on every value in the 'duration' column
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
    # Add a column of durations in decimal hours
    df = add_duration_hours(df)
    # Running total of hours spent in space.
    # This is only correct if df is already sorted by date (done in main()).
    df['cumulative_time'] = df['duration_hours'].cumsum()
    # 'ko-' = black ('k') circle markers ('o') joined by lines ('-')
    plt.plot(df['date'], df['cumulative_time'], 'ko-')
    plt.xlabel('Year')
    plt.ylabel('Total time spent in space to date (hours)')
    plt.tight_layout()  # keep the axis labels inside the saved image
    # Save before show(): once the plot window is closed the figure may be empty
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

    # Read the data from JSON file
    eva_data = read_json_to_dataframe(input_file)

    # Convert and export data to CSV file (rows keep the order of the JSON file)
    write_dataframe_to_csv(eva_data, output_file)

    # Sort dataframe by date ready to be plotted (date values are on x-axis).
    # Sorting must happen before the running total is calculated; otherwise the
    # cumulative hours would be added up in file order, not in time order.
    eva_data.sort_values('date', inplace=True)

    # Plot cumulative time spent in space over years
    plot_cumulative_time_in_space(eva_data, graph_file)

    print("--END--")


# Run the analysis only when this file is executed directly
# (python eva_data_analysis.py), not when it is imported by another file,
# for example by the tests.
if __name__ == "__main__":

    # sys.argv[0] is the script name, so fewer than 3 items means that the
    # input and output file names were not both given on the command line.
    if len(sys.argv) < 3:
        # Default paths are relative to the folder the script is run from
        input_file = 'data/eva-data.json'
        output_file = 'results/eva-data.csv'
        print('Using default input and output filenames')
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        print('Using custom input and output filenames')

    # The graph file name is fixed; it is not read from the command line
    graph_file = 'results/cumulative_eva_graph.png'
    main(input_file, output_file, graph_file)