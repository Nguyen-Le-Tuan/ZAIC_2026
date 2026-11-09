"""Build audited LifeMate parameter-budget combinations from candidate metadata."""
import csv
from pathlib import Path

P=Path('docs/research/model_candidates_2026-11-08.csv')
OUT=Path('docs/research/model_combos_2026-11-08.csv')
M={r['repo_id']:int(r['params_total']) for r in csv.DictReader(P.open(encoding='utf-8')) if r['params_total']}
F='combo_id components params_total params_llm headroom_6b headroom_5b rule_interpretation vram_gb latency_estimate_s work_needed gpu_hours cost_usd expected_gain evidence_level fits_before_13_11 risks rank notes'.split()
rows=[]

def combo(cid,parts,llm,adapter=0,rank='',rule='strict; counts every loaded model and unmerged adapter',lat='unknown; target <25',work='',hours='',gain='unknown',before='no',risk='',note='',known=True):
    total=sum(M[x] for x in parts)+adapter
    lp=sum(M[x] for x in llm)+adapter
    # Weight-only estimates: runtime activations/KV cache are additional and must be measured.
    vram=f'bf16 weights {2*total/1e9:.2f} GB; 4-bit lower bound {0.60*total/1e9:.2f} GB; KV/activations extra'
    rows.append(dict(combo_id=cid,components=' + '.join(parts)+(f' + unmerged LoRA {adapter}' if adapter else ''),params_total=total,params_llm=lp,headroom_6b=6_000_000_000-total,headroom_5b=5_000_000_000-lp,rule_interpretation=rule,vram_gb=vram,latency_estimate_s=lat,work_needed=work,gpu_hours=hours,cost_usd='planning only: '+(f'${float(hours.split("-")[0])*0.34:.1f}-${float(hours.split("-")[-1])*0.70:.1f}' if hours and '-' in hours else 'unknown'),expected_gain=gain,evidence_level='[Bằng chứng mạnh] count; [Suy luận] gain/latency' if known else '[Chưa kiểm chứng] component count',fits_before_13_11=before,risks=risk,rank=rank,notes=note))

q4='Qwen/Qwen3-4B-Instruct-2507'; q35='Qwen/Qwen3.5-4B'; q35t='tuandunghcmut/Qwen3.5-4B-text-only'; pho='vinai/PhoWhisper-large'; turbo='openai/whisper-large-v3-turbo'; qasr='Qwen/Qwen3-ASR-0.6B'; moon='moonshine-ai/moonshine-streaming-tiny-vi'; gip='g-group-ai-lab/gipformer1.5-68M-rnnt'
q4_lora=66_060_288; q35_lora=60_948_480

combo('C0',[q4,pho],[q4],q4_lora,rank='2',lat='measured 10.4 s mean on 4070; 5090 unknown',work='none; preserve current Docker',hours='0-2',gain='reference public 51.16; no private forecast',before='yes',risk='Docker sm_120 validation pending',note='PhoWhisper LoRA merged; Qwen LoRA unmerged; score is observed public only')
combo('C1',[q35t,pho],[q35t],q35_lora,rank='1',lat='estimate 6-20; measure p95 on 5090',work='adapt Qwen3.5 tokenizer/prompt; add linear-attn LoRA targets; SFT; Docker smoke',hours='8-20',gain='hypothesis -4 to +10 pp vs C0, no LifeMate test',before='yes',risk='new hybrid runtime and template; derivative acceptance; 2-4 pp seed noise',note='Text-only derivative released 2026-06-24; card claims greedy parity with original; LoRA r32 60,948,480 counted from tensor shapes')
combo('C1m',[q35t,pho],[q35t],0,lat='estimate 6-20; measure',work='SFT then merge LoRA in bf16 and verify parity',hours='10-24',gain='unknown; same hypothesis as C1',before='yes',risk='merge may change NF4 behavior; need full bf16 GPU test',note='Only valid if adapter actually merged, not loaded separately')
combo('C2',[q35,turbo],[q35],q35_lora,rank='3',lat='estimate 5-18; measure',work='SFT Qwen3.5; use existing turbo-ft ASR; change prompt/runtime',hours='8-18',gain='hypothesis -6 to +8 pp vs C0',before='yes',risk='ASR was ~4.87 public points worse with old agent; architecture integration',note='Count full vision+MTP checkpoint conservatively')
combo('C3',[q35,qasr],[q35],q35_lora,rank='4',lat='estimate 6-24; measure',work='new Qwen ASR adapter + Qwen3.5 SFT',hours='10-24',gain='hypothesis -8 to +10 pp vs C0',before='yes',risk='ASR Vietnamese slot quality unmeasured; two new runtimes',note='Qwen ASR name 0.6B but true count 938,008,576')
combo('C4',[q35,'vinai/PhoWhisper-medium'],[q35],q35_lora,lat='estimate 6-20; measure',work='fine-tune medium on domain + Qwen3.5 SFT',hours='12-28',gain='hypothesis -7 to +9 pp vs C0',before='yes',risk='ASR medium domain quality unknown',note='Whisper parameter formula verified against HF OpenAI counts')
combo('C5',[q35,gip],[q35],q35_lora,lat='estimate 5-17 on 5090; measure',work='icefall/ONNX adapter + Qwen3.5 SFT',hours='9-20',gain='hypothesis -10 to +7 pp vs C0; ASR only WER 16.89 on first 100 dev_random',before='yes',risk='Gipformer count from config; ASR WER above Pho-large-ft on non-identical subset; slot/agent effects unmeasured',note='Pha D CPU int8 ONNX 100 final WAVs: WER 16.89, RTF 0.021, 35/36 numeric values; no domain fine-tune')
combo('C6',[q4,pho,moon],[q4],q4_lora,lat='estimate 7-22 on 5090; measure',work='add second ASR and conservative consensus; keep Qwen agent',hours='4-10',gain='hypothesis -3 to +3 pp vs C0; Moonshine alone WER 41.29 on first 100 dev_random',before='no',risk='ROVER can corrupt correct numerals; second ASR far worse on domain; extra latency',note='Pha D CPU fp32 100 final WAVs: Moonshine WER 41.29, RTF 0.036; dual-ASR complementarity untested')
combo('C7',['Qwen/Qwen3-4B-Thinking-2507',pho],['Qwen/Qwen3-4B-Thinking-2507'],q4_lora,rank='5',lat='estimate 10-30+; cap reasoning',work='SFT Thinking; cap output/reasoning; same ASR',hours='8-20',gain='hypothesis -5 to +7 pp vs C0',before='yes',risk='30s timeout; reasoning may not fit greedy',note='Same size as current LLM; different behavior')
combo('C8',[q35t,qasr,'Qwen/Qwen3-0.6B'],[q35t,'Qwen/Qwen3-0.6B'],0,lat='estimate 8-25; measure',work='train verifier/router and Qwen3.5; merge adapter; new ASR; guarded call policy',hours='16-40',gain='hypothesis -8 to +12 pp vs C0',before='no',risk='multi-LLM rule just fits strict sum; tight schedule',note='Strict LLM sum 4,957,383,680; any unmerged adapter may exceed 5B')
combo('C9',[q35t,pho,moon],[q35t],q35_lora,lat='estimate 8-24; measure',work='dual ASR consensus + Qwen3.5 SFT',hours='12-26',gain='hypothesis -4 to +10 pp vs C0',before='no',risk='extra complexity; Moonshine alone WER 41.29 on LifeMate first 100 dev_random',note='Text-only + two ASR under 6B; complementarity untested')
combo('C10',['Tiiny/SmallThinker-4BA0.6B-Instruct',pho],['Tiiny/SmallThinker-4BA0.6B-Instruct'],0,lat='estimate 6-20; measure',work='MoE custom code, prompt/SFT, merge adapter if trained',hours='12-28',gain='unknown; no LifeMate evidence',before='no',risk='trust_remote_code; Vietnamese unmeasured',note='MoE total count; active count never substitutes for total')
combo('C11',['ibm-granite/granite-3.1-3b-a800m-instruct',pho],['ibm-granite/granite-3.1-3b-a800m-instruct'],0,lat='estimate 6-20; measure',work='MoE SFT and prompt adaptation',hours='10-24',gain='unknown',before='no',risk='smaller agent; no Vietnamese task score',note='MoE total count 3,298,793,472')
combo('C12',['mistralai/Voxtral-Mini-3B-2507'],['mistralai/Voxtral-Mini-3B-2507'],0,lat='estimate 7-25; measure',work='audio-direct agent + Mistral tool schema/SFT',hours='20-50',gain='unknown; possible ASR text bottleneck removal',before='no',risk='Vietnamese spoken tool-calling unmeasured; integration work',note='LLM count 4,014,136,320, not whole checkpoint count')
rows[-1]['params_llm']=4_014_136_320;rows[-1]['headroom_5b']=5_000_000_000-4_014_136_320
combo('C13',['google/gemma-4-E2B-it'],['google/gemma-4-E2B-it'],0,lat='estimate 8-25; measure',work='audio-direct agent; Gemma4 runtime; SFT',hours='20-50',gain='unknown',before='no',risk='LLM portion vs full checkpoint rule ambiguity; Vietnamese audio unmeasured',note='Header split counted; audio+vision included strictly')
rows[-1]['params_llm']=4_647_449_891;rows[-1]['headroom_5b']=5_000_000_000-4_647_449_891
combo('C14',['Qwen/Qwen2.5-Omni-3B'],['Qwen/Qwen2.5-Omni-3B'],0,lat='estimate 8-25; measure',work='audio-direct agent; disable talker; SFT',hours='20-50',gain='unknown',before='no',risk='EXCLUDED: qwen-research licence conflicts with competition commercial-use condition; LLM partition and runtime complexity',note='Illustrative rejected combination only; thinker=4,703,464,448 conservative upper bound for LLM')
rows[-1]['params_llm']=4_703_464_448;rows[-1]['headroom_5b']=5_000_000_000-4_703_464_448
combo('C15',['ServiceNow-AI/Apriel-5B-Instruct',turbo],['ServiceNow-AI/Apriel-5B-Instruct'],0,lat='estimate 6-20; measure',work='custom Apriel code, SFT then merge LoRA; existing turbo ASR',hours='12-28',gain='unknown',before='no',risk='Vietnamese/tool use unmeasured; custom architecture',note='Count assumes adapter merged')
combo('C16',['arcee-ai/AFM-4.5B',qasr],['arcee-ai/AFM-4.5B'],0,lat='estimate 6-20; measure',work='SFT then merge LoRA; ASR adapter',hours='12-28',gain='unknown',before='no',risk='two untested models',note='Count assumes adapter merged')
combo('C17',[q4,qasr],[q4],q4_lora,lat='estimate 5-18; measure',work='new ASR adapter; agent unchanged',hours='2-8',gain='hypothesis -6 to +4 pp vs C0',before='yes',risk='ASR slot quality unmeasured',note='Cheap ASR ablation; no need retrain agent')
combo('C18',[q35t,pho,gip],[q35t],q35_lora,lat='estimate 8-25; measure',work='Qwen3.5 SFT + Gipformer adapter + voting',hours='14-30',gain='unknown',before='no',risk='Gipformer count from config; two ASR; complementarity not measured',note='Pha D Gipformer WER 16.89 on LifeMate first 100 dev_random; alternative dual ASR')

for r in rows:
    r['rule_interpretation'] += '; 6B and 5B are strict <, not <='
    if int(r['headroom_6b']) <= 0 or int(r['headroom_5b']) <= 0:
        r['fits_before_13_11']='no';r['risks']+='; over parameter cap'

with OUT.open('w',newline='',encoding='utf-8') as fp:
    w=csv.DictWriter(fp,fieldnames=F);w.writeheader();w.writerows(rows)
print(len(rows),'combos; top',[(r['combo_id'],r['params_total'],r['headroom_6b']) for r in rows if r['rank']])
