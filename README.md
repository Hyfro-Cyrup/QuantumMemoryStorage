# Project Specifications
This project was completed during the Erdos Institute Quantum Computing Bootcamp in the Summer of 2026. Its requirements are as follows: 

> ### Mini-Project #8: Quantum ROM
>
> Write a Qiskit function that takes a Boolean function
>
> \[
 f : \mathbb{F}_2^n \to \mathbb{F}_2^d
 \]
>
> and outputs a circuit \(U\) such that
>
> \[
 U \lvert x \rangle_n \lvert 0 \rangle_d
 =
 \lvert x \rangle_n \lvert f(x) \rangle_d.
 \]
>
> The construction may use:
>
> - Any number of ancilla qubits,
> - Arbitrary controlled multi-qubit gates,
> - Qiskit's built-in Quantum Fourier Transform (QFT) and inverse QFT, if needed.
>
> **Deliverables**
>
> - Documentation describing the construction.
> - Working Qiskit code for arbitrary \(n\).
> - A demonstration for the case \(n = 3\).
>
> **Note:** This is intentionally open-ended. There are straightforward but inefficient constructions that are still educational, as well as more sophisticated approaches that achieve better performance.

# Submission Contents
Each file and function has docstrings describing it. There is also a walkthrough of the ideas presented in the notebook `demo.ipynb`
 - `naive_solution.py`: The indicated straightforward solution
 - `naive_plus.py`: Three small optimizations made to the naive solution, some based on a paper https://doi.org/10.48550/arXiv.2204.03097
 - `util.py`: Small common definitions shared across solutions
 - `demo.ipynb`: Demos of both the general and n=3 case. 