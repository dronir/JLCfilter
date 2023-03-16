import pandas as pd
import argparse

from pathlib import Path
from os import getcwd
from functools import cache
from sys import exit
from enum import Enum
from typing import Optional, List, Dict, Tuple


DESC = """Convert BOM and position files from KiCad Pcbnew to format desired by JLCPCB.

The BOM filename defaults to '[project].csv' and the position filename defaults
to '[project]-all-pos.csv', where 'project' is determined by looking for [project].kicad_pdb.
Use the command line arguments to change these if necessary.

"""


class FileType(str, Enum):
    POS = "pos"
    BOM = "BOM"


DELIMITER = {
    FileType.BOM: ";",
    FileType.POS: ",",
}


DEFAULT_FILENAME = {
    FileType.BOM: "{}.csv",
    FileType.POS: "{}-all-pos.csv",
}


COLUMN_FILTERS = {
    FileType.POS: ["Ref", "PosX", "PosY", "Side", "Rot"],
    FileType.BOM: ["Id", "Quantity", "Designator"],
}


JLCPCB_NAMES = {
    FileType.POS: {
        "Ref": "Designator",
        "PosX": "Mid X",
        "PosY": "Mid Y",
        "Side": "Layer",
        "Rot": "Rotation",
    },
    FileType.BOM: {
        "Designator": "Footprint",
        "Quantity": "Comment",
        "Id": "Designator"
    },
}


@cache
def find_projectfile(path: Path) -> Optional[str]:
    g = list(path.glob("*.kicad_pcb"))
    if len(g) == 1:
        print(f"Found {g[0]}.")
        return str(g[0]).split(".")[0]

    if len(g) > 1:
        print("Could not determine project name: Found multiple .kicad_pcb files.")
    else:
        print(f"Could not determine project name: No .kicad_pcb file found in {path}")
    return None


def autodetect_filename(style: FileType, path: Path) -> Optional[str]:
    maybe_project = find_projectfile(path)
    if maybe_project is None:
        return None
    out = DEFAULT_FILENAME[style].format(maybe_project)
    print(f"-> Guessing that {style} file is {out}.")
    return out


def process(data: pd.DataFrame, fields: List[str], rename_mapping: Dict[str, str]) -> pd.DataFrame:
    filtered = data[fields]
    return filtered.rename(rename_mapping, axis="columns", errors="raise")


def process_and_save(style: FileType, infile: str, overwrite: bool, outfile: str) -> None:
    if infile is None:
        print(f"No {style} filename given.")
        return
    try:
        data = pd.read_csv(infile, delimiter=DELIMITER[style])
        print(f"Opened {infile}.")
    except FileNotFoundError:
        print(f"File not found: {infile}")
        return

    processed = process(data, COLUMN_FILTERS[style], JLCPCB_NAMES[style])

    if Path(outfile).exists() and not overwrite:
        print(f"{outfile} exists already, use --force to overwrite!")
        return

    processed.to_csv(outfile, index=False)
    print(f"Wrote output to {outfile}.")


def main():

    parser = argparse.ArgumentParser(description=DESC)

    parser.add_argument(
        "--bom",
        metavar="BOM_file",
        help="BOM file from KiCad",
        default=argparse.SUPPRESS
    )
    parser.add_argument(
        "--pos",
        metavar="position_file",
        help="Position file from KiCad",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Overwrite output files if they exist",
    )
    parser.add_argument(
        "--bom-output",
        help="Name of BOM output file (default: bom_to_fab.csv)",
        default="bom_to_fab.csv",
    )
    parser.add_argument(
        "--pos-output",
        help="Name of position output file (default: pos_to_fab.csv)",
        default="pos_to_fab.csv",
    )
    parser.add_argument(
        "path",
        help="The directory to process",
        default="."
    )
    args = vars(parser.parse_args())

    path = Path(args["path"])

    if "bom" in args:
        bom_file = args["bom"]
    else:
        bom_file = autodetect_filename(FileType.BOM, path)

    if "pos" in args:
        pos_file = args["pos"]
    else:
        pos_file = autodetect_filename(FileType.POS, path)

    process_and_save(FileType.BOM, infile=bom_file, overwrite=args["force"], outfile=args["bom_output"])
    process_and_save(FileType.POS, infile=pos_file, overwrite=args["force"], outfile=args["pos_output"])


if __name__ == "__main__":
    main()
