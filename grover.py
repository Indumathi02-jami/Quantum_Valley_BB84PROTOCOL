from flask import Flask, render_template, request, jsonify
import numpy as np

app = Flask(__name__)

def grover_backend(n_qubits, secret_index, num_iterations):
    N = 2 ** n_qubits
    state = np.ones(N) / np.sqrt(N)   # uniform superposition
    probs_per_iter = []
    success_probs = []

    for it in range(num_iterations):
        state[secret_index] *= -1                     # Oracle
        mean = np.mean(state)                         # Diffusion
        state = 2 * mean - state
        state = state / np.linalg.norm(state)         # Normalize
        probs = np.abs(state) ** 2
        probs_per_iter.append(probs.tolist())
        success_probs.append(float(probs[secret_index]))

    return {
        "n_qubits": n_qubits,
        "N": N,
        "secret_index": secret_index,
        "iterations": num_iterations,
        "probs_per_iter": probs_per_iter,
        "success_probs": success_probs,
        "final_success": success_probs[-1] if success_probs else 0.0
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/simulate", methods=["POST"])
def simulate():
    data = request.json
    try:
        n_qubits = int(data.get("n_qubits", 3))
        secret_index = int(data.get("secret_index", 0))
        iterations = int(data.get("iterations", 1))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid inputs"}), 400

    if n_qubits < 1 or n_qubits > 10:
        return jsonify({"error": "n_qubits must be between 1 and 10"}), 400
    N = 2 ** n_qubits
    if secret_index < 0 or secret_index >= N:
        return jsonify({"error": f"secret_index must be between 0 and {N-1}"}), 400
    if iterations < 1 or iterations > 100:
        return jsonify({"error": "iterations must be between 1 and 100"}), 400

    result = grover_backend(n_qubits, secret_index, iterations)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
