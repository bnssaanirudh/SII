#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys, nbformat
ROOT=Path(__file__).resolve().parent
subprocess.run([sys.executable,'-m','pytest','-q','tests/test_core.py'],cwd=ROOT,check=True)
clean=True
for p in sorted((ROOT/'notebooks').glob('*.ipynb')):
    nb=nbformat.read(p,4); codes=[c for c in nb.cells if c.cell_type=='code']
    errors=[]
    for i,c in enumerate(codes):
        for o in c.get('outputs',[]):
            if o.output_type=='error': errors.append((i,o.ename,o.evalue))
    executed=sum(c.get('execution_count') is not None for c in codes)
    ok=(executed==len(codes) and not errors)
    clean &= ok
    print(f'{p.name}: {executed}/{len(codes)} executed, errors={errors}')
if not clean: raise SystemExit(1)
print('Package verification passed.')
