import streamlit as st
import json
import random
from math import gcd

# --- RSA Helpers ---
def mod_pow(base, exp, mod):
    result = 1
    b = base % mod
    e = exp
    while e > 0:
        if e & 1:
            result = (result * b) % mod
        b = (b * b) % mod
        e >>= 1
    return result

def egcd(a, b):
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = egcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)

def mod_inv(a, m):
    g, x = egcd(a, m)[:2]
    if g != 1:
        raise Exception("No modular inverse")
    return (x % m + m) % m

def rsa_encrypt(m, e, N):
    return mod_pow(m, e, N)

def rsa_decrypt(c, d, N):
    return mod_pow(c, d, N)

# --- Shor (simulated factoring) ---
def factorize_n(N):
    for i in range(2, int(N**0.5)+1):
        if N % i == 0:
            return i, N//i
    return None, None

# --- UI ---
st.set_page_config(page_title="Shor Simulator — Quantum Attack on RSA", layout="wide")

st.title("🔐 Shor Simulator — Quantum Attack on RSA")

# Sidebar controls
st.sidebar.header("⚙️ Controls")
plaintext = st.sidebar.number_input("Enter plaintext (< N)", min_value=1, value=42)
generate = st.sidebar.button("Generate RSA Keys")
run_attack = st.sidebar.button("Run Shor Attack")

# App state (using session_state)
if "N" not in st.session_state:
    st.session_state.e = 17
    st.session_state.N = None
    st.session_state.d = None
    st.session_state.ciphertext = None
    st.session_state.p = None
    st.session_state.q = None
    st.session_state.recovered_d = None
    st.session_state.eve_plain = None
    st.session_state.logs = []

# Generate RSA Keys
if generate:
    small_primes = [61, 53, 47, 59, 67]
    p = random.choice(small_primes)
    q = random.choice([x for x in small_primes if x != p])
    N = p * q
    phi = (p - 1) * (q - 1)
    d = mod_inv(st.session_state.e, phi)

    st.session_state.N = N
    st.session_state.d = d
    st.session_state.p = None
    st.session_state.q = None
    st.session_state.recovered_d = None
    st.session_state.eve_plain = None
    st.session_state.logs = [f"Generated RSA keys: N={N}, e={st.session_state.e}, d={d}"]

    st.session_state.ciphertext = rsa_encrypt(plaintext, st.session_state.e, N)

# Display RSA workflow
st.subheader("1️⃣ RSA Workflow: Alice → Bob")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Alice's Message (Plaintext)**")
    st.info(str(plaintext))

with col2:
    st.markdown("**Locked Message (Ciphertext)**")
    st.warning(str(st.session_state.ciphertext) if st.session_state.ciphertext else "—")

with col3:
    st.markdown("**Bob's Decryption**")
    if st.session_state.N:
        bob_plain = rsa_decrypt(st.session_state.ciphertext, st.session_state.d, st.session_state.N)
        st.success(str(bob_plain))
    else:
        st.write("—")

# Run Shor Attack
if run_attack and st.session_state.N:
    st.session_state.logs.append("Eve intercepts the ciphertext...")
    with st.spinner("Running Shor's Algorithm (simulated)..."):
        p, q = factorize_n(st.session_state.N)
        st.session_state.p, st.session_state.q = p, q
        st.session_state.logs.append(f"Eve discovered primes: {p} × {q}")

        phi = (p - 1) * (q - 1)
        st.session_state.recovered_d = mod_inv(st.session_state.e, phi)
        st.session_state.logs.append(f"Eve recovered secret key d={st.session_state.recovered_d}")

        st.session_state.eve_plain = rsa_decrypt(st.session_state.ciphertext, st.session_state.recovered_d, st.session_state.N)
        st.session_state.logs.append(f"Eve unlocked the message: {st.session_state.eve_plain}")

# Show attack explanation visually
if st.session_state.p:
    st.subheader("2️⃣ Shor's Attack — Step by Step")

    steps = [
        ("🔒", f"Alice locks the message with RSA: {plaintext} → {st.session_state.ciphertext}"),
        ("📡", "Ciphertext travels over the wire..."),
        ("🧑‍🔬", f"Eve runs Shor’s Algorithm to factor N={st.session_state.N}"),
        ("🧮", f"Eve found the secret primes: {st.session_state.p} × {st.session_state.q}"),
        ("🔑", f"Eve calculated the private key d={st.session_state.recovered_d}"),
        ("📖", f"Eve unlocked the message: {st.session_state.eve_plain}")
    ]

    for icon, text in steps:
        st.markdown(f"{icon} {text}")

# Export JSON
if st.session_state.N:
    export_data = {
        "N": st.session_state.N,
        "e": st.session_state.e,
        "plaintext": plaintext,
        "ciphertext": st.session_state.ciphertext,
        "p": st.session_state.p,
        "q": st.session_state.q,
        "recovered_d": st.session_state.recovered_d,
        "recovered_plaintext": st.session_state.eve_plain,
        "logs": st.session_state.logs
    }

    st.download_button(
        label="📥 Export Simulation as JSON",
        data=json.dumps(export_data, indent=2),
        file_name="shor_simulation.json",
        mime="application/json"
    )

# Technical log
if st.session_state.logs:
    with st.expander("📝 Technical Log"):
        for log in st.session_state.logs:
            st.text(log)
