"""
mini_takameru.py

Package 

Author:
    kinami

Created:
    23/4/22
"""
import os

import click
from PIL import Image

from takameru import upscale, waifu_2x


@click.command()
@click.argument(
    'dir',
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True
    )
)
@click.option('-n', '--noise-level',    'noise',    default=0,      help='denoise level (-1/0/1/2/3, default=0)')
@click.option('-s', '--scale',          'scale',    default=2,      help='upscale ratio (1/2/4/8/16/32, default=2)')
@click.option('-f', '--format',         'format',   default='',     help='input format filter (default=all)')
def mini_takameru(dir: str, noise: int, scale: int, format: str):
    """
    Upscale all files in a folder
    :param dir: the input folder
    :param noise: the noise level
    :param scale: the scale ratio
    :param format: file extension to filter by
    """
    waifu2x = waifu_2x(scale, noise)

    upscale(
        [
            (f'{dir}/{f}', Image.open(f'{dir}/{f}'))
            for f
            in os.listdir(dir)
            if f.endswith(format)
        ],
        waifu2x,
        write=True
    )


if __name__ == '__main__':
    mini_takameru()
    print('Done!')
