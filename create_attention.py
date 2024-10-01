import pyvips
import torch
import h5py
import os

from utils.color import ColorGradient
from progress.bar import Bar

progress = 0
progress_bar_patches = Bar('Processing patches', suffix='%(index)d/%(max)d, ETA: %(eta)ds')
progress_bar_attention = Bar('Saving attention file', suffix='%(percent)d%%, ETA: %(eta)ds')


def eval_progress(_, write_progress):
    global progress
    if write_progress.percent != progress:
        progress = write_progress.percent
        progress_bar_attention.next()


def clamp(value, min=0, max=0):
    if value < min:
        return min
    if value > max:
        return max
    return value


def get_min_max_chunked(tensor, chunk_size=10000):
    min_val = float('inf')
    max_val = float('-inf')
    for i in range(0, tensor.size(0), chunk_size):
        chunk = tensor[i:i + chunk_size]
        min_val = min(min_val, chunk.min().item())
        max_val = max(max_val, chunk.max().item())
    return torch.tensor(min_val), torch.tensor(max_val)


def normalize_tensor_chunked(tensor, min_val, max_val, chunk_size=10000):
    num_elements = tensor.numel()
    for start in range(0, num_elements, chunk_size):
        end = min(start + chunk_size, num_elements)
        tensor.view(-1)[start:end] = (tensor.view(-1)[start:end] - min_val) / (max_val - min_val)


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
    print(f'Successfully loaded {input_slide} slide: [w: {slide_width}, h: {slide_height}]')

    attention_weights_file = args['attention_weights']
    attention_weights = torch.load(attention_weights_file, weights_only=True, map_location=torch.device('cpu'))[0]
    print(f'Attention weights size: {len(attention_weights)}')
    min_val, max_val = get_min_max_chunked(attention_weights)
    print(f'Attention values between [{min_val.item()}, {max_val.item()}]')
    normalize_tensor_chunked(attention_weights, min_val, max_val)
    print(f'Loaded and normalized weights from {attention_weights_file}')

    attention = pyvips.Image.black(slide_width, slide_height).addalpha()
    attention = attention.new_from_image([255, 255, 255, 255])
    attention = attention.copy(interpretation='srgb')

    color_gradient = ColorGradient()
    color_gradient.create_default_heatmap_gradient()

    create_png = True
    if len(os.listdir(work_dir)) != 0:
        print(f'Directory {work_dir} not empty, using existing PNGs')
        create_png = False

    patches_chunk_size = args['patches_chunk_size']
    print(f'Using patches chunk size: {patches_chunk_size}')
    chunks = []
    global_index = 0
    progress_bar_patches.max = total_patches
    for i in range(0, total_patches, patches_chunk_size):
        chunk_coords = coords[i:i + patches_chunk_size]
        mx = my = Mx = My = -1
        chunk = None
        if create_png:
            chunk = pyvips.Image.black(slide_width, slide_height).addalpha()
            chunk = chunk.new_from_image([255, 255, 255, 0])
            chunk = chunk.copy(interpretation='srgb')
        for coord in chunk_coords:
            x, y = coord
            if mx < 0 or x < mx:
                mx = x
            if my < 0 or y < my:
                my = y
            if Mx < 0 or x + 256 > Mx:
                Mx = x + 256
            if My < 0 or y + 256 > My:
                My = y + 256

            if create_png:
                patch = pyvips.Image.black(256, 256).addalpha()
                color = color_gradient.get_color_at_value(attention_weights[global_index])
                patch = patch.new_from_image([color[0], color[1], color[2], 255])
                patch = patch.copy(interpretation='srgb')
                chunk = chunk.insert(patch, x, y)

            global_index += 1
        progress_bar_patches.next(n=patches_chunk_size)
        mx, my = clamp(mx, max=slide_width), clamp(my, max=slide_height)
        Mx, My = clamp(Mx, max=slide_width), clamp(My, max=slide_height)
        chunk_file = f'{work_dir}/{len(chunks)}.png'
        if create_png:
            cropped_chunk = chunk.crop(mx, my, Mx - mx, My - my)
            cropped_chunk.cast("uchar").write_to_file(chunk_file)
        chunks.append({
            'chunk_file': chunk_file,
            'x': mx,
            'y': my
        })
    progress_bar_patches.finish()

    output_slide = args['output_file']
    print(f'Saving attention slide into {output_slide}')
    for c in chunks:
        chunk = pyvips.Image.new_from_file(c['chunk_file'])
        attention = attention.composite(chunk, 'over', x=c['x'], y=c['y'])

    attention.set_progress(True)
    attention.signal_connect('eval', eval_progress)
    attention.cast("uchar").tiffsave(output_slide, tile=True, pyramid=True, compression='jpeg', Q=80, bigtiff=True)
    for c in chunks:
        os.remove(c['chunk_file'])
    print('Attention slide saved!')
    progress_bar_attention.finish()


if __name__ == '__main__':
    args = {
        'input_file': 'input/slides/tcga-ov/TCGA-25-1320-01A-01-TS1.7baccc6e-48b9-4f66-b04a-5a550b77dfce.svs',
        'use_cache': False,
        'patches_coords': 'input/patches/tcga-ov/TCGA-25-1320-01A-01-TS1.7baccc6e-48b9-4f66-b04a-5a550b77dfce.h5',
        'attention_weights': 'input/attention/tcga-brca/ATTN_TCGA-A2-A0CW-01Z-00-DX1.8E313A22-B0E8-44CF-ADEA-8BF29BA23FFE.pt',
        'patches_chunk_size': 2000,
        'output_file': 'output/slides/tcga-ov/ATTN_TCGA-25-1320_E50_local.svs'
    }
    with torch.no_grad():
        create_attention(args)
