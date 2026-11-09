"""Metadata-only Hugging Face audit for LifeMate; never downloads weights.

Usage: python docs/research/tools/hf_model_audit_2026-11-08.py
Writes only the candidate CSV named by the research brief. Missing fields stay empty.
"""
from __future__ import annotations

import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
import time
import requests

OUT = Path('docs/research/model_candidates_2026-11-08.csv')
API = 'https://huggingface.co/api/models'
KEY_REPOS = {'Qwen/Qwen3.5-4B','Qwen/Qwen3-4B-Instruct-2507','openai/whisper-large-v3-turbo','vinai/PhoWhisper-large','Qwen/Qwen3-ASR-0.6B','g-group-ai-lab/gipformer1.5-68M-rnnt','BuzzASR/vietnamese','microsoft/FrogNano-4B-2609','mistralai/Voxtral-Mini-3B-2507','google/gemma-4-E2B-it','ServiceNow-AI/Apriel-5B-Instruct','ibm-granite/granite-4.2-3b','principled-intelligence/Qwen3.5-4B-text-only','tuandunghcmut/Qwen3.5-4B-text-only'}
FIRST_WEIGHT_DATES = {
 'BuzzASR/vietnamese':'2026-09-08', 'Qwen/Qwen3-ASR-0.6B':'2026-01-28',
 'g-group-ai-lab/gipformer1.5-68M-rnnt':'2026-08-21', 'openai/whisper-large-v3-turbo':'2024-10-01',
 'vinai/PhoWhisper-large':'2023-12-19', 'Qwen/Qwen3-4B-Instruct-2507':'2025-08-05',
 'Qwen/Qwen3-4B-Thinking-2507':'2025-08-05',
 'Qwen/Qwen3.5-4B':'2026-02-27', 'ServiceNow-AI/Apriel-5B-Instruct':'2025-04-11',
 'google/gemma-4-E2B-it':'2026-04-02', 'ibm-granite/granite-4.2-3b':'2026-08-07',
 'microsoft/FrogNano-4B-2609':'2026-09-17',
 'principled-intelligence/Qwen3.5-4B-text-only':'2026-03-11',
 'tuandunghcmut/Qwen3.5-4B-text-only':'2026-06-24',
 'mistralai/Voxtral-Mini-3B-2507':'2025-07-15',
 'trinhtuyen201/speecht5_tts_vietnamese_nl':'2024-05-20',
 'dinhthuan/index-tts-2-vietnamese':'2025-11-17',
}
FIELDS = 'component repo_id revision family params_total params_breakdown params_source weights_first_commit license license_ok vietnamese_evidence tool_calling_evidence key_benchmarks context_len arch_class transformers_ok vllm_ok vram_bf16_gb latency_note status exclusion_reason url accessed'.split()

SEEDS = {
 'llm': '''Qwen/Qwen3-4B-Instruct-2507|Qwen/Qwen3-4B-Thinking-2507|Qwen/Qwen3.5-4B|Qwen/Qwen3.5-4B-Base|Qwen/Qwen3.5-2B|Qwen/Qwen3.5-0.8B|principled-intelligence/Qwen3.5-4B-text-only|tuandunghcmut/Qwen3.5-4B-text-only|Qwen/Qwen3-VL-4B-Instruct|microsoft/Phi-4-mini-instruct|microsoft/Phi-4-mini-flash-reasoning|google/gemma-3-4b-it|google/gemma-4-E2B-it|meta-llama/Llama-3.2-3B-Instruct|nvidia/Llama-3.1-Nemotron-Nano-4B-v1.1|nvidia/Nemotron-Mini-4B-Instruct|nvidia/Llama-3.1-Minitron-4B-Width-Base|nvidia/Llama-3.1-Minitron-4B-Depth-Base|tencent/Hunyuan-4B-Instruct|openbmb/MiniCPM3-4B|openbmb/MiniCPM4-4B|THUDM/glm-edge-4b-chat|ibm-granite/granite-4.0-micro|ibm-granite/granite-4.0-h-micro|ibm-granite/granite-4.2-3b|LiquidAI/LFM2-2.6B|HuggingFaceTB/SmolLM3-3B|mistralai/Ministral-3-3B-Instruct-2512|ServiceNow-AI/Apriel-5B-Instruct|arcee-ai/AFM-4.5B|LGAI-EXAONE/EXAONE-4.0-1.2B|tiiuae/Falcon-H1-3B-Instruct|Zyphra/Zamba2-2.7B-instruct|janhq/Jan-v1-4B|janhq/Jan-nano|Polaris-4B|microsoft/FrogNano-4B-2609|Nanbeige4-3B|Youtu-LLM-2B|vinai/PhoGPT-4B-Chat|arcee-ai/VyLinh|Vi-Qwen2-3B|SeaLLMs-v3-1.5B|Sailor2-3B|GemSUra-2B|VinaLlama-2.7B|aisingapore/SEA-LION-v4-4B-VL|Salesforce/xLAM-2-3b-fc-r|Salesforce/xLAM-2-1b-fc-r|Hammer2.1-3b|katanemo/Arch-Function-3B|katanemo/Arch-Agent-3B|SmallThinker-4BA0.6B|ibm-granite/granite-3.1-3b-a800m''',
 'asr': '''vinai/PhoWhisper-tiny|vinai/PhoWhisper-base|vinai/PhoWhisper-small|vinai/PhoWhisper-medium|vinai/PhoWhisper-large|openai/whisper-large-v3-turbo|openai/whisper-large-v3|Qwen/Qwen3-ASR-0.6B|Qwen/Qwen3-ASR-1.7B|g-group-ai-lab/gipformer1.5-68M-rnnt|BuzzASR/vietnamese|nvidia/parakeet-ctc-0.6b-vi|khanhld/chunkformer-large-vie|hynt/Zipformer-30M-RNNT-6000h|nguyenvulebinh/wav2vec2-base-vietnamese-250h|nguyenvulebinh/wav2vec2-large-vietnamese-250h|facebook/mms-1b-all|facebook/seamless-m4t-v2-large|espnet/owsm_v3.1_ebf|espnet/owsm_ctc_v3.1|Voxtral-Mini-3B-Transcribe|DataoceanAI1/dolphin-small|DataoceanAI1/dolphin-base|Moonshine Vietnamese|VietASR Zipformer|EraX-WoW-Turbo|erax-ai/erax-wows-turbo|Systran/faster-whisper-large-v3|nvidia/canary-1b-v2|nvidia/parakeet-tdt-0.6b-v3|k2-fsa/zipformer|Viettel ASR|FPT ASR|5CD-AI/VieGem-ASR|qnguyen3/QUAN-Transcribe-1.0|nvidia/nemotron-3.5-asr-streaming-0.6b|moonshine-ai/moonshine-streaming-tiny-vi|microsoft/VibeVoice-ASR-BitNet|kyle/vi-asr-fastconformer-114m|HoangPhu/ZipFormer-150M-finetuned-vi-ticket''',
 'speech_llm': '''google/gemma-3n-E2B-it|google/gemma-3n-E4B-it|google/gemma-4-E2B-it|Qwen/Qwen2.5-Omni-3B|mistralai/Voxtral-Mini-3B-2507|microsoft/Phi-4-multimodal-instruct|fixie-ai/ultravox-v0_5-llama-3_1-8b|ibm-granite/granite-speech-3.3-2b|openbmb/MiniCPM-o-2_6|LLaMA-Omni2-3B|mistralai/Voxtral-Mini-3B-Transcribe|Qwen/Qwen3-Omni-4B''',
 'aux': '''facebook/bartpho-syllable|VietAI/vit5-base|VietAI/vit5-large|snakers4/silero-vad|nvidia/NeMo-text-processing|Qwen/Qwen3-0.6B|microsoft/Phi-4-mini-instruct''',
 'tts': '''pnnbao-ump/VieNeu-TTS|pnnbao-ump/VieNeu-TTS-v3-Turbo|toandev/F5-TTS-Vietnamese|hynt/F5-TTS-Vietnamese-ViVoice|viXTTS|facebook/mms-tts-vie|ResembleAI/chatterbox|fishaudio/fish-speech-1.5|FunAudioLLM/CosyVoice2-0.5B|OpenAudio/S1-mini|VietTTS|VITS Vietnamese|trinhtuyen201/speecht5_tts_vietnamese_nl|dinhthuan/index-tts-2-vietnamese''',
 'teacher': '''Qwen/Qwen3-32B|Qwen/Qwen3.5-27B|deepseek-ai/DeepSeek-R1''',
 'draft': '''Qwen/Qwen3-0.6B|Qwen/Qwen3-1.7B'''
}

def get(url, **kwargs):
    for attempt in range(2):
        try:
            r = requests.get(url, timeout=15, **kwargs)
            if r.status_code == 200:
                return r.json()
            if r.status_code not in (429,500,502,503,504):
                return None
        except (requests.RequestException, ValueError):
            pass
        time.sleep(0.4 * 2**attempt)
    return None

def resolve(seed):
    direct = get(f'{API}/{seed}', params=[('expand[]',k) for k in ['sha','safetensors','createdAt','cardData','tags','downloads','likes']])
    if direct:
        return direct
    hits = get(API, params={'search': seed.split('/')[-1], 'limit': 30}) or []
    key = seed.split('/')[-1].casefold()
    exact = [h for h in hits if h['id'].split('/')[-1].casefold() == key and ('/' not in seed or h['id'].split('/')[0].casefold() == seed.split('/')[0].casefold())]
    if len(exact) == 1:
        return get(f"{API}/{exact[0]['id']}", params=[('expand[]',k) for k in ['sha','safetensors','createdAt','cardData','tags','downloads','likes']])
    return None

def first_weight_commit(repo):
    commits = get(f'{API}/{repo}/commits/main') or []
    if not commits or len(commits) >= 100:
        return ''
    for c in reversed(commits):
        tree = get(f"{API}/{repo}/tree/{c['id']}", params={'recursive':'true','expand':'false'}) or []
        if any(f.get('type')=='file' and f.get('path','').lower().endswith(('.safetensors','.bin','.pt','.ckpt','.gguf')) for f in tree):
            return c['date'][:10]
    return ''

def whisper_params(c):
    try:
        d=c['d_model']; fe=c['encoder_ffn_dim']; fd=c['decoder_ffn_dim']; v=c['vocab_size']
        el=c['encoder_layers']; dl=c['decoder_layers']; es=c['max_source_positions']; ds=c['max_target_positions']; mel=c['num_mel_bins']
        if not c.get('tie_word_embeddings',True): return None
        enc=d*mel*3+d + d*d*3+d + es*d + el*(4*d*d+2*d*fe+8*d+fe)+2*d
        dec=v*d+ds*d+dl*(8*d*d+2*d*fd+13*d+fd)+2*d
        return enc+dec
    except KeyError:
        return None

def audit(item):
    component, seed = item
    row = dict.fromkeys(FIELDS, '')
    row.update(component=component, repo_id=seed, family=seed.split('/')[-1], accessed=date.today().isoformat(), url=f'https://huggingface.co/{seed}', status='unverified')
    m = resolve(seed)
    if not m:
        row['exclusion_reason'] = 'Không tìm thấy repo_id duy nhất bằng HF API; không suy đoán tên.'
        return row
    repo = m['id']
    x = m
    card = x.get('cardData') or m.get('cardData') or {}
    safe = x.get('safetensors') or m.get('safetensors') or {}
    total = safe.get('total')
    lic = card.get('license') or ''
    created = x.get('createdAt') or m.get('createdAt') or ''
    weight_date = FIRST_WEIGHT_DATES.get(repo,'')
    row.update(repo_id=repo, revision=m.get('sha',''), url=f'https://huggingface.co/{repo}', license=lic,
               params_total=total or '', params_breakdown=str(safe.get('parameters','')) if total else '',
               params_source='hf_api' if total else '', weights_first_commit=weight_date,
               license_ok='no' if any(k in lic.lower() for k in ['nc','research']) else ('yes' if lic.lower() in ['apache-2.0','mit','bsd-3-clause','cc-by-4.0'] else 'ask_btc'),
               status='verified' if total and lic else 'reported')
    if weight_date and weight_date >= '2026-10-26':
        row['status'] = 'excluded'; row['exclusion_reason'] = 'Trọng số đầu tiên sau hạn 26/10/2026.'
    elif created and created[:10] >= '2026-10-26':
        row['status'] = 'excluded'; row['exclusion_reason'] = 'Repo tạo sau hạn 26/10/2026.'
    elif row['license_ok'] == 'no':
        row['status'] = 'excluded'; row['exclusion_reason'] = 'Licence hạn chế NC/research.'
    elif not total:
        row['exclusion_reason'] = 'Chưa lấy được số đếm safetensors; không dùng để tính combo.'
    row['latency_note'] = f'HF createdAt {created[:10]}; weight commit {weight_date or "chưa xác minh"}'
    if not total:
        cfg = get(f'https://huggingface.co/{repo}/resolve/main/config.json') or {}
        n = whisper_params(cfg) if cfg.get('model_type')=='whisper' else cfg.get('num_parameters')
        if isinstance(n, int) and n > 0:
            row['params_total']=n; row['params_source']='config_calc'
            if lic and not row['exclusion_reason'].startswith(('Repo tạo','Trọng số đầu tiên','Licence')):
                row['status']='verified' if cfg.get('model_type')=='whisper' else 'reported'
                row['exclusion_reason']=''
            row['vram_bf16_gb']=f'{2*n/1e9:.3f}'
    if total:
        row['vram_bf16_gb'] = f'{2*total/1e9:.3f}'
    return row

def main():
    items = list(dict.fromkeys((component,s.strip()) for component, seeds in SEEDS.items() for s in seeds.split('|') if s.strip()))
    rows = []
    with ThreadPoolExecutor(max_workers=1) as pool:
        for f in as_completed([pool.submit(audit, it) for it in items]):
            rows.append(f.result())
    rows.sort(key=lambda x:(x['component'],x['repo_id']))
    with OUT.open('w', newline='', encoding='utf-8') as fp:
        w=csv.DictWriter(fp, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    from collections import Counter
    print(len(rows), Counter((r['component'],r['status']) for r in rows))

if __name__ == '__main__':
    main()
