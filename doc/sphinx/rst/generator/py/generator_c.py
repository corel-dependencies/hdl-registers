# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project, a HDL register generator fast enough to run
# in real time.
# https://hdl-registers.com
# https://gitlab.com/hdl_registers/hdl_registers
# --------------------------------------------------------------------------------------------------

# Standard libraries
import sys
from pathlib import Path

# First party libraries
from hdl_registers.generator.c.header import CHeaderGenerator
from hdl_registers.parser import from_toml

THIS_DIR = Path(__file__).parent


def main(output_folder: Path):
    """
    Create register C artifacts from the TOML example file.
    """
    register_list = from_toml(
        module_name="example",
        toml_file=THIS_DIR.parent.parent / "user_guide" / "toml" / "toml_format.toml",
    )

    CHeaderGenerator(register_list=register_list, output_folder=output_folder).create()


if __name__ == "__main__":
    main(output_folder=Path(sys.argv[1]))