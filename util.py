"""
Common definitions used throughout the project

exports:
    Bit (type) : element of F_2
    BooleanFunction (type) : function F_2^n -> F_2^d
    bitstrings_of_length (function) : get all bitstrings of given length
"""

from itertools import product
from typing import Iterable, Callable
from qiskit import QuantumRegister, QuantumCircuit

Bit = int # expected to be 0 or 1
BooleanFunction = Callable[[tuple[Bit]], tuple[Bit]]

def bitstrings_of_length(n : int) -> Iterable[tuple[Bit]]:
    """Returns an Iterator that produces all bitstrings of length `n`.
    """
    return product(*[(0,1) for _ in range(n)])

def toggle_address(circuit : QuantumCircuit, address_register : QuantumRegister, address : tuple[Bit]):
    """Apply X gates to every bit where the address is zero. 
    Every multi-controled gate after this says "If the address line is `address`, do the gate"
    """
    for idx, qbit in enumerate(address):
        if not qbit:
            circuit.x(address_register[idx])