import pyvips
import os


def from_svs_to_dzi(input_file, output_file):
    svs_image = pyvips.Image.new_from_file(input_file)
    dzi_image, _ = os.path.splitext(output_file)
    pyvips.Image.dzsave(svs_image, dzi_image, tile_size=256, overlap=1)


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
