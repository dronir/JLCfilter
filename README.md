
# KiCad files to JLCSMD manufacture

This is a quick script to convert the BOM and position files produced by KiCad's Pcbnew
to the format that the JLCPCB assembly service desires. It simply loads in the CSV files,
selects the required columns, renames the columns to what JLC expects, and writes out
new CSV files.

Requires [Pandas](https://pandas.pydata.org/) for processing the CSV files.

## Files

This script will work on these two specific files:

* BOM file generated in Pcbnew with `File / Fabrication Outputs / BOM file`
* Position file generated in Pcbnew with `File / Fabrication Outputs / Footprint Position (.pos) File`

Generate the position file with the following settings:

* Format: CSV
* Units: millimeters
* Files: Single file for board


## Usage

The command `python JLCfilter.py -h` will print a help message.

If you are in your KiCad project folder, this can be enough:

```
python JLCfilter.py . 
```

Or in another directory,

```
python JLCfilter.py path/to/files
```


The script tries to automatically determine your project name by looking for a `.kicad_pcb`
file in the directory. If that file doesn't exist or you have named the BOM and position 
files something else, you need to specify them:

```
python JLCfilter.py --bom my_BOM.csv --pos my_positions.csv
```

By default, the output files will be called `bom_to_fab.csv` and `pos_to_fab.csv`. 
You can change them with command line arguments:

```
python JLCfilter.py --bom my_BOM.csv --pos my_positions.csv --bom-output BOM_output.csv --pos-output pos_output.csv
```

The script will not overwrite existing output files, 
unless you give it the argument `--force`.
