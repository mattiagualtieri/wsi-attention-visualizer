import pyvips
import os

from progress.bar import Bar


progress = 0
progress_bar = Bar('Converting file', suffix='%(percent)d%%, ETA: %(eta)ds')


def eval_progress(_, write_progress):
    global progress
    if write_progress.percent != progress:
        progress = write_progress.percent
        progress_bar.next()


def from_svs_to_dzi(input_file, output_file):
    svs_image = pyvips.Image.new_from_file(input_file)
    dzi_image, _ = os.path.splitext(output_file)
    svs_image.set_progress(True)
    svs_image.signal_connect('eval', eval_progress)
    svs_image.dzsave(dzi_image, tile_size=256, overlap=1)
    progress_bar.finish()


def format_converter(args: dict):
    input_file = args['input_file']
    output_file = args['output_file']
    _, input_extension = os.path.splitext(input_file)
    _, output_extension = os.path.splitext(output_file)
    if input_extension == '.svs' and output_extension == '.dzi':
        print(f'Converting {input_file} into {output_file}')
        from_svs_to_dzi(input_file, output_file)
        print('Convertion succeeded!')
    else:
        raise NotImplementedError(f'Converter from "{input_extension}" to "{output_extension}" not supported')


if __name__ == '__main__':
    args = {
        # 'input_file': 'input/slides/TCGA-A2-A0CW-01Z-00-DX1.8E313A22-B0E8-44CF-ADEA-8BF29BA23FFE.svs',
        'input_file': 'output/slides/ATTN_TCGA-A2-A0CW-01Z-00-DX1.8E313A22-B0E8-44CF-ADEA-8BF29BA23FFE.svs',
        # 'output_file': 'output/dzi/slide.dzi',
        'output_file': 'output/dzi/ATTN_TCGA-A2-A0CW-01Z-00-DX1.8E313A22-B0E8-44CF-ADEA-8BF29BA23FFE.dzi',
    }
    format_converter(args)
