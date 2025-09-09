import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit.primitives import BackendSamplerV2

# -------------------------
# Parameters
# -------------------------

rng = np.random.default_rng()
bit_num = 10

# -------------------------
# Alice inputs her bits and bases
# -------------------------
qc = QuantumCircuit(bit_num, bit_num)

# Alice's random bits and bases
abits = np.round(rng.random(bit_num)).astype(int)   # 0 or 1
abase = np.round(rng.random(bit_num)).astype(int)

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
# Simulate clean Aer
# -------------------------
sim = AerSimulator()
tqc = transpile(qc, sim)
result = sim.run(tqc, shots=1).result()
counts = result.get_counts()
measured_str = list(counts.keys())[0]
bob_bits_clean = [int(bit) for bit in measured_str[::-1]]  # reverse for little-endian
print("\nBob's measured bits (clean simulator):", bob_bits_clean)

# Sifted key (clean)
sifted_alice_clean = []
sifted_bob_clean = []

for i in range(bit_num):
    if abase[i] == bbase[i]:
        sifted_alice_clean.append(int(abits[i]))   # ensure plain int
        sifted_bob_clean.append(int(bob_bits_clean[i]))

# Print as lists
print("Sifted Alice's bits:", sifted_alice_clean)
print("Sifted Bob's bits:  ", sifted_bob_clean)

# -------------------------
# Print quantum circuit
# -------------------------
print("\nQuantum circuit:")
print(qc.draw(output='text'))

# -------------------------
# Connect to IBM Quantum with API key
# -------------------------
service = QiskitRuntimeService(
    channel="ibm_cloud",
    token="1YGtJioY2aFi8rMOG_3FPc9jUmEsj4UuY2qQb9dZNDyM"
)

# Try using a real backend (if accessible), else fallback
try:
    backend = service.backend("ibm_brisbane")
except Exception:
    backend = service.backend("ibmq_qasm_simulator")

print("\nConnected to backend:", backend.name)

# Load the backend sampler
from qiskit.primitives import BackendSamplerV2
 
# Load the Aer simulator and generate a noise model based on the currently-selected backend.
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
 
# Load the qiskit runtime sampler
from qiskit_ibm_runtime import SamplerV2 as Sampler
 
 
noise_model = NoiseModel.from_backend(backend)
 
# Define a simulator using Aer, and use it in Sampler.
backend_sim = AerSimulator(noise_model=noise_model)
sampler_sim = BackendSamplerV2(backend=backend_sim)

# Qiskit patterns step 2: Transpile
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
 
target = backend.target
pm = generate_preset_pass_manager(target=target, optimization_level=3)
qc_isa = pm.run(qc)

#step 3

# This required 5 s to run on ibm_torino on 10-28-24
sampler = Sampler(mode=backend)
job = sampler.run([qc_isa], shots=1)
# job = sampler_sim.run([qc], shots = 1)
counts = job.result()[0].data.c.get_counts()
countsint = job.result()[0].data.c.get_int_counts()

#step 4
# Get an array of bits
 
keys = counts.keys()
key = list(keys)[0]
bmeas = list(key)
bmeas_ints = []
for n in range(bit_num):
    bmeas_ints.append(int(bmeas[n]))
 
# Reverse the order to match our input. See "little endian" notation.
 
bbits = bmeas_ints[::-1]
 
print(bbits)

#step 4 .1

# QKD step 3: Public discussion of bases
 
agoodbits = []
bgoodbits = []
match_count = 0
for n in range(bit_num):
    # Check whether bases matched.
    if abase[n] == bbase[n]:
        agoodbits.append(int(abits[n]))
        bgoodbits.append(bbits[n])
        # If bits match when bases matched, increase count of matching bits
        if int(abits[n]) == bbits[n]:
            match_count += 1
 
print(agoodbits)
print(bgoodbits)
print("fidelity = ", match_count / len(agoodbits))
print("loss = ", 1 - match_count / len(agoodbits))