"""
This file is a second iteration on the rudimentary solution presented in `naive-solution.py`.
The same ideas are present, just presented slightly more optimally. 

Primarily, that means using fewer multi-controlled X gates. We accomplish this two ways:
    1. One additional control line lets us only ask "Is this address the given address" twice,
    instead of every time we want to flip a bit in the data track. 
    2. 2^n additional ancillary qubits can reduce those two MCX gates per address to one. 
    If we store the result of "Is this address the given address" in its own qubit, then we never
    have to ask it again in order to clear the control line. 
    I'm less sure that this version is worth it. I don't know enough about the construction to say
    that qubits are easier to make that MCX gates. 

Both of those optimizations can be found in this paper from 2022: https://doi.org/10.48550/arXiv.2204.03097

Lastly, one more small optimization is made. The third version of quantum ROM in this file applies 
simplifying logic to optimization #1 above, reducing the number of X gates. 

exports: 
    quantum_ROM_1 : Optimization #1: Reduce MCX gates with one ancillary qubit
    quantum_ROM_2 : Optimization #2: Reduce MCX gates further with 2^n ancillary qubits
    quantum_ROM_3 : Optimization #1, simplified to reduce X gates
"""

from util import Bit, BooleanFunction, bitstrings_of_length, toggle_address
from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister

def quantum_ROM_1(n : int, d : int, f : BooleanFunction, 
                barriers=False, address_name=None, 
                control_name=None, data_name=None, **kwargs) -> QuantumCircuit:
    """Construct a quantum memory circuit from a boolean function

    Uses one ancillary qubit to reduce the number of MCX gates.

    Args:
        n (int): the number of address qubits
        d (int): the number of data qubits
        f (BooleanFunction): a function from F_2^n to F_2^d (tuples of ints to tuples of ints)

        barriers (boolean, default False): If True, draw barriers between each address in the circuit
        address_name (string): optional name of the address register
        control_name (string): optional name of the ancilla control register
        data_name (string): optional name of data register
    """
    address_register = QuantumRegister(n, name=address_name)
    control_register = AncillaRegister(1, name=control_name)
    data_register = QuantumRegister(d, name=data_name)
    circuit = QuantumCircuit(address_register, control_register, data_register)

    for address in bitstrings_of_length(n):
        toggle_address(circuit, address_register, address)
        circuit.mcx(address_register[:], control_register[0])

        set_data(circuit, control_register, data_register, f(address))

        circuit.mcx(address_register[:], control_register[0])
        toggle_address(circuit, address_register, address) 

        if barriers and address != tuple(1 for _ in range(n)):
            # Separate each address by barriers if requested.
            circuit.barrier()
    
    return circuit

def set_data(circuit : QuantumCircuit, control_register : AncillaRegister, data_register : QuantumRegister, data : tuple[Bit]):
    for idx, qbit in enumerate(data):
        if qbit:
            circuit.cx(control_register[0], data_register[idx])


def quantum_ROM_2(n : int, d : int, f : BooleanFunction, 
                barriers=False, address_name=None, 
                control_name=None, predecoding_name=None,
                data_name=None, **kwargs) -> QuantumCircuit:
    """Construct a quantum memory circuit from a boolean function

    Uses 2^n ancilla qubits for "predecoding". 
    This means each one stores whether a given address was found. 
    These never return to zero. You either reuse them when you need to ask 
    what that address line read again or they are garbage to you. 

    Args:
        n (int): the number of address qubits
        d (int): the number of data qubits
        f (BooleanFunction): a function from F_2^n to F_2^d (tuples of ints to tuples of ints)

        barriers (boolean, default False): If True, draw barriers between each address in the circuit
        address_name (string): optional name of the address register
        predecoding_name (string) : optional name of the predecoding ancilla register
        control_name (string): optional name of the ancilla control register
        data_name (string): optional name of data register
    """
    address_register = QuantumRegister(n, name=address_name)
    predecoding_register = AncillaRegister(2**n, name=predecoding_name)
    control_register = AncillaRegister(1, name=control_name)
    data_register = QuantumRegister(d, name=data_name)
    circuit = QuantumCircuit(address_register, predecoding_register, control_register, data_register)

    # pre-decoding section. Store whether each address was found in its associated predecoding qubit
    for idx, address in enumerate(bitstrings_of_length(n)):
        toggle_address(circuit, address_register, address)
        circuit.mcx(address_register[:], predecoding_register[idx])
        toggle_address(circuit, address_register, address) 

    if barriers:
        # Separate the predecoding section from the assignment section
        circuit.barrier()

    # data assignment section. For each predecoding qubit, load the data for its associated address
    for idx, address in enumerate(bitstrings_of_length(n)):
        if not any(f(address)):
            # go ahead and skip if the data is all zeroes
            continue

        circuit.cx(predecoding_register[idx], control_register[0])
        set_data(circuit, control_register, data_register, f(address))
        circuit.cx(predecoding_register[idx], control_register[0])
    
    return circuit

def quantum_ROM_3(n : int, d : int, f : BooleanFunction, 
                barriers=False, address_name=None, 
                control_name=None, data_name=None, **kwargs) -> QuantumCircuit:
    """Construct a quantum memory circuit from a boolean function

    Uses one ancillary qubit to reduce the number of MCX gates.
    Simplifies some unneeded X gates. 

    Args:
        n (int): the number of address qubits
        d (int): the number of data qubits
        f (BooleanFunction): a function from F_2^n to F_2^d (tuples of ints to tuples of ints)

        barriers (boolean, default False): If True, draw barriers between each address in the circuit
        address_name (string): optional name of the address register
        control_name (string): optional name of the ancilla control register
        data_name (string): optional name of data register
    """
    address_register = QuantumRegister(n, name=address_name)
    control_register = AncillaRegister(1, name=control_name)
    data_register = QuantumRegister(d, name=data_name)
    circuit = QuantumCircuit(address_register, control_register, data_register)

    # walk from 00000 to 11111 counting in binary, applying X wherever bits flip
    # would be fun to see if this is an optimal or near optimal path to take, i.e. uses the fewest X gates
    # We should start our walk with the |00000> state toggled. 
    prev = (1 << n) - 1
    for curr in range(1 << n):
        diff = curr ^ prev # bitwise XOR to see which bits flipped (which qubits to flip)
        # We need to toggle the address given by `curr` in binary.
        address = tuple(1 if (curr & (1 << idx)) else 0 for idx in range(n))
        if not any(f(address)):
            continue

        for idx in range(n):
            if diff & (1 << idx):
                # bitwise AND is truthy whenever the bit at this index was flipped
                circuit.x(address_register[idx])

        # The address is toggled. Load the data. 
        circuit.mcx(address_register[:], control_register[0])

        set_data(circuit, control_register, data_register, f(address))

        circuit.mcx(address_register[:], control_register[0])

        prev = curr

    
    return circuit

if __name__ == '__main__':
    def f(address):
        return (address[0], int(address[0] and address[1]), int(address[0] or (address[1] or address[2])))
    
    circ = quantum_ROM_3(3, 3, f, barriers=True, address_name='a', data_name='d')
    import matplotlib.pyplot as plt
    fig = circ.draw(output='mpl')
    plt.show()