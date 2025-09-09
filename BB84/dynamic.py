import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import QiskitRuntimeService

# -------------------------
# Parameters
# -------------------------
bit_num = 5  # Number of qubits (small for testing)
qc = QuantumCircuit(bit_num, bit_num)

# -------------------------
# Alice inputs her bits and bases
# -------------------------
abits = []
abase = []

print("Enter Alice's bits (0 or 1):")
for i in range(bit_num):
    b = int(input(f"Bit {i}: "))
    abits.append(b)

print("\nEnter Alice's bases (0=Z, 1=X):")
for i in range(bit_num):
    b = int(input(f"Basis {i}: "))
    abase.append(b)

# -------------------------
# Alice prepares qubits
# -------------------------
for n in range(bit_num):
    if abits[n] == 0 and abase[n] == 1:
        qc.h(n)
    if abits[n] == 1:
        if abase[n] == 0:
            qc.x(n)
        if abase[n] == 1:
            qc.x(n)
            qc.h(n)

qc.barrier()

# -------------------------
# Bob's random bases and measurement
# -------------------------
bbase = np.round(np.random.random(bit_num))
for m in range(bit_num):
    if bbase[m] == 1:
        qc.h(m)
    qc.measure(m, m)

# -------------------------
# Print Alice & Bob setup
# -------------------------
print("\nAlice's bits are", abits)
print("Alice's bases are", abase)
print("Bob's bases are", bbase)

# -------------------------
# Simulate Bob's measurement
# -------------------------
sim = AerSimulator()
tqc = transpile(qc, sim)
result = sim.run(tqc, shots=1).result()
counts = result.get_counts()
measured_str = list(counts.keys())[0]
bob_bits = [int(bit) for bit in measured_str[::-1]]  # reverse for little-endian

print("Bob's measured bits are", bob_bits)

# -------------------------
# Sifted key: only keep matching bases
# -------------------------
sifted_alice = []
sifted_bob = []
for i in range(bit_num):
    if abase[i] == bbase[i]:
        sifted_alice.append(abits[i])
        sifted_bob.append(bob_bits[i])

print("Sifted Alice's bits are", sifted_alice)
print("Sifted Bob's bits are", sifted_bob)

# -------------------------
# Print the quantum circuit
# -------------------------
print("\nQuantum circuit:")
print(qc.draw(output='text'))

# -------------------------
# Connect to IBM Quantum with API key
# -------------------------
service = QiskitRuntimeService(
    channel="ibm_cloud",
    token="1YGtJioY2aFi8rMOG_3FPc9jUmEsj4UuY2qQb9dZNDyM"  # 👈 your API key
)

# Try using a real backend (if you have access), else fallback to simulator
try:
    backend = service.backend("ibm_brisbane")
except Exception:
    backend = service.backend("ibmq_qasm_simulator")

print("\nConnected to backend:", backend.name)

