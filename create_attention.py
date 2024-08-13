import argparse
import pyvips
import h5py


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

    patches_coords = args['patches_coords']
    with h5py.File(patches_coords, 'r') as f:
        coords = f['coords'][:1000]
    total_patches = len(coords)
    print(f'Successfully loaded {total_patches} patch coordinates from {patches_coords}')

    input_slide = args['input_file']
    slide = pyvips.Image.new_from_file(input_slide, access='sequential')
    if slide.interpretation != 'srgb':
        slide = slide.colourspace('srgb')
    slide_width = slide.width
    slide_height = slide.height
    print(f'Successfully loaded {input_slide} slide')

    patches_chunk_size = args['patches_chunk_size']
    chunks = []
    for i in range(0, total_patches, patches_chunk_size):
        chunk_coords = coords[i:i + patches_chunk_size]
        mx = my = Mx = My = -1
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
            patch = pyvips.Image.black(256, 256).addalpha()
            patch = patch.new_from_image([255, 0, 0, 255])
            patch = patch.copy(interpretation='srgb')
            chunk = chunk.insert(patch, x, y)
        print(f'Progress: {i}/{total_patches}')
        cropped_chunk = chunk.crop(mx, my, Mx - mx, My - my)
        chunk_file = f'tmp/{len(chunks)}.png'
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
        slide = slide.insert(chunk, c['x'], c['y'])
    slide.set_progress(True)
    slide.signal_connect('eval', eval_progress)
    slide.tiffsave(output_slide, tile=True, pyramid=True, compression='jpeg', Q=80, bigtiff=True)
    print('Attention slide saved!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', help="Input slide (SVS format)", type=str, required=True)
    parser.add_argument('--use_cache', help="Whether to use cache during processing or not", type=bool, default=True)
    parser.add_argument('--patches_coords', help="File which contains patches coordinates (from CLAM in HDF5 format)", type=str)
    parser.add_argument('--patches_chunk_size', help="Chunk size of patches to elaborate", type=int, default=1000)
    parser.add_argument('--output_file', help="Output file (SVS format)", type=str, required=True)
    args = vars(parser.parse_args())
    create_attention(args)
