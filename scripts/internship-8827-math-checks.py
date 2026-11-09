"""CPU-only checks for the 8827 lesson. No models, optimization runs or server access."""
import argparse
import json
from pathlib import Path
import numpy as np

p = argparse.ArgumentParser()
p.add_argument('--case', type=Path, required=True)
p.add_argument('--measurements', type=Path, required=True)
p.add_argument('--out', type=Path)
a = p.parse_args()
z = np.load(a.case)
m = json.loads(a.measurements.read_text(encoding='utf-8'))
samples = {s['name']: s for s in m['samples']}
checks = []

def check(name, actual, expected, atol=1e-6):
    actual, expected = np.asarray(actual), np.asarray(expected)
    err = float(np.max(np.abs(actual - expected)))
    ok = bool(np.allclose(actual, expected, atol=atol, rtol=1e-6))
    checks.append(dict(name=name, passed=ok, max_absolute_error=err))
    assert ok, (name, actual, expected)

def jac(fn, x, eps=1e-5):
    x = np.asarray(x, dtype=float)
    return np.stack([(np.asarray(fn(x + eps * e)) - np.asarray(fn(x - eps * e))) / (2 * eps)
                     for e in np.eye(x.size)], axis=-1)

K, R, C = z['K'], z['c2w'][:3,:3], z['c2w'][:3,3] - z['origin']
A, B = samples['A'], samples['B']
check('road A intersects z=0', A['local_mean'][2], 0)
xc = R.T @ (np.array(B['local_mean']) - C)
project = lambda x: (K @ x)[:2] / x[2]
check('B world-camera projection round trip', project(xc), [B['u']+.5, B['v']+.5])
check('B camera point', xc, B['camera_point'])
check('B SH initialization restores RGB', np.array(B['sh0'])*.28209479177387814+.5, np.array(B['rgb'])/255)
X,Y,Z = xc
J = np.array([[K[0,0]/Z,0,-K[0,0]*X/Z**2],[0,K[1,1]/Z,-K[1,1]*Y/Z**2]])
check('perspective Jacobian finite difference', jac(project, xc), J)
sig = lambda x: 1/(1+np.exp(-x))
loss = lambda x: abs(x[0]*sig(x[1])-.6)
check('color and opacity-logit chain rule', jac(loss,[.8,0]), [-.5,-.2])
w, depths = np.array([.5,.4]), np.array([10.,20.])
ed = lambda x: x @ depths / x.sum()
check('expected-depth weight derivative', jac(ed,w), (depths-ed(w))/w.sum())
inv = lambda x: abs(1/x[0]-.1)
check('inverse-depth derivative', jac(inv,[12]), [1/144])
newloss = float(loss(np.array([.8,0])-.1*np.array([-.5,-.2])))
assert newloss < loss([.8,0])
checks.append(dict(name='teaching SGD step lowers its toy loss', passed=True, before=.2, after=newloss))
scale = np.diag([756/1920,420/1080,1])
check('saved depth K agrees with axis-specific scaling', z['K_depth'], scale @ K, atol=5e-5)
report = dict(scope='CPU algebra checks, not CUDA gradient validation or reconstruction accuracy',
              passed=len(checks), checks=checks)
payload = json.dumps(report, ensure_ascii=False, indent=2)
if a.out: a.out.write_text(payload, encoding='utf-8')
print(payload)
