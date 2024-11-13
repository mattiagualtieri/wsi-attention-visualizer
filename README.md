# wsi-attention-visualizer
Tool to create attention maps in Histopathological Whole Slide Images.

## How to use
### Format converter
The script `format_converter.py` can be executed both from `main.py` and as main itself. Is needed to convert 
images in different formats (SVS, DZI, MRXS). To be visualized, slides and attention maps must be converted 
into DZI.

Example of command to execute:
```commandline
python main.py --command format_converter --input_file /path/to/svs --output_file /path/to/dzi --smooth False
```

There is a naming convention to name slides and attention maps converted to DZI:
- Tumor type
- Patient ID
- Signature
- Model name
- Epoch

Example:
```
TCGA-OV_TCGA-23-2078_CCNE1_MCAT_20
```

### Create attention
The script `create_attention.py` is used to create attention maps from the attention weights in output of 
multimodal models.

Example:
```commandline
python main.py --command create_attention --input_file /path/to/slide/svs --patches_coords /path/to/clam/patches/h5 --attention_weights /path/to/attention/pt --patches_chunk_size 1000 --output_file /path/to/output/slide/svs --use_cache True
```

In SLURM environment, it's possible to use the following `.sbatch` file:
```shell
#!/bin/bash
#SBATCH --job-name=attention_wsi
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=<email>
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --time=60
#SBATCH --mem=24G
#SBATCH --output=logs/run.log
#SBATCH --err=logs/error.run.log

DATASET=tcga-ov
SLIDE=TCGA-13-A5FT-01Z-00-DX1.2B292DC8-7336-4CD9-AB1A-F6F482E6151A
ATTENTION_IN=ATTN_NaCAGaT_TCGA-13-A5FT_202410311541_E10_0
ATTENTION_OUT=$ATTENTION_IN
PATCHES_CHUNK_SIZE=1000

echo "Dataset: $DATASET"
echo "Slide: $SLIDE"
echo "Attention input: $ATTENTION_IN"
echo "Attention output: $ATTENTION_OUT"

echo "Executing attention creation..."
conda run -n pyvips python main.py --command create_attention --input_file input/slides/$DATASET/$SLIDE.svs --patches_coords input/patches/$DATASET/$SLIDE.h5 --attention_weights input/attention/$DATASET/$ATTENTION_IN.pt --patches_chunk_size $PATCHES_CHUNK_SIZE --output_file output/slides/$DATASET/$ATTENTION_OUT.svs --use_cache True
```

### Patients
New slides and new attention visualization must be added to the `patients.json` file. Each new patient
must be added in the correspondent cancer type (e.g. TCGA-OV). A patient is defined as follows:
```json
{
    "id": "TCGA-13-A5FT",
    "visible": true,
    "notes": "Any significant notes here",
    "signatures": [
        {
            "name": "CCNE1",
            "epochs": [
                20
            ]
        },
        {
            "name": "EMT",
            "epochs": [
                20
            ]
        }
    ]
}
```

### Visualize attention

https://github.com/user-attachments/assets/4ac85676-4e0a-4385-af99-31793ac33f2b
