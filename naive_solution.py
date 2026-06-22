"""
This file implements the "straightforward but inefficient construction" that
was hinted at in the project description. 
There are `n` address qubits and `d` data qubits. We map |a>|0> to |a>|f(a)> 
where f(a) is the data at that address. 
We do this by checking if each of the 2^n addresses was given. For each, 
we use multi-controlled X gates to assign data to d if the specified 
address was found. 

exports:
    quantum_ROM: This function creates the quantum memory circuit from 
        - the number of address qubits
        - the number of data qubits
        - a boolean function


"""
from qiskit import QuantumCircuit, QuantumRegister
from util import Bit, BooleanFunction, bitstrings_of_length, toggle_address


def quantum_ROM(n : int, d : int, f : BooleanFunction, 
                barriers=False, address_name=None, data_name=None, **kwargs) -> QuantumCircuit:
    """Construct a quantum memory circuit from a boolean function
    Args:
        n (int): the number of address qubits
        d (int): the number of data qubits
        f (BooleanFunction): a function from F_2^n to F_2^d (tuples of ints to tuples of ints)

        barriers (boolean, default False): If True, draw barriers between each address in the circuit
        address_name (string): optional name of the address register
        data_name (string): optional name of data register
    """
    address_register = QuantumRegister(n, name=address_name)
    data_register = QuantumRegister(d, name=data_name)
    circuit = QuantumCircuit(address_register, data_register)

    for address in bitstrings_of_length(n):
        toggle_address(circuit, address_register, address)
        set_data(circuit, address_register, data_register, f(address))
        toggle_address(circuit, address_register, address) 
        if barriers and address != tuple(1 for _ in range(n)):
            # Separate each address by barriers if requested.
            circuit.barrier()
    
    return circuit

def set_data(circuit : QuantumCircuit, address_register : QuantumRegister, data_register : QuantumRegister, data : tuple[Bit]):
    """If the address line is |1111111> (n many 1s), set the data line to the given data"""
    for idx, qbit in enumerate(data):
        if qbit:
            circuit.mcx(address_register[:], data_register[idx])

if __name__ == '__main__':
    def f(address):
        return (address[0], int(address[0] ^ address[2]), int(address[0] and (address[1] or address[2])))
    
    # circ = quantum_ROM(3, 3, f, barriers=True, address_name='a', data_name='d')
    # import matplotlib.pyplot as plt
    # fig = circ.draw(output='mpl')
    # plt.show()
    for address in bitstrings_of_length(3):
        print(f"{address}: {f(address)},")
