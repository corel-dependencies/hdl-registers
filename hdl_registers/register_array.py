# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the hdl_registers project.
# https://hdl-registers.com
# https://gitlab.com/tsfpga/hdl_registers
# --------------------------------------------------------------------------------------------------

from .register import Register


class RegisterArray:

    """
    Represent an array of registers. That is, a sequence of registers that shall be repeated a
    number of times in a register list.
    """

    def __init__(self, name, base_index, length, description, atomic=None):
        """
        Arguments:
            name (str): The name of this register array.
            base_index (int): The zero-based index of the first register of this array in
                the register list.
            length (int): The number of times the register sequence shall be repeated.
            description (str): Textual register array description.
            atomic (str): Atomic read/write specification.
                In the following the register array is described as a 2D
                structure having a number of rows equal to length and a number
                of columns equal to the number of appended registers.

                None: no additional logic added.  Each read/write transaction
                reads/writes a register.
                'row': the addresses in each row are marked for atomic
                read/write.  The total number of atomic areas is equal to
                length.
                'all': the addresses in the whole register array are marked for
                atomic read/write.  This creates one atomic area.

                For each atomic area the generated logic depends on the
                registers type.  In any case the bus is expected to access the
                area from the lowest address to the highest address.
                'r' : reading at the first address of the area latches all the
                values provided by fabric to an internal buffer.  Reading at any
                other address of the area will access those latched values.
                'w' : all write operations will write data in an internal buffer
                that is not connected to fabric.  Writing at the last address of
                the area transfers all those values to another buffer connected
                to fabric.
                'r_w': write behavior as in 'w'.  Read will directly access the
                values in the buffer connected to fabric.
                'wpulse' : behaviour as in 'w' but the buffer connected to
                fabric is zero-cleared after one clock cycle.  The written
                values are available to fabric for one clock cycle.
                'r_wpulse': read behavior as in 'r'.  Write bevahior as in
                'wpulse'.
        """
        if atomic not in (None, "row", "all"):
            raise ValueError('atomic must be None or "entry" or "all"')
        self.atomic = atomic

        self.name = name
        self.base_index = base_index
        self.length = length
        self.description = description

        self.registers = []

    def append_register(self, name, mode, description):
        """
        Append a register to this array.

        Arguments:
            name (str): The name of the register.
            mode (str): A valid register mode.
            description (str): Textual register description.

        Return:
            :class:`.Register`: The register object that was created.
        """
        if self.registers:
            if self.atomic:
                if mode != self.registers[0].mode:
                    raise ValueError(
                        f"Cannot append register with mode {mode}.  All registers "
                        f"in the register array must have the same access modes "
                        f"if atomic={self.atomic}."
                    )

        index = len(self.registers)
        register = Register(name, index, mode, description)

        self.registers.append(register)
        return register

    def get_register(self, name):
        """
        Get a register from this array. Will raise exception if no register matches.

        Arguments:
            name (str): The name of the register.
        Return:
            :class:`.Register`: The register.
        """
        for register in self.registers:
            if register.name == name:
                return register

        raise ValueError(f'Could not find register "{name}" within register array "{self.name}"')

    @property
    def index(self):
        """
        Property exists to be used analogously with ``Register.index``.

        Return:
            int: The highest index occupied by this array.
        """
        return self.base_index + self.length * len(self.registers) - 1

    def get_start_index(self, array_index):
        """
        The index within the register list where array iteration number ``array_index`` starts.

        Arguments:
            array_index (int): The array iteration index.
                Shall be less than or equal to the array ``length``.
        """
        if array_index >= self.length:
            raise ValueError(
                f'Index {array_index} out of range for register array "{self.name}" '
                f"of length {self.length}."
            )

        return self.base_index + array_index * len(self.registers)

    def __repr__(self):
        return f"""{self.__class__.__name__}(\
name={self.name},\
base_index={self.base_index},\
length={self.length},\
description={self.description},\
atomic={self.atomic},\
registers={','.join([repr(register) for register in self.registers])},\
)"""
