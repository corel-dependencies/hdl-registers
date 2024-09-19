from hdl_registers.enum import SequentialEnum, EnumType, EnumField
from hdl_registers.register import Register
from enum import IntEnum
import pytest


def test_sequential_enum():
    class Example(SequentialEnum):
        A = ()
        B = ()
        C = ()
        D = ()

    assert Example.A.value == 0
    assert Example.B.value == 1
    assert Example.C.value == 2
    assert Example.D.value == 3

    enum_type = EnumType(Example)
    assert enum_type.is_sequential


# noinspection PyUnresolvedReferences
def test_sequential_enum_functional_api():
    example = SequentialEnum("Example", "A B C D")

    assert example.A.value == 0
    assert example.B.value == 1
    assert example.C.value == 2
    assert example.D.value == 3


class ExampleEnum(IntEnum):
    A = 2
    B = 3
    C = 6
    D = 12


def test_enum_type():
    enum_type = EnumType(ExampleEnum)
    width = enum_type.expected_bit_width
    assert not enum_type.is_sequential
    assert width == 2
    assert enum_type.min_value(enum_type.expected_bit_width) == 2
    assert enum_type.max_value(enum_type.expected_bit_width) == 12

    assert enum_type.convert_from_unsigned_binary(
        bit_width=width, unsigned_binary=0
    ) == ExampleEnum.A

    assert enum_type.convert_from_unsigned_binary(
        bit_width=width, unsigned_binary=1
    ) == ExampleEnum.B

    assert enum_type.convert_from_unsigned_binary(
        bit_width=width, unsigned_binary=2
    ) == ExampleEnum.C

    assert enum_type.convert_from_unsigned_binary(
        bit_width=width, unsigned_binary=3
    ) == ExampleEnum.D

    with pytest.raises(ValueError):
        enum_type.convert_from_unsigned_binary(
            bit_width=width, unsigned_binary=4
        )

    assert enum_type.convert_to_unsigned_binary(
        bit_width=width, value=ExampleEnum.A
    ) == 0

    assert enum_type.convert_to_unsigned_binary(
        bit_width=width, value=ExampleEnum.B
    ) == 1

    assert enum_type.convert_to_unsigned_binary(
        bit_width=width, value=ExampleEnum.C
    ) == 2

    assert enum_type.convert_to_unsigned_binary(
        bit_width=width, value=ExampleEnum.D
    ) == 3

    other_enum = IntEnum("other", "A B C")
    with pytest.raises(ValueError):
        enum_type.convert_to_unsigned_binary(
            bit_width=width, value=other_enum.A
        )

    # Want the ability to set register via float for testing
    # noinspection PyTypeChecker
    assert enum_type.convert_from_unsigned_binary(
        bit_width=width,
        unsigned_binary=enum_type.convert_to_unsigned_binary(
            bit_width=width, value=5.7
        )
    ) == ExampleEnum.C


def test_enum_field():
    enum_field = EnumField(
        name="a",
        base_index=2,
        description="b",
        enum=ExampleEnum,
        default_value=ExampleEnum.A,
    )
    assert enum_field.width == 2
    assert int(enum_field.default_value, 2) == 2


def test_append_enum():
    register = Register(name="r", index=0, mode="r", description="r")
    field = register.append_enum(
        name="a",
        description="b",
        enum=ExampleEnum,
        default_value=ExampleEnum.A
    )
    assert field.width == 2
    assert int(field.default_value, 2) == 2

    with pytest.raises(ValueError):
        for _ in range(32 // field.width):
            register.append_enum(
                name="a",
                description="b",
                enum=ExampleEnum,
                default_value=ExampleEnum.A
            )
