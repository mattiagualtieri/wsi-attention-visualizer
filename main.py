import argparse

from create_attention import create_attention
from format_converter import format_converter


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--command', help="Command to execute", type=str, required=True)
    parser.add_argument('--input_file', help="Input slide (SVS format)", type=str, required=True)
    parser.add_argument('--use_cache', help="Whether to use cache during processing or not", type=bool, default=True)
    parser.add_argument('--patches_coords', help="File which contains patches coordinates (from CLAM in HDF5 format)", type=str)
    parser.add_argument('--patches_chunk_size', help="Chunk size of patches to elaborate", type=int, default=1000)
    parser.add_argument('--work_dir', help="Working directory", type=str, default='work')
    parser.add_argument('--output_file', help="Output file (SVS format)", type=str, required=True)
    args = vars(parser.parse_args())
    command = args['command']
    if command == 'create_attention':
        create_attention(args)
    elif command == 'format_converter':
        format_converter(args)
    else:
        raise NotImplementedError(f'Command "{command}" not supported')
