import itertools as it
import sys

import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib as mpl

import argparse as arg

def choose(subset, exclude, algo="first"):
    """ This is the main routine to find possible solutions"""
    exclude = [ex for ex in exclude if ex not in subset]

    possible = [comb for comb in all_combinations
                if all(value in comb for value in subset)
                and not any(value in comb for value in exclude)]
    try:
        if algo == 'first':
            ret = possible[0]
        if algo == 'rand':
            n_possible = len(possible)
            idx = random.randrange(n_possible)
            ret = possible[idx]
    except ValueError:
        print("Run unsuccessful: no viable combinations available")
        sys.exit()

    new_values = [val for val in ret if val not in subset]
    all_combinations.remove(ret)

    return ret, new_values

parser = arg.ArgumentParser(description='Generate a genetic pixel map.')
parser.add_argument('n_pixels', action="store", type=int, help="size of pixel map")
parser.add_argument('n_channels', action="store", type=int, help="number of channles")
parser.add_argument('size_subsquare', action="store", type=int, help="size of sub-square")
parser.add_argument('--plot', action="store_true", default=False, help="plot the pixel map")
parser.add_argument('--save_plot', action="store_true", default=False, help="save plot")
args = parser.parse_args()

n_pixel = args.n_pixels  # number of pixels
n_channels = args.n_channels

size_square = args.size_subsquare

# generate the central list of all possible combinations
all_combinations = list(it.combinations(range(n_channels), r=size_square * size_square))

# central pixel map, undefined values are marked as -1
pixel_map = -1 * np.ones((n_pixel, n_pixel))

# we loop over all pixels starting at index 0,0 and go through row wise. We step through all sub-squares
# with size "size_square" and pick a viable tuple from the list (if available)
for col_idx in range(n_pixel - 1):
    for row_idx in range(n_pixel - 1):
        # get the subsquare to process
        sub_square = pixel_map[col_idx:col_idx + 2, row_idx:row_idx + 2]
        sub_square_list = sub_square.flatten().tolist()

        exclude_values = []
        # look forward the sub-square size (from the starting edge). This value must be
        # excluded in the search
        if row_idx + 2 < n_pixel:
            exclude_values.append(pixel_map[col_idx, row_idx + 2])

        already_set_values = list(filter((-1.).__ne__, sub_square_list))
        _, new_vals = choose(already_set_values, exclude_values, algo='rand')

        # now fill the new values into the pixel map
        for new, idx, idy in zip(new_vals, *np.where(sub_square == -1)):
            sub_square[idx, idy] = new

print(pixel_map)

np.savetxt(f"map-n{n_pixel}-c{n_channels}-s{size_square}.txt", pixel_map, fmt="%2d")

if args.plot:
    cm = 1 / 2.54  # centimeters in inches
    qrates = list(range(n_channels))
    norm = mpl.colors.BoundaryNorm(np.linspace(0, n_channels, n_channels + 1), n_channels)
    fmt = mpl.ticker.FuncFormatter(lambda x, pos: qrates[::-1][norm(x)])

    fig, ax = plt.subplots(figsize=(5 * cm, 5 * cm))
    ax.imshow(pixel_map,
              cmap=mpl.colormaps["Dark2"].resampled(n_channels),
              norm=norm)

    # Loop over data dimensions and create text annotations.
    for i in range(n_pixel):
        for j in range(n_pixel):
            text = ax.text(j, i, f"{pixel_map[i, j]:.0f}",
                           ha="center", va="center", color="w")
    ax.axis('off')

    plt.tight_layout()

    if args.save_plot:
        plt.savefig(f"map-n{n_pixel}-c{n_channels}-s{size_square}.png")

    plt.show()