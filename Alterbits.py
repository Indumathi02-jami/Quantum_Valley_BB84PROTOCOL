import random
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# Number of qubits (key length)
n = 16  

# Alice prepares random bits and bases
alice_bits = [random.randint(0, 1) for _ in range(n)]
alice_bases = [random.randint(0, 1) for _ in range(n)]  # 0 = Z-basis, 1 = X-basis

# Eve measures alternate bits (0, 2, 4, ...)
eve_bases = [random.randint(0, 1) if i % 2 == 0 else None for i in range(n)]

# Bob chooses random bases
bob_bases = [random.randint(0, 1) for _ in range(n)]

# Quantum circuit
qc = QuantumCircuit(n, n)

# Step 1: Alice encodes bits
for i in range(n):
    if alice_bits[i] == 1:
        qc.x(i)
    if alice_bases[i] == 1:
        qc.h(i)

# Step 2: Eve intercepts alternate bits
for i in range(n):
    if eve_bases[i] is not None:  
        if eve_bases[i] == 1:
            qc.h(i)
        qc.measure(i, i)
        qc.reset(i)
        if random.randint(0, 1) == 1:
            qc.x(i)
        if alice_bases[i] == 1:
            qc.h(i)

# Step 3: Bob measures
for i in range(n):
    if bob_bases[i] == 1:
        qc.h(i)
    qc.measure(i, i)

# Run the circuit once
sim = AerSimulator()
result = sim.run(qc, shots=1).result()
bob_results = list(result.get_counts().keys())[0]  
bob_bits = [int(b) for b in bob_results[::-1]]

# Step 4: Find matching bases and generate sifted key if QBER ≤ 11%
matching_indices = []
sifted_alice = []
sifted_bob = []

for i in range(n):
    if alice_bases[i] == bob_bases[i]:
        matching_indices.append(i)
        sifted_alice.append(alice_bits[i])
        sifted_bob.append(bob_bits[i])

# Step 5: QBER calculation
errors = sum(1 for a, b in zip(sifted_alice, sifted_bob) if a != b)
qber = (errors / len(sifted_alice)) * 100 if len(sifted_alice) > 0 else 0

SECURITY_THRESHOLD = 11

# --- OUTPUT ---
print("Alice bits : ", alice_bits)
print("Alice bases: ", alice_bases)
print("Eve bases  : ", eve_bases)
print("Bob bases  : ", bob_bases)
print("Bob bits   : ", bob_bits)

print(f"\nMatching bases indices: {matching_indices}")
print(f"Number of matched bases: {len(matching_indices)}")
print(f"Error rate (QBER): {qber:.2f}%")

if qber > SECURITY_THRESHOLD:
    print("🚨 Eve detected! Communication aborted — no sifted key generated.")
else:
    print("✅ Communication secure (QBER ≤ 11%).")
    print("Sifted Alice key:", sifted_alice)
    print("Sifted Bob key  :", sifted_bob)
