#!/usr/bin/env python3

import argparse
import os
import pandas as pd
import plotly.graph_objects as go

def compute_bull_bear_boundaries(input_csv):
    """
    Reads the CSV file, determines the boundary sample numbers between
    Bull #1 / Bear / Bull #2, and returns them.

    Returns:
        (boundary_sample_1, boundary_sample_2, final_sample)

    Where:
    - boundary_sample_1 = the sample index at which Bull #1 changes to Bear
      (max Close in the first half)
    - boundary_sample_2 = the sample index at which Bear changes to Bull #2
      (min Close in the second half)
    - final_sample       = the final sample index in the dataset
    """
    # Read CSV
    df = pd.read_csv(input_csv)

    # Ensure we have a 0-based "Sample" index
    # so that df["Sample"] goes from 0 to len(df)-1
    df.reset_index(drop=False, inplace=True)
    df.rename(columns={"index": "Sample"}, inplace=True)

    # Split data into first half and second half
    half_idx = len(df) // 2
    df_first_half = df.iloc[:half_idx]
    df_second_half = df.iloc[half_idx:]

    # Row index of max Close in the first half
    row_max_close_first_half = df_first_half["Close"].idxmax()
    # Row index of min Close in the second half
    row_min_close_second_half = df_second_half["Close"].idxmin()

    boundary_sample_1 = df.loc[row_max_close_first_half, "Sample"]
    boundary_sample_2 = df.loc[row_min_close_second_half, "Sample"]
    final_sample = len(df) - 1

    return boundary_sample_1, boundary_sample_2, final_sample


def create_plot_figure(input_csv, boundary_sample_1, boundary_sample_2):
    """
    Creates and returns a Plotly Figure with three line segments:
        - Bull #1: from start to boundary_sample_1
        - Bear:    from boundary_sample_1 to boundary_sample_2
        - Bull #2: from boundary_sample_2 to the end

    The figure also contains a candlestick chart of the OHLC data.

    Returns:
        plotly.graph_objects.Figure
    """
    # Read CSV
    df = pd.read_csv(input_csv)

    # Ensure we have a 0-based "Sample" index
    df.reset_index(drop=False, inplace=True)
    df.rename(columns={"index": "Sample"}, inplace=True)

    # Convert the DateTime column from Unix seconds
    df["DateTime"] = pd.to_datetime(df["DateTime"], unit="s")

    # Build candlestick chart
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df["DateTime"],
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="OHLC"
            )
        ]
    )

    # Determine a Y value slightly above the lowest "Low"
    lowest_val = df["Low"].min()
    highest_val = df["High"].max()
    y_range = highest_val - lowest_val
    y_line = lowest_val + 0.02 * y_range

    # Convert sample indices to DateTimes for the shapes
    time_min = df["DateTime"].min()
    time_max = df["DateTime"].max()

    # boundary_time_1 is the DateTime for boundary_sample_1
    boundary_time_1 = df.loc[df["Sample"] == boundary_sample_1, "DateTime"].iloc[0]
    # boundary_time_2 is the DateTime for boundary_sample_2
    boundary_time_2 = df.loc[df["Sample"] == boundary_sample_2, "DateTime"].iloc[0]

    # Add shapes (Bull-Bear-Bull) on a horizontal line
    fig.add_shape(
        type="line",
        xref="x",
        yref="y",
        x0=time_min,
        x1=boundary_time_1,
        y0=y_line,
        y1=y_line,
        line=dict(color="skyblue", width=6),
        name="Bull Market (Segment 1)"
    )

    fig.add_shape(
        type="line",
        xref="x",
        yref="y",
        x0=boundary_time_1,
        x1=boundary_time_2,
        y0=y_line,
        y1=y_line,
        line=dict(color="orange", width=6),
        name="Bear Market"
    )

    fig.add_shape(
        type="line",
        xref="x",
        yref="y",
        x0=boundary_time_2,
        x1=time_max,
        y0=y_line,
        y1=y_line,
        line=dict(color="skyblue", width=6),
        name="Bull Market (Segment 2)"
    )

    # Update layout
    fig.update_layout(
        title="OHLC Plot with Bull-Bear-Bull Market Segments",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False
    )

    return fig


def main():
    parser = argparse.ArgumentParser(
        description="Plot OHLC data, mark bull/bear segments, and optionally show/save the figure."
    )
    parser.add_argument("input_csv", help="Path to the input CSV file.")
    parser.add_argument("output_file", nargs="?", default=None, help="Optional output filename (HTML or image).")
    parser.add_argument("--show-figure", action="store_true", default=False,
                        help="If set, display the Plotly figure on screen.")

    args = parser.parse_args()

    # 1. Compute boundary samples
    boundary_sample_1, boundary_sample_2, final_sample = compute_bull_bear_boundaries(args.input_csv)

    # Print them
    print(f"Bull Market #1: start sample = 0, end sample = {boundary_sample_1}")
    print(f"Bear Market   : start sample = {boundary_sample_1}, end sample = {boundary_sample_2}")
    print(f"Bull Market #2: start sample = {boundary_sample_2}, end sample = {final_sample}")

    # 2. Create plot figure
    fig = create_plot_figure(args.input_csv, boundary_sample_1, boundary_sample_2)

    # 3. Show figure if requested
    if args.show_figure:
        fig.show()

    # 4. Save figure if output file is specified
    if args.output_file:
        _, extension = os.path.splitext(args.output_file)
        extension = extension.lower()

        if extension == ".html":
            fig.write_html(args.output_file)
            print(f"Chart saved as HTML to: {args.output_file}")
        else:
            # For static images, you need kaleido installed:
            #   pip install kaleido
            fig.write_image(args.output_file, width=1920, height=1080, scale=2)
            print(f"Chart saved as an image to: {args.output_file}")


if __name__ == "__main__":
    main()