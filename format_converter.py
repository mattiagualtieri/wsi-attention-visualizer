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


def from_svs_to_dzi(input_file, output_file, smooth=False):
    svs_image = pyvips.Image.new_from_file(input_file)
    if smooth:
        print('Applying smoothing to the image')
        svs_image = svs_image.gaussblur(100)
    dzi_image, _ = os.path.splitext(output_file)
    svs_image.set_progress(True)
    svs_image.signal_connect('eval', eval_progress)
    svs_image.dzsave(dzi_image, tile_size=256, overlap=1)
    progress_bar.finish()


def from_mrxs_to_svs(input_file, output_file):
    input_image = pyvips.Image.new_from_file(input_file, access='sequential')
    output_image, _ = os.path.splitext(output_file)
    input_image.set_progress(True)
    input_image.signal_connect('eval', eval_progress)
    input_image.tiffsave(output_image + '.svs',
                         tile=True,
                         pyramid=True,
                         bigtiff=True,
                         compression="jpeg",
                         Q=80,
                         tile_width=256,
                         tile_height=256)
    progress_bar.finish()


def from_mrxs_to_dzi(input_file, output_file):
    input_image = pyvips.Image.new_from_file(input_file, access='sequential')
    output_image, _ = os.path.splitext(output_file)
    input_image.set_progress(True)
    input_image.signal_connect('eval', eval_progress)
    input_image.dzsave(output_image, tile_size=256, overlap=1)
    progress_bar.finish()


def format_converter(args: dict):
    input_file = args['input_file']
    output_file = args['output_file']
    _, input_extension = os.path.splitext(input_file)
    _, output_extension = os.path.splitext(output_file)

    print(f'Converting {input_file} into {output_file}')
    if input_extension == '.svs' and output_extension == '.dzi':
        from_svs_to_dzi(input_file, output_file, args['smooth'])
    elif input_extension == '.mrxs' and output_extension == '.svs':
        from_mrxs_to_svs(input_file, output_file)
    elif input_extension == '.mrxs' and output_extension == '.dzi':
        from_mrxs_to_dzi(input_file, output_file)
    else:
        raise NotImplementedError(f'Converter from "{input_extension}" to "{output_extension}" not supported')

    print('Conversion succeeded!')


if __name__ == '__main__':

    # Naming
    # convention:
    # - Cancer type (TCGA-BRCA, DECIDER, ...)
    # - Patient (TCGA-A2-A0EY, D328, ...)
    # - Model (NaCAGaT, MCAT)
    # - Signature (TUMOR-SUPPRESSOR, CCN1, ...)
    # - Epoch (05, 20, ...)

    dataset = 'tcga-ov'
    attention = 'ATTN_MCAT_TCGA-23-2078_20241106193004_E20_0'
    output = 'TCGA-OV_TCGA-23-2078_CCNE1_MCAT_20'
    # mrxs = 'H084_pOme_PE_IIB_231123'
    # svs = 'H173_pPer_PE_I_HE_rscn'

    args = {
        # 'input_file': f'input/mrxs/{dataset}/{mrxs}.mrxs',
        # 'output_file': 'output/dzi/DECIDER_H084-CCNE1.dzi',
        # 'input_file': f'input/slides/{dataset}/{svs}.svs',
        # 'input_file': 'output/slides/tcga-ov/ATTN_TCGA-25-1320_E50_local_2.svs',
        # 'output_file': f'input/slides/decider-ov/{mrxs}.svs',
        'input_file': f'output/slides/{dataset}/{attention}.svs',
        'output_file': f'output/dzi/{output}.dzi',
        'smooth': False
    }
    format_converter(args)
