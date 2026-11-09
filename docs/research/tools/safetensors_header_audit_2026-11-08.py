"""Count tensors in HF safetensors HTTP headers only; no weight bytes downloaded.

Usage: python docs/research/tools/safetensors_header_audit_2026-11-08.py Qwen/Qwen3.5-4B
HTTP Range requests are checked for 206 before reading any response body.
"""
import json
import math
import sys
from collections import defaultdict
from urllib.parse import quote

import requests

def fetch_header(repo, filename):
    url=f'https://huggingface.co/{repo}/resolve/main/{quote(filename)}'
    with requests.get(url,headers={'Range':'bytes=0-7'},stream=True,timeout=20) as r:
        if r.status_code != 206: raise RuntimeError(f'Range unavailable: {r.status_code} {url}')
        b=r.raw.read(8)
    n=int.from_bytes(b,'little')
    if not 0 < n < 16_000_000: raise RuntimeError(f'Unexpected header length {n}')
    with requests.get(url,headers={'Range':f'bytes=8-{7+n}'},stream=True,timeout=20) as r:
        if r.status_code != 206: raise RuntimeError(f'Header Range unavailable: {r.status_code}')
        head=r.raw.read(n)
    if len(head)!=n: raise RuntimeError('Incomplete header')
    return json.loads(head)

def count(repo):
    idx_url=f'https://huggingface.co/{repo}/resolve/main/model.safetensors.index.json'
    ri=requests.get(idx_url,timeout=15)
    files=sorted(set(ri.json()['weight_map'].values())) if ri.status_code==200 else ['model.safetensors']
    groups=defaultdict(int); dtypes=defaultdict(int); total=0
    for filename in files:
        header=fetch_header(repo,filename)
        for name,t in header.items():
            if name=='__metadata__': continue
            n=math.prod(t['shape']); total+=n; dtypes[t['dtype']]+=n
            prefix=name.split('.')[0]
            if prefix=='model' and '.' in name: prefix='model.'+name.split('.')[1]
            groups[prefix]+=n
    print(repo, 'total',total,'files',len(files),'dtypes',dict(dtypes))
    for k,v in sorted(groups.items()):print(' ',k,v)

if __name__=='__main__':
    for repo in sys.argv[1:]:
        try: count(repo)
        except Exception as e: print(repo,'ERROR',e)
