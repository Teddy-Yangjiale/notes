"""Executable, deterministic checks of the teaching examples (stdlib only).

These check small analytic models, not a complete renderer, fluid solver,
camera calibration, perceptual model, or deployed server environment.
"""
import json, math, random
from pathlib import Path

results=[]
def check(name,value,expected,tol=1e-9):
    assert math.isfinite(value),name
    assert math.isclose(value,expected,rel_tol=tol,abs_tol=tol),(name,value,expected)
    results.append(dict(name=name,value=value,expected=expected,tolerance=tol))

def main():
    pi=math.pi
    check('01/rgb-buffer-bytes',4*3*3,36)
    check('01/triangle-area',abs(4*3)/2,6)
    check('01/coverage',sum([1,1,1,0])/4,.75)
    check('14/isotropic-power',2*4*pi,8*pi)
    check('14/point-irradiance',8*math.cos(pi/3)/2**2,1)
    check('14/radiance',.02/(.1*.5*.2),2)
    check('14/disk-source',2*pi/(1+3),pi/2)
    # Midpoint quadrature independently checks the projected hemisphere measure.
    n=20000
    integral=sum(math.cos((i+.5)*pi/(2*n))*math.sin((i+.5)*pi/(2*n)) for i in range(n))*pi/(2*n)*2*pi
    check('14/hemisphere-integral',integral,pi,tol=2e-9)
    check('15/non-unit-domain',sum(x/.5 for x in [.25,1.75])/2,2)
    check('15/pdf-normalization',4*.25,1)
    check('15/inverse-cdf',(2*(1/8)**(1/3))**3/8,1/8)
    check('15/area-to-direction-probability',(.5*4/.5)*(.01*.5/4),.5*.01)
    check('15/cosine-lambert-weight',(.8/pi)*.5/(.5/pi),.8)
    rng=random.Random(184)
    uniform=[2*rng.random() for _ in range(100000)] # integral of 2x on [0,1]
    mean=sum(uniform)/len(uniform)
    assert abs(mean-1)<.01,mean
    results.append(dict(name='15/MC-uniform-2x',value=mean,reference=1,samples=len(uniform),seed=184,gate='absolute error < 0.01; one seeded experiment, not a proof of unbiasedness'))
    importance=[2*math.sqrt(rng.random()) for _ in range(100)]
    check('15/importance-constant-contribution',sum(x/x for x in importance)/100,1)
    check('16/throughput',.8*.5*10,4)
    check('16/roulette-expectation',.25*(2/.25)+.75*0,2)
    check('16/geometric-tail',sum(.5**i for i in range(4))+.125,2)
    check('16/uniform-environment',(.4/pi)*(5*pi),2)
    check('18/reflection-unit-length',(-.6)**2+.8**2,1)
    check('18/snell',1.5*math.sin(math.asin(1/3)),.5)
    check('18/schlick-F0',((1-1.5)/(1+1.5))**2,.04)
    check('18/schlick-60deg',.04+.96*(1-.5)**5,.07)
    check('18/microfacet',.04*2*.8/(4*.5*.5),.064)
    check('18/beer-composition',math.exp(-.5)*math.exp(-.5),math.exp(-1))
    check('19/cone-inner-product',3*.2+1*.8,1.4)
    check('19/xy-reconstruction',(3/.3)*.2,2)
    check('19/gamma-roundtrip',(.5**(1/2.2))**2.2,.5)
    check('19/tone-map-inverse',(.75)/(1-.75),3)
    check('21/LBS-x',.75*2+.25*0,1.5)
    check('21/blendshape',1+.5*.2,1.1)
    check('21/IK-cosine',(1**2+1**2-1**2-1**2)/2,0)
    check('21/damped-J-update',.1*.02/(.1**2+.1**2),.1)
    check('24/spring-force',100*(1.2-1),20)
    check('24/internal-damping-power',6*0-6*2,-12)
    check('24/series-stiffness',1/(1/20+1/20),10)
    x,v=1.,0.;h=.1
    ex,ev=x+h*v,v-h*x
    sv=v-h*x;sx=x+h*sv
    ix=(x+h*v)/(1+h*h);iv=v-h*ix
    check('24/explicit-energy',.5*(ex*ex+ev*ev),.505)
    check('24/semi-energy',.5*(sx*sx+sv*sv),.49505)
    check('24/implicit-energy-ratio',(.5*(ix*ix+iv*iv))/.5,1/(1+h*h))
    # Long-running oscillators expose the mechanism hidden by one-step tests.
    for method in ['explicit','semi','implicit']:
        x,v=1.,0.;energy=[]
        for _ in range(1000):
            if method=='explicit':x,v=x+h*v,v-h*x
            elif method=='semi':v-=h*x;x+=h*v
            else:xnext=(x+h*v)/(1+h*h);v-=h*xnext;x=xnext
            energy.append(.5*(x*x+v*v))
        if method=='explicit':assert energy[-1]>1000
        elif method=='semi':assert max(energy)<.54 and min(energy)>.47
        else:assert energy[-1]<.001
        results.append(dict(name=f'24/oscillator-{method}',steps=1000,step=h,energy_min=min(energy),energy_max=max(energy),energy_final=energy[-1]))
    check('25/divergence-cell',(3-1+2-2)/1,2)
    check('25/pressure-projection',3-.5/2*12,0)
    check('25/laplacian-constant',2+2+2+2-4*2,0)
    check('25/advection-interpolation',.5*2+.5*4,3)
    check('25/pressure-gradient-x',.1*(2*1),.2)
    check('25/pressure-gradient-y',.1*(2*2),.4)
    check('26/stereo-disparity',1000*.06/2,30)
    check('26/latency-pixels',90*.033*20,59.4)
    check('26/foveated-work',.1+.9*.25,.325)
    check('26/effective-baseline-60',6*math.cos(pi/3),3)
    check('26/effective-baseline-90',6*math.cos(pi/2),0)
    zi=50*1000/(1000-50)
    check('90/thin-lens',1/1000+1/zi,1/50)
    check('90/horizontal-FOV',math.degrees(2*math.atan(36/(2*50))),39.597752709049864)
    check('90/circle-of-confusion',10*abs(51-50)/50,.2)
    check('90/exposure-equivalence',(1/200)/2**2,(1/50)/4**2)
    check('91/constant-kernel',3*(1/4+1/2+1/4),3)
    check('91/sharpen-overshoot',5*10-4*8,18)
    check('91/separable-work',225/(15+15),7.5)
    check('91/median',sorted([10,11,255,10,9])[2],10)
    check('91/bilateral-constant',(1*10+.01*10)/(1+.01),10)
    check('91/420-count',16*16+2*8*8,384)
    check('91/quantization',round(23/10)*10,20)
    destination=Path(__file__).resolve().parents[1]/'.work/cs184/numerical-results.json'
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(dict(status='PASS',checks=len(results),scope='analytic teaching models only',results=results),ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(dict(status='PASS',checks=len(results),report=str(destination))))

if __name__=='__main__':main()
