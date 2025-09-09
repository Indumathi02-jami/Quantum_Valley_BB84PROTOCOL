# Qiskit patterns step 1: Map your problem to quantum circuit
# Import some generic packages

import numpy as np
from qiskit import QuantumCircuit, Aer, transpile, assemble, execute

# Set up a random number generator and a quantum circuit.
bit_num = 20
rng = np.random.default_rng()
qc = QuantumCircuit(bit_num, bit_num)

# QKD step 1: Random bits and bases for Alice
abits = np.round(rng.random(bit_num))
abase = np.round(rng.random(bit_num))

# Alice's state preparation
for n in range(bit_num):
    if abits[n] == 0:
        if abase[n] == 1:
            qc.h(n)
    if abits[n] == 1:
        if abase[n] == 0:
            qc.x(n)
        if abase[n] == 1:
            qc.x(n)
            qc.h(n)

qc.barrier()

# QKD step 2: Random bases for Bob
bbase = np.round(rng.random(bit_num))

for m in range(bit_num):
    if bbase[m] == 1:
        qc.h(m)
    qc.measure(m, m)

# Print Alice's and Bob's setup
print("Alice's bits are ", abits)
print("Alice's bases are ", abase)
print("Bob's bases are ", bbase)

# Draw the circuit
qc.draw(output='mpl', style='clifford')

# Simulate Bob's measurement
sim = Aer.get_backend('qasm_simulator')
tqc = transpile(qc, sim)
qobj = assemble(tqc)
result = execute(qc, backend=sim, shots=1).result()
counts = result.get_counts()
measured_str = list(counts.keys())[0]  # e.g. '010101...'
bob_bits = [int(bit) for bit in measured_str[::-1]]  # reverse for little-endian

print("Bob's measured bits are ", bob_bits)

# Sifted key: keep only bits where Alice and Bob chose the same basis
sifted_alice = []
sifted_bob = []

for i in range(bit_num):
    if abase[i] == bbase[i]:
        sifted_alice.append(int(abits[i]))
        sifted_bob.append(bob_bits[i])

print("Sifted Alice's bits are ", sifted_alice)
print("Sifted Bob's bits are ", sifted_bob)
