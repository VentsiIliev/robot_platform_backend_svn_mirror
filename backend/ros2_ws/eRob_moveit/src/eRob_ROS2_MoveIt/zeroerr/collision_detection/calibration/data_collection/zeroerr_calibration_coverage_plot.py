#!/usr/bin/env python3
"""Render Cartesian calibration coverage from a runner output directory."""

import argparse
import csv
import warnings
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run', help='run directory or coverage_points.csv')
    parser.add_argument('--output', help='output PNG (default: RUN/coverage.png)')
    args = parser.parse_args()

    source = Path(args.run).expanduser()
    csv_path = source if source.is_file() else source / 'coverage_points.csv'
    if not csv_path.is_file():
        parser.error(f'coverage CSV not found: {csv_path}')
    points = []
    with csv_path.open(newline='') as handle:
        for row in csv.DictReader(handle):
            points.append((float(row['x_m']), float(row['y_m']), float(row['z_m'])))
    if not points:
        parser.error('coverage CSV contains no Cartesian points (dry runs do not move the robot)')

    try:
        warnings.filterwarnings(
            'ignore', message='Unable to import Axes3D.*', category=UserWarning)
        import matplotlib.pyplot as plt
    except ImportError as exc:
        parser.error(f'matplotlib is required: {exc}')

    x, y, z = zip(*points)
    figure = plt.figure(figsize=(12, 9), constrained_layout=True)
    views = ((x, y, 'X [m]', 'Y [m]', 'XY'),
             (x, z, 'X [m]', 'Z [m]', 'XZ'),
             (y, z, 'Y [m]', 'Z [m]', 'YZ'))
    for number, (a, b, xlabel, ylabel, title) in enumerate(views, 1):
        axis = figure.add_subplot(2, 2, number)
        axis.scatter(a, b, c=range(len(points)), s=4, cmap='viridis')
        axis.axhline(0.0, color='black', linewidth=0.8, alpha=0.6)
        axis.axvline(0.0, color='black', linewidth=0.8, alpha=0.6)
        axis.set(xlabel=xlabel, ylabel=ylabel, title=f'{title} coverage')
        axis.grid(True, alpha=0.25)
        axis.set_aspect('equal', adjustable='box')
    try:
        axis3d = figure.add_subplot(2, 2, 4, projection='3d')
        axis3d.scatter(x, y, z, c=range(len(points)), s=4, cmap='viridis')
        axis3d.set(xlabel='X [m]', ylabel='Y [m]', zlabel='Z [m]', title='XYZ coverage')
    except (KeyError, ValueError):
        # Some systems accidentally mix apt and pip Matplotlib installations,
        # which removes the optional Axes3D projection. Preserve a useful plot.
        fallback = figure.add_subplot(2, 2, 4)
        scatter = fallback.scatter(x, y, c=z, s=5, cmap='viridis')
        fallback.set(
            xlabel='X [m]', ylabel='Y [m]',
            title='XY coverage colored by Z (3-D backend unavailable)')
        fallback.grid(True, alpha=0.25)
        fallback.axhline(0.0, color='black', linewidth=0.8, alpha=0.6)
        fallback.axvline(0.0, color='black', linewidth=0.8, alpha=0.6)
        fallback.set_aspect('equal', adjustable='box')
        figure.colorbar(scatter, ax=fallback, label='Z [m]')
    output = Path(args.output).expanduser() if args.output else csv_path.parent / 'coverage.png'
    figure.savefig(output, dpi=180)
    print(output)


if __name__ == '__main__':
    main()
