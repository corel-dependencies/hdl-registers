from hdl_registers.bit_vector import BitVector
from hdl_registers.register_field_type import EnumType, enum_bit_width
from typing import Type
from enum import IntEnum


class SequentialEnum(IntEnum):
    """Like enum.auto but it starts from 0."""

    def __new__(cls, *args):
        value = len(cls.__members__)
        obj = int.__new__(cls, *args)
        obj._value_ = value
        return obj


class EnumField(BitVector):
    def __init__(
        self,
        name,
        base_index,
        description,
        enum: Type["IntEnum"],
        default_value: "IntEnum",
    ):
        width = enum_bit_width(enum)
        super().__init__(
            name=name,
            base_index=base_index,
            description=description,
            width=width,
            default_value=f"{default_value:0{width}b}",
            field_type=EnumType(enum),
        )
