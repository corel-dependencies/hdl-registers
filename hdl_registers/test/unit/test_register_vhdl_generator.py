# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project.
# https://hdl-registers.com
# https://gitlab.com/tsfpga/hdl_registers
# --------------------------------------------------------------------------------------------------

"""
Some limited unit tests that check the generated code.

It is also functionally tested in the file tb_artyz.vhd.
That testbench compiles the VHDL package and performs some run-time assertions on the
generated values. That test is considered more meaningful and exhaustive than a unit test would be.
"""

import pytest
from enum import IntEnum

import tsfpga
from tsfpga.system_utils import read_file

from hdl_registers.parser import from_toml
from hdl_registers.register_field_type import Unsigned, Signed, SignedFixedPoint, UnsignedFixedPoint
from hdl_registers.enum import SequentialEnum
from hdl_registers.register_list import RegisterList


class RegisterConfiguration:
    def __init__(self, module_name, source_toml_file):
        self.register_list = from_toml(module_name, source_toml_file)
        self.register_list.add_constant("dummy_constant", "3")
        self.register_list.add_constant("flappy_constant", "91")

    def test_vhdl_package(self, output_path, test_registers, test_constants):
        self.register_list.create_vhdl_package(output_path)
        vhdl = read_file(output_path / "artyz7_regs_pkg.vhd")

        if test_registers:
            assert "constant artyz7_reg_map : " in vhdl, vhdl
        else:
            assert "constant artyz7_reg_map : " not in vhdl, vhdl

        if test_constants:
            assert "constant artyz7_constant_dummy_constant : integer := 3;" in vhdl, vhdl
        else:
            assert "constant artyz7_constant_dummy_constant : integer := 3;" not in vhdl, vhdl


@pytest.fixture
def register_configuration():
    return RegisterConfiguration(
        "artyz7", tsfpga.TSFPGA_EXAMPLE_MODULES / "artyz7" / "regs_artyz7.toml"
    )


# False positive for pytest fixtures
# pylint: disable=redefined-outer-name


def test_vhdl_package_with_registers_and_constants(tmp_path, register_configuration):
    register_configuration.test_vhdl_package(tmp_path, test_registers=True, test_constants=True)


def test_vhdl_package_with_registers_and_no_constants(tmp_path, register_configuration):
    register_configuration.register_list.constants = []
    register_configuration.test_vhdl_package(tmp_path, test_registers=True, test_constants=False)


def test_vhdl_package_with_constants_and_no_registers(tmp_path, register_configuration):
    register_configuration.register_list.register_objects = []
    register_configuration.test_vhdl_package(tmp_path, test_registers=False, test_constants=True)


def test_vhdl_package_with_only_one_register(tmp_path):
    """
    Test that reg_map constant has valid VHDL syntax even when there is only one register.
    """
    register_list = RegisterList(name="apa", source_definition_file=None)
    register_list.append_register(name="hest", mode="r", description="a single register")
    register_list.create_vhdl_package(tmp_path)
    vhdl = read_file(tmp_path / "apa_regs_pkg.vhd")

    expected = """
  constant apa_reg_map : reg_definition_vec_t(apa_reg_range) := (
    0 => (idx => apa_hest, reg_type => r)
  );

  constant apa_regs_init : apa_regs_t := (
    0 => "00000000000000000000000000000000"
  );
"""
    assert expected in vhdl, vhdl


def test_vhdl_typedef(tmp_path):
    register_list = RegisterList(name="artyz7", source_definition_file=None)
    number = register_list.append_register("number", "r_w", "")
    number.append_bit_vector("udata0", "expected unsigned(1 downto 0)", 2, "11", Unsigned())
    number.append_bit_vector("sdata0", "expected signed(1 downto 0)", 2, "11", Signed())
    number.append_bit_vector(
        "ufixed0", "expected ufixed(1 downto 0)", 2, "11", UnsignedFixedPoint(-1, -2)
    )
    number.append_bit_vector(
        "ufixed1", "expected ufixed(5 downto -2)", 8, "1" * 8, UnsignedFixedPoint(5, -2)
    )
    number.append_bit_vector(
        "ufixed1", "expected ufixed(5 downto -2)", 8, "1" * 8, UnsignedFixedPoint(5, -2)
    )
    number.append_bit_vector(
        "sfixed0", "expected sfixed(-1 downto -2)", 2, "11", SignedFixedPoint(-1, -2)
    )
    number.append_bit_vector(
        "sfixed0", "expected sfixed(5 downto 0)", 6, "1" * 6, SignedFixedPoint(5, 0)
    )

    register_list.create_vhdl_package(tmp_path)
    vhdl = read_file(tmp_path / "artyz7_regs_pkg.vhd")

    assert "subtype artyz7_number_udata0_t is unsigned(1 downto 0);" in vhdl, vhdl
    assert "subtype artyz7_number_sdata0_t is signed(1 downto 0);" in vhdl, vhdl
    assert "subtype artyz7_number_ufixed0_t is ufixed(-1 downto -2);" in vhdl, vhdl
    assert "subtype artyz7_number_ufixed1_t is ufixed(5 downto -2);" in vhdl, vhdl
    assert "subtype artyz7_number_sfixed0_t is sfixed(-1 downto -2);" in vhdl, vhdl
    assert "subtype artyz7_number_sfixed0_t is sfixed(5 downto 0);" in vhdl, vhdl


class ExampleSequentialEnum(SequentialEnum):
    A = ()
    B = ()
    C = ()


class ExampleUserEnum(IntEnum):
    A = 2
    B = 3
    C = 6
    D = 12


def test_vhdl_enum_types(tmp_path):
    register_list = RegisterList(name="artyz7", source_definition_file=None)
    register = register_list.append_register("enums", "r_w", "")
    register.append_enum(
        name="sequential",
        description="",
        enum=ExampleSequentialEnum,
        default_value=ExampleSequentialEnum.A
    )
    register.append_enum(
        name="user",
        description="",
        enum=ExampleUserEnum,
        default_value=ExampleSequentialEnum.A
    )

    register_list.create_vhdl_package(tmp_path)
    vhdl = read_file(tmp_path / "artyz7_regs_pkg.vhd")

    assert "subtype artyz7_enums_sequential is natural range 1 downto 0;" in vhdl, vhdl
    assert "constant artyz7_enums_sequential_width : positive := 2;" in vhdl, vhdl
    assert "subtype artyz7_enums_user is natural range 3 downto 2;" in vhdl, vhdl
    assert "constant artyz7_enums_user_width : positive := 2;" in vhdl, vhdl
    assert "type artyz7_enums_sequential_t is (A, B, C);" in vhdl, vhdl
    assert "type artyz7_enums_sequential_vector_t is array(artyz7_enums_sequential_t) of integer;" in vhdl, vhdl
    assert """function artyz7_enums_sequential_down (
    reg : std_ulogic_vector(31 downto 0))
    return artyz7_enums_sequential_t;""" in vhdl, vhdl
    assert """function artyz7_enums_sequential_up (
    value : artyz7_enums_sequential_t)
    return std_ulogic_vector;""" in vhdl, vhdl
    assert "type artyz7_enums_user_t is (A, B, C, D);" in vhdl, vhdl
    assert "type artyz7_enums_user_vector_t is array(artyz7_enums_user_t) of integer;" in vhdl, vhdl
    assert "constant artyz7_enums_user_c : artyz7_enums_user_vector_t := (2, 3, 6, 12);" in vhdl, vhdl
    assert """function artyz7_enums_user_down (
    reg : std_ulogic_vector(31 downto 0))
    return artyz7_enums_user_t;""" in vhdl, vhdl
    assert """function artyz7_enums_user_up (
    value : artyz7_enums_user_t)
    return std_ulogic_vector;""" in vhdl, vhdl

    assert """function artyz7_enums_sequential_down (
    reg : std_ulogic_vector(31 downto 0))
    return artyz7_enums_sequential_t is
  begin
    return artyz7_enums_sequential_t'val(to_integer(unsigned(reg(artyz7_enums_sequential))));
  end function;""" in vhdl, vhdl

    assert """function artyz7_enums_sequential_up (
    value : artyz7_enums_sequential_t)
    return std_ulogic_vector is
  begin
    return std_ulogic_vector(to_unsigned(artyz7_enums_sequential_t'pos(value), artyz7_enums_sequential_width));
  end function;""" in vhdl, vhdl

    assert """function artyz7_enums_user_down (
    reg : std_ulogic_vector(31 downto 0))
    return artyz7_enums_user_t is
  begin
    return artyz7_enums_user_t'val(to_integer(unsigned(reg(artyz7_enums_user))));
  end function;""" in vhdl, vhdl

    assert """function artyz7_enums_user_up (
    value : artyz7_enums_user_t)
    return std_ulogic_vector is
  begin
    return std_ulogic_vector(to_unsigned(artyz7_enums_user_t'pos(value), artyz7_enums_user_width));
  end function""" in vhdl, vhdl
