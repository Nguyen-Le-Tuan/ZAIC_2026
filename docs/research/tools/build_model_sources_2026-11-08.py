"""Build a source register using the prior research CSV schema."""
import csv
from pathlib import Path

BASE=Path('docs/research/codex_sources_2026-10-31.csv')
CAND=Path('docs/research/model_candidates_2026-11-08.csv')
OUT=Path('docs/research/model_sources_2026-11-08.csv')
fields=list(next(csv.DictReader(BASE.open(encoding='utf-8'))))
manual=[
 ('Official LifeMate Rule','Zalo AI','2026','official rules','https://challenge.zalo.ai/portal/lifemate','Rule API: <6B whole; <5B LLM; 16,384 context; A30; 30s; offline; date','R0'),
 ('Official LifeMate Rule API','Zalo AI','2026','official rules API','https://api-challenge.zalo.ai/fe/api/config-detail?name=rule&title=1','Public endpoint; requires Origin/Referer challenge.zalo.ai; updated_time 1793671790','R0'),
 ('ZAC 2026 competition regulations','Zalo AI','2026','official regulations','https://dl-challenge.zalo.ai/zalo-ai-challenge-regulations-en.pdf','Open-source commercial terms and 16 Nov deadline','R0'),
 ('LifeMate Docker Guide','Zalo AI','2026','official Docker guide','https://dl-challenge.zalo.ai/2026/lifemate_argfzdgert/Docker_Guide_ZAC2026_LifeMate.pdf','Page 4 RTX 5090 32GB driver 595.58.03 CUDA13.2; conflicts with Rule A30','R0'),
 ('Qwen3.5-4B card','Qwen','2026','model card','https://huggingface.co/Qwen/Qwen3.5-4B','BFCL-V4 50.3 self-report; text-only flag; native tool use; version notes','R1;R5'),
 ('Qwen3.5 text-only derivative','tuandunghcmut','2026','model card','https://huggingface.co/tuandunghcmut/Qwen3.5-4B-text-only','Vision/MTP removed; card claims greedy parity','R1;R5'),
 ('Qwen3.5 Transformers architecture','Hugging Face','2026','official library docs','https://huggingface.co/docs/transformers/main/model_doc/qwen3_5','Qwen3_5ForCausalLM text-only class','R1;R5'),
 ('Qwen3-ASR documentation','Hugging Face','2026','official library docs','https://huggingface.co/docs/transformers/model_doc/qwen3_asr','Vietnamese language listed','R2'),
 ('Qwen3.5 safetensors index','Qwen','2026','model index','https://huggingface.co/Qwen/Qwen3.5-4B/resolve/main/model.safetensors.index.json','Tensor names; HTTP Range headers counted by audit script','R5'),
 ('Gipformer 1.5 model card','G-Group AI Lab','2026','model card','https://huggingface.co/g-group-ai-lab/gipformer1.5-68M-rnnt','Vietnamese WER self-report','R2'),
 ('BuzzASR Vietnamese model card','BuzzASR','2026','model card','https://huggingface.co/BuzzASR/vietnamese','FLEURS Vietnamese WER self-report','R2'),
 ('Moonshine tiny Vietnamese model card','Moonshine AI','2026','model card','https://huggingface.co/moonshine-ai/moonshine-streaming-tiny-vi','FLEURS and LSVSC WER on 400 seeded utterances','R2'),
 ('QUAN Transcribe model card','qnguyen3','2026','model card','https://huggingface.co/qnguyen3/QUAN-Transcribe-1.0','External EmbeddingGemma 2; 356M card; gated','R2'),
 ('VibeVoice ASR BitNet model card','Microsoft','2026','model card','https://huggingface.co/microsoft/VibeVoice-ASR-BitNet','Quantized tensor count misleading; original 4.62GB FP16','R2'),
 ('Voxtral Mini model card','Mistral','2025','model card','https://huggingface.co/mistralai/Voxtral-Mini-3B-2507','Function calling from voice; component count from headers','R3'),
 ('Gemma 4 E2B card','Google','2026','model card','https://huggingface.co/google/gemma-4-E2B-it','Audio input and function calling','R3'),
 ('vLLM structured outputs','vLLM','2026','official docs','https://docs.vllm.ai/en/stable/features/structured_outputs/','XGrammar/guidance JSON and grammar','R4'),
 ('vLLM N-gram speculative decoding','vLLM','2026','official docs','https://docs.vllm.ai/en/stable/features/speculative_decoding/n_gram/','Draft-free prompt lookup','R4'),
 ('Vocabulary trimming','Ushio et al.','2023','paper','https://arxiv.org/abs/2305.15020','Vocabulary pruning; original task not LifeMate','R5'),
 ('Minitron pruning and distillation','NVIDIA','2024','paper','https://arxiv.org/abs/2408.11796','8B to 4B released approach','R5'),
 ('Whisper encoder layer pruning','Aagaard et al.','2026','paper','https://arxiv.org/abs/2609.27980','Six-layer pruning with WER tradeoff','R5'),
 ('HyPoradise ASR error correction','NVIDIA/IBM','2023','paper','https://arxiv.org/abs/2309.15701','N-best correction evidence','R4'),
 ('TIES Merging','Yadav et al.','2023','paper','https://arxiv.org/abs/2306.01708','Model merge technique','R4'),
 ('SOLAR depth up-scaling','Kim et al.','2023','paper','https://arxiv.org/abs/2312.15166','Depth duplication with continued training','R5'),
 ('GigaSpeech 2 dataset card','SpeechColab','2024','dataset card','https://huggingface.co/datasets/speechcolab/gigaspeech2','30k hours across three languages; commercial caveat','R2'),
 ('Vast AI live GPU prices','Vast AI','2026','provider price page','https://vast.ai/article/how-much-does-it-cost-to-rent-a-gpu-in-the-cloud-live-pricing-guide','Indicative on-demand GPU price; changes frequently','R8'),
 ('Runpod RTX4090 price','Runpod','2026','provider price page','https://www.runpod.io/gpu-models/rtx-4090','From $0.34/h; provider quote','R8'),
 ('LifeMate competitor baseline README','MrPickle200','2026','public repo README','https://github.com/MrPickle200/zalo-ai-2026-lifemate','Qwen3.5 4B + faster-whisper disclosed in README only','R7'),
 ('LifeMate competitor README','trtkiet','2026','public repo README','https://github.com/trtkiet/zalo-ai-challenge','Gipformer/Zipformer + SEA-LION disclosed in README only','R7'),
]
rows=[];seen=set()
for title,org,year,typ,url,claims,axes in manual:
    rows.append(dict(sid=f'S{len(rows)+1}',title=title,authors_or_org=org,year=year,venue_or_type=typ,url=url,accessed='2026-11-08',evidence_type=typ,axes=axes,claims_used=claims,license='',weights_release_date='',params='',relevance_1to5='5',notes=''));seen.add(url)
for c in csv.DictReader(CAND.open(encoding='utf-8')):
    if c['status']=='unverified':continue
    url=c['url']
    if not url or url in seen:continue
    rows.append(dict(sid=f'S{len(rows)+1}',title=c['repo_id'],authors_or_org=c['repo_id'].split('/')[0],year=(c['weights_first_commit'] or c['accessed'])[:4],venue_or_type='HF model metadata/card' if c['component']!='technique' else 'method primary source',url=url,accessed='2026-11-08',evidence_type=c['params_source'] or 'card/paper',axes=c['component'],claims_used='existence; license; parameter count when available',license=c['license'],weights_release_date=c['weights_first_commit'],params=c['params_total'],relevance_1to5='4',notes=c['exclusion_reason']));seen.add(url)
with OUT.open('w',newline='',encoding='utf-8') as fp:
    w=csv.DictWriter(fp,fieldnames=fields);w.writeheader();w.writerows(rows)
print(len(rows),'sources')
