"""
takameru.py

Author:
    kinami

Created:
    2/13/22
"""
import os.path
import zipfile

import click
import questionary
from PIL import Image
from alive_progress import alive_it
from waifu2x_ncnn_vulkan_python import Waifu2x


def extract(file: str) -> list[Image]:
    """
    Extracts all images from a CBZ fp
    :param file: the fp
    :return: a list of PIL images
    """
    assert '.cbz' in file, 'The input fp must be a CBZ fp'

    print('Extracting images...')
    res = []
    with zipfile.ZipFile(file) as z:
        for i in z.infolist():
            if i.filename.endswith('.jpg') or i.filename.endswith('.png') or i.filename.endswith('.jpeg'):
                res.append((os.path.basename(i.filename), Image.open(z.open(i))))

    return res


def upscale(images: list[tuple[str, Image]], waifu2x: Waifu2x) -> list[Image]:
    """
    Upscales all PIL images inputted
    :param waifu2x: the waifu2x upscaler
    :param images: the images to upscale
    :return: a list of upscaled images
    """
    # Upscales the images
    res = []
    bar = alive_it(images, length=20)
    for f, im in bar:
        bar.text(f'Upscaling {f}')
        res.append(waifu2x.process(im))

    return res


def save_to_pdf(images: list[Image], output: str):
    """
    Saves a list of images to a PDF
    :param images: the images to save
    :param output: the output fp
    """
    print(f'Saving in {output}...')
    images[0].save(output, save_all=True, append_images=images[1:])


@click.command()
@click.option('-n', '--noise-level',    'noise', default=2, help='denoise level (-1/0/1/2/3, default=0)')
@click.option('-s', '--scale',          'scale', default=2, help='upscale ratio (1/2/4/8/16/32, default=2)')
@click.argument('fp')
@click.argument('output')
def takameru(fp: str, output: str, noise: int, scale: int):
    """
    Upscales a CBZ file or all CBZ files in a folder
    :param fp: the file or directory to upscale
    :param output: the file or directory to save the output
    :param noise: the denoising level
    :param scale: the scaling factor
    """
    # Checks the fp exists has a compatible extension
    assert os.path.isfile(fp) or os.path.isdir(fp), 'The input path does not exist'

    if os.path.isfile(fp):
        files = [fp]
    else:
        assert os.path.isdir(output), 'The output path does not exist'
        files = [
            os.path.join(fp, f)
            for f
            in os.listdir(fp)
            if os.path.isfile(os.path.join(fp, f))
            and '.cbz' in f
        ]

    # Creates the waifu2x upscaler
    print('Starting waifu2x...')
    waifu2x = Waifu2x(gpuid=0, scale=scale, noise=noise, num_threads=4)

    for f in files:
        out = os.path.join(output, os.path.basename(f).replace('.cbz', '.pdf'))
        if os.path.isfile(out) and not questionary.confirm(f'{out} already exists. Do you wish to overwrite it?').ask():
            continue
        if os.path.isfile(out):
            os.remove(out)

        print(f'\nProcessing {os.path.basename(f)}...')
        images = extract(f)
        images = upscale(images, waifu2x)
        save_to_pdf(images, out)


if __name__ == '__main__':
    takameru()
    print('Done!')
