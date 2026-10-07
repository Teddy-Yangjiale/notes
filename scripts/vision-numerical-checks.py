"""Independent checks of the numerical examples printed in the vision notes.

Only Python's standard library and tiny synthetic inputs are used.
This checks teaching arithmetic, not a real model's performance.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
checks = []


def close(actual, expected, tolerance=1e-9):
    assert abs(actual - expected) < tolerance, (actual, expected)


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]


def transpose(a):
    return [list(row) for row in zip(*a)]


def record(name, result):
    checks.append({"name": name, "result": result, "passed": True})


# Reconstruct the hand-derived SVD, rather than merely comparing a memorized answer.
u = [[1 / math.sqrt(5), -2 / math.sqrt(5)],
     [2 / math.sqrt(5), 1 / math.sqrt(5)]]
reconstruction = matmul(matmul(u, [[5, 0], [0, 0]]), transpose(u))
for row, target in zip(reconstruction, [[1, 2], [2, 4]]):
    for a, b in zip(row, target):
        close(a, b)
record("SVD reconstruction", reconstruction)

points = [[3, 1], [-1, 1], [1, 2], [1, 0]]
mean = [sum(row[j] for row in points) / len(points) for j in range(2)]
centered = [[row[j] - mean[j] for j in range(2)] for row in points]
cov = [[v / 3 for v in row] for row in matmul(transpose(centered), centered)]
close(cov[0][0], 8 / 3)
close(cov[1][1], 2 / 3)
close(cov[0][1], 0)
record("PCA covariance and retained variance", {"covariance": cov, "fraction": 0.8})

# Matrix loss derivative checked by perturbing each weight.
x = [[1, 2], [3, 4]]
w = [[1.0, 0.0], [0.0, 2.0]]
target = [[1, 1], [5, 5]]
def matrix_loss(weights):
    y = matmul(x, weights)
    return sum(0.5 * (y[i][j] + [1, -1][j] - target[i][j]) ** 2
               for i in range(2) for j in range(2))
expected = [[-2, 8], [-2, 12]]
for i in range(2):
    for j in range(2):
        plus, minus = [r.copy() for r in w], [r.copy() for r in w]
        plus[i][j] += 1e-5
        minus[i][j] -= 1e-5
        close((matrix_loss(plus) - matrix_loss(minus)) / 2e-5, expected[i][j], 1e-7)
close(matrix_loss(w), 5)
record("Matrix gradient finite differences", expected)

# Recompute the classifier's full first update independently of the article code.
data = [[1, 0], [0, 1], [-1, -1], [1, 1]]
labels = [0, 1, 2, 0]
weights = [[0.1, -0.1, 0], [-0.1, 0.1, 0]]
grad = [[0.0] * 3 for _ in range(2)]
bias_grad = [0.0] * 3
for row, label in zip(data, labels):
    scores = [sum(row[k] * weights[k][j] for k in range(2)) for j in range(3)]
    e = [math.exp(z - max(scores)) for z in scores]
    p = [v / sum(e) for v in e]
    for j in range(3):
        dz = (p[j] - int(j == label)) / len(data)
        bias_grad[j] += dz
        for k in range(2):
            grad[k][j] += row[k] * dz
rounded = [[round(v, 6) for v in row] for row in grad]
assert rounded == [[-0.408209, 0.075152, 0.333056],
                   [-0.174848, -0.158209, 0.333056]], rounded
training = (ROOT / "src/content/notes/vision-05-training/index.md").read_text(encoding="utf-8")
for row in rounded:
    assert "&".join(f"{v:.6f}" for v in row) in training
record("Printed first classifier update", {
    "gradient": rounded, "biasGradient": [round(v, 6) for v in bias_grad],
    "weightsAfter": [[round(weights[i][j] - 0.1 * grad[i][j], 6)
                      for j in range(3)] for i in range(2)],
})

p, q = [0.5, 0.5], [0.9, 0.1]
kl_pq = sum(a * math.log(a / b) for a, b in zip(p, q))
kl_qp = sum(b * math.log(b / a) for a, b in zip(p, q))
close(kl_pq, 0.5108256237659907)
close(kl_qp, 0.3680642071684971)
record("KL directions", [kl_pq, kl_qp])

posterior = 0.01 * 0.9 / (0.01 * 0.9 + 0.99 * 0.05)
close(posterior, 9 / 58.5)
record("Bayes defect posterior", posterior)

# LN's derivative includes dependencies through both mean and variance.
values, upstream, eps = [1.0, 3.0], [1.0, 0.0], 1e-5
mu = sum(values) / len(values)
variance = sum((v - mu) ** 2 for v in values) / len(values)
scale = math.sqrt(variance + eps)
normalized = [(v - mu) / scale for v in values]
mean_g = sum(upstream) / len(upstream)
mean_gx = sum(g * v for g, v in zip(upstream, normalized)) / len(values)
analytic = [(g - mean_g - v * mean_gx) / scale
            for g, v in zip(upstream, normalized)]
def ln_objective(row):
    m = sum(row) / len(row)
    s = math.sqrt(sum((v - m) ** 2 for v in row) / len(row) + eps)
    return sum(g * (v - m) / s for g, v in zip(upstream, row))
for k in range(2):
    plus, minus = values.copy(), values.copy()
    plus[k] += 1e-4
    minus[k] -= 1e-4
    close((ln_objective(plus) - ln_objective(minus)) / 2e-4, analytic[k], 1e-8)
record("LayerNorm finite differences with epsilon", analytic)

adam_second = 0.1 * (0.28 / 0.19) / math.sqrt(0.004996 / 0.001999)
close(adam_second, 0.09321796388114091)
record("Adam second update", adam_second)

new_prediction = 1.94 * (0.94 - 1.12 * 2 + 2.94) - 0.03
new_loss = 0.5 * (new_prediction - 1) ** 2
close(new_prediction, 3.1516)
close(new_loss, 2.31469128)
record("Two-layer network after SGD", {"prediction": new_prediction, "loss": new_loss})

close((1 - 0.5) * ((1 - 0.25) * 0 + 0.25 * 10)
      + 0.5 * ((1 - 0.25) * 20 + 0.25 * 30), 12.5)
assert (2 * (350 - 200), 2 * (220 - 100)) == (300, 240)
assert (500 * 1 / 5 + 320, 500 * 0.5 / 5 + 240) == (420, 290)
record("Bilinear, crop coordinates and pinhole", {
    "bilinear": 12.5, "cropPoint": [300, 240], "pinholePoint": [420, 290],
})

print(json.dumps({"checks": checks, "total": len(checks), "passed": True},
                 ensure_ascii=False, indent=2))
