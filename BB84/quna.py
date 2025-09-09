import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# -------------------------
# Step 1: Alice prepares qubits
# -------------------------
rng = np.random.default_rng()
bit_num = 20

qc = QuantumCircuit(bit_num, bit_num)

# Alice's random bits and bases
abits = np.round(rng.random(bit_num)).astype(int)   # 0 or 1
abase = np.round(rng.random(bit_num)).astype(int)   # 0=Z basis, 1=X basis

# Prepare Alice's states
for n in range(bit_num):
    if abits[n] == 0:
        if abase[n] == 1:   # |+>
            qc.h(n)
    if abits[n] == 1:
        if abase[n] == 0:   # |1>
            qc.x(n)
        if abase[n] == 1:   # |->
            qc.x(n)
            qc.h(n)

qc.barrier()

# -------------------------
# Step 2: Bob chooses bases and measures
# -------------------------
bbase = np.round(rng.random(bit_num)).astype(int)

for m in range(bit_num):
    if bbase[m] == 1:   # X basis → apply H before measure
        qc.h(m)
    qc.measure(m, m)

# -------------------------
# Step 3: Run simulation
# -------------------------
sim = AerSimulator()
result = sim.run(qc).result()
counts = result.get_counts()

# Simulator outputs counts of all possible bitstrings,
# we only need one sample since this is a projective measurement
bob_raw = list(counts.keys())[0]
bob_raw = bob_raw[::-1]   # reverse bit order
bob_bits = np.array([int(b) for b in bob_raw])

# -------------------------
# Step 4: Sifting - keep only same bases
# -------------------------
sifted_alice = []
sifted_bob = []
for i in range(bit_num):
    if abase[i] == bbase[i]:   # keep only if bases match
        sifted_alice.append(abits[i])
        sifted_bob.append(bob_bits[i])

# -------------------------
# Display results
# -------------------------
print("Alice bits:  ", abits)
print("Alice bases: ", abase)
print("Bob bases:   ", bbase)
print("Bob bits:    ", bob_bits)
print("\nSifted Alice key:", sifted_alice)
print("Sifted Bob key:  ", sifted_bob)
