#!/usr/bin/env python3
import argparse, os, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
NBS=sorted((ROOT/'notebooks').glob('*.ipynb'))

p=argparse.ArgumentParser()
p.add_argument('--mode',choices=['smoke','standard','full'],default='smoke')
p.add_argument('--timeout',type=int,default=600)
a=p.parse_args()

env=os.environ.copy()
env['SMOKE_TEST']='1' if a.mode=='smoke' else '0'
env['FULL_RUN']='1' if a.mode=='full' else '0'

print(f'Running {len(NBS)} notebooks in {a.mode} mode')
for nb in NBS:
    print(f'\n=== {nb.name} ===',flush=True)
    cmd=[sys.executable,'-m','jupyter','nbconvert','--to','notebook','--execute',nb.name,'--inplace',f'--ExecutePreprocessor.timeout={a.timeout}']
    subprocess.run(cmd,cwd=nb.parent,env=env,check=True)
print('\nAll notebooks completed successfully.')
