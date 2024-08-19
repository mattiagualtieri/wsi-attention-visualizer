import pyvips
import torch
import h5py
import os

from utils.color import ColorGradient

progress = 0


def eval_progress(_, write_progress):
    global progress
    if write_progress.percent != progress:
        progress = write_progress.percent
        print('{}%, eta {}s'.format(write_progress.percent, write_progress.eta))


def create_attention(args: dict):
    use_cache = args['use_cache']
    if not use_cache:
        pyvips.cache_set_max(0)

    work_dir = 'work'
    if 'work_dir' in args:
        work_dir = args['work_dir']

    patches_coords = args['patches_coords']
    with h5py.File(patches_coords, 'r') as f:
        coords = f['coords'][:]
    total_patches = len(coords)
    print(f'Successfully loaded {total_patches} patch coordinates from {patches_coords}')

    input_slide = args['input_file']
    slide = pyvips.Image.new_from_file(input_slide, access='sequential')
    if slide.interpretation != 'srgb':
        slide = slide.colourspace('srgb')
    slide_width = slide.width
    slide_height = slide.height
    print(f'Successfully loaded {input_slide} slide')

    attention_weights_file = args['attention_weights']
    attention_weights = torch.load(attention_weights_file)[1]
    print(f'Attention weights size: {len(attention_weights)}')
    min_val = attention_weights.min()
    max_val = attention_weights.max()
    print(f'Attention values between [{min_val.item()}, {max_val.item()}]')
    attention_weights = (attention_weights - min_val) / (max_val - min_val)
    print(f'Loaded and normalized weights from {attention_weights_file}')

    attention = pyvips.Image.black(slide_width, slide_height).addalpha()
    attention = attention.new_from_image([255, 255, 255, 255])
    attention = attention.copy(interpretation='srgb')

    color_gradient = ColorGradient()
    color_gradient.create_default_heatmap_gradient()

    patches_chunk_size = args['patches_chunk_size']
    print(f'Using patches chunk size: {patches_chunk_size}')
    chunks = []
    for i in range(0, total_patches, patches_chunk_size):
        chunk_coords = coords[i:i + patches_chunk_size]
        mx = my = Mx = My = -1
        chunk = pyvips.Image.black(slide_width, slide_height).addalpha()
        chunk = chunk.new_from_image([255, 255, 255, 0])
        chunk = chunk.copy(interpretation='srgb')
        patch_index = 0
        for coord in chunk_coords:
            x, y = coord
            if mx < 0 or x < mx:
                mx = x
            if my < 0 or y < my:
                my = y
            if Mx < 0 or x + 256 > Mx:
                print(f'Condition true: Mx: {Mx} --> {x + 256}')
                Mx = x + 256
            if My < 0 or y + 256 > My:
                My = y + 256
            patch = pyvips.Image.black(256, 256).addalpha()
            color = color_gradient.get_color_at_value(attention_weights[patch_index])
            patch = patch.new_from_image([color[0], color[1], color[2], 255])
            patch = patch.copy(interpretation='srgb')
            chunk = chunk.insert(patch, x, y)
            patch_index += 1
        print(f'Progress: {i}/{total_patches}')
        print(f'Cropping chunk at [x: {mx} - {Mx}, y: {my} - {My}]')
        cropped_chunk = chunk.crop(mx, my, Mx, My)
        chunk_file = f'{work_dir}/{len(chunks)}.png'
        cropped_chunk.write_to_file(chunk_file)
        chunks.append({
            'chunk_file': chunk_file,
            'x': mx,
            'y': my
        })

    output_slide = args['output_file']
    print(f'Saving attention slide into {output_slide}')
    for c in chunks:
        chunk = pyvips.Image.new_from_file(c['chunk_file'])
        attention = attention.composite(chunk, 'over', x=c['x'], y=c['y'])

    attention.set_progress(True)
    attention.signal_connect('eval', eval_progress)
    attention.tiffsave(output_slide, tile=True, pyramid=True, compression='jpeg', Q=80, bigtiff=True)
    for c in chunks:
        os.remove(c['chunk_file'])
    print('Attention slide saved!')


if __name__ == '__main__':
    args = {
        'input_file': 'input/slides/TCGA-A2-A0CW-01Z-00-DX1.8E313A22-B0E8-44CF-ADEA-8BF29BA23FFE.svs',
        'use_cache': True,
        'patches_coords': 'input/patches/TCGA-A2-A0CW-01Z-00-DX1.8E313A22-B0E8-44CF-ADEA-8BF29BA23FFE.h5',
        'attention_weights': 'input/attention/ATTN_TCGA-A2-A0CW-01Z-00-DX1.8E313A22-B0E8-44CF-ADEA-8BF29BA23FFE.pt',
        'patches_chunk_size': 1000,
        'output_file': 'output/slides/ATTN_TCGA-A2-A0CW-01Z-00-DX1.8E313A22-B0E8-44CF-ADEA-8BF29BA23FFE.svs'
    }
    create_attention(args)
