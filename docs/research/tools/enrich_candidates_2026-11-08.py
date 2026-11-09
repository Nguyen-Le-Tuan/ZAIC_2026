"""Add card-level evidence and audited non-model techniques to the metadata CSV."""
import csv
from pathlib import Path

P=Path('docs/research/model_candidates_2026-11-08.csv')
rows=list(csv.DictReader(P.open(encoding='utf-8')))
fields=list(rows[0])
by={(r['component'],r['repo_id']):r for r in rows}

def setrow(component,repo,**kwargs):
    r=by.get((component,repo))
    if r:r.update(kwargs)

setrow('llm','Qwen/Qwen3.5-4B',params_breakdown='language_model=4205751296;visual=333514240;mtp=120599552;embedding tied once',vietnamese_evidence='Qwen card: multilingual; no independent LifeMate vi score',tool_calling_evidence='Qwen card: BFCL-V4 50.3 self-reported; vLLM qwen3_coder parser',key_benchmarks='BFCL-V4 50.3 (card; not comparable to BFCL-v3)',context_len='262144',arch_class='hybrid Gated DeltaNet + full attention; vision',transformers_ok='native Qwen3_5; version-pinned smoke test needed',vllm_ok='Qwen card recommends main/nightly; --language-model-only')
for repo in ['principled-intelligence/Qwen3.5-4B-text-only','tuandunghcmut/Qwen3.5-4B-text-only']:
    setrow('llm',repo,params_breakdown='language_model=4205751296; no visual or mtp; tied embedding',vietnamese_evidence='inherits Qwen3.5 multilingual text backbone; no LifeMate vi measurement',tool_calling_evidence='inherits Qwen3.5; third-party card claims greedy logit parity',context_len='262144',arch_class='Qwen3_5ForCausalLM; hybrid Gated DeltaNet',transformers_ok='native in transformers>=5.9; pinned 5.21 likely, smoke test',vllm_ok='text-only support version-dependent; test')
setrow('llm','Qwen/Qwen3-4B-Instruct-2507',vietnamese_evidence='team LifeMate dev/public measured',tool_calling_evidence='team SFT + Qwen ChatML tool tags; BFCL-v3 61.9 card',key_benchmarks='LifeMate public 51.16 with PhoWhisper-large-ft; BFCL-v3 61.9 card',context_len='262144',arch_class='dense Qwen3',transformers_ok='yes, current pipeline',vllm_ok='yes, code backend exists')
setrow('llm','Qwen/Qwen3-4B-Thinking-2507',vietnamese_evidence='Qwen multilingual card; no LifeMate measurement',tool_calling_evidence='Qwen native tool use; reasoning length risk',context_len='262144',arch_class='dense Qwen3 thinking',transformers_ok='likely, smoke test',vllm_ok='likely, smoke test')
setrow('llm','microsoft/FrogNano-4B-2609',params_breakdown='language_model=4205751296;visual=333514240;mtp=120599552',vietnamese_evidence='card: English and Python evaluated; Vietnamese unvalidated',tool_calling_evidence='card: Leaf five-tool coding harness; not LifeMate',key_benchmarks='SWE-bench Verified 61.5 card; task differs',context_len='131072',arch_class='Qwen3.5 derivative hybrid',transformers_ok='Qwen3.5 runtime required',vllm_ok='Qwen3.5 runtime required')
setrow('asr','vinai/PhoWhisper-large',vietnamese_evidence='Vietnamese-specific; team fine-tuned checkpoint WER ~9.2 on dev_random',key_benchmarks='team public +4.87 vs Whisper-turbo-ft, different ASR same agent',arch_class='Whisper encoder-decoder',transformers_ok='yes, current pipeline',vllm_ok='ASR uses transformers')
setrow('asr','openai/whisper-large-v3-turbo',vietnamese_evidence='Vietnamese multilingual; team fine-tuned WER ~11.2 dev_random',key_benchmarks='team pretrained WER ~31.2 vs fine-tuned ~11.2 dev_random',arch_class='Whisper 32-layer encoder/4-layer decoder',transformers_ok='yes',vllm_ok='ASR uses transformers')
setrow('asr','Qwen/Qwen3-ASR-0.6B',params_breakdown='whole checkpoint=938008576 (name 0.6B understates)',vietnamese_evidence='Qwen/HF docs list vi; no LifeMate WER',arch_class='speech encoder + decoder',transformers_ok='Qwen3-ASR support; adapter needed',vllm_ok='not checked')
setrow('asr','g-group-ai-lab/gipformer1.5-68M-rnnt',vietnamese_evidence='Vietnamese specific',key_benchmarks='LifeMate dev_random first 100 final WAVs: WER 16.89, 35/36 numbers, 10/10 numeric times, 290/349 capitalized-word proxy; CPU int8 ONNX',arch_class='Zipformer RNN-T/ONNX',transformers_ok='custom icefall/sherpa adapter needed',vllm_ok='not applicable')
setrow('asr','BuzzASR/vietnamese',vietnamese_evidence='Vietnamese specific',key_benchmarks='FLEURS WER 7.26 (card, normalized)',arch_class='Whisper large derivative',transformers_ok='likely Whisper-compatible, verify',vllm_ok='not applicable')
setrow('asr','moonshine-ai/moonshine-streaming-tiny-vi',weights_first_commit='2026-08-24',vietnamese_evidence='Vietnamese-specific 12,288-token tokenizer',key_benchmarks='LifeMate dev_random first 100 final WAVs: WER 41.29; card FLEURS vi WER 10.98, LSVSC 7.63 on other sets',arch_class='streaming encoder-decoder',transformers_ok='MoonshineStreamingForConditionalGeneration; adapter needed',vllm_ok='not applicable')
setrow('asr','vinai/PhoWhisper-tiny',key_benchmarks='LifeMate dev_random first 100 final WAVs: WER 42.21, unfine-tuned fp32 CPU')
setrow('asr','vinai/PhoWhisper-base',key_benchmarks='LifeMate dev_random first 100 final WAVs: WER 40.55, unfine-tuned fp32 CPU')
setrow('asr','qnguyen3/QUAN-Transcribe-1.0',params_total='',params_breakdown='HF safetensors only 101738068; also best.pt 1.22GB and external EmbeddingGemma2; card claims 356M total',params_source='',license_ok='ask_btc',status='reported',exclusion_reason='Gated Gemma licence; HF safetensors count omits external encoder; exact total unverified',vietnamese_evidence='Vietnamese-specific; card claims avg WER 6.87 on 8 datasets',key_benchmarks='card self-reported 6.87% average; not LifeMate',arch_class='EmbeddingGemma2 encoder + CTC reader')
setrow('asr','microsoft/VibeVoice-ASR-BitNet',params_total='',params_breakdown='quantized packed tensors: HF API 322592829 is not original parameter count; card says 4.62GB FP16 original',params_source='',status='excluded',exclusion_reason='Quantized count misleading; original size likely >2B; no exact count for combination',vietnamese_evidence='card includes Vietnamese; MLC-VI WER 22.38',key_benchmarks='card MLC-VI WER 22.38',arch_class='quantized speech model')
setrow('asr','5CD-AI/VieGem-ASR',vietnamese_evidence='Vietnamese-English streaming CTC',key_benchmarks='card 359M reported; checkpoint count unavailable',arch_class='CTC')
setrow('asr','nvidia/nemotron-3.5-asr-streaming-0.6b',license_ok='no',status='excluded',exclusion_reason='NVIDIA Model Evaluation License; commercial permission unclear',vietnamese_evidence='NVIDIA card lists vi-VN',arch_class='streaming ASR')
setrow('speech_llm','mistralai/Voxtral-Mini-3B-2507',params_breakdown='language_model=4014136320;audio_tower=636968960;projector=25165824',vietnamese_evidence='Vietnamese quality not established on LifeMate',tool_calling_evidence='Mistral card states function calling directly from voice',context_len='32768',arch_class='audio tower + LLM + projector',transformers_ok='Voxtral native architecture; integration test',vllm_ok='Mistral card gives vLLM recipe')
setrow('speech_llm','google/gemma-4-E2B-it',params_total='5123178979',params_breakdown='language_model=4647449891;audio_tower=304825088;vision_tower=167365056;embed_audio=2359296;embed_vision=1179648; safetensors header count differs HF API by 928',params_source='safetensors_header',vietnamese_evidence='Vietnamese speech benchmark not found',tool_calling_evidence='Gemma 4 card: function calling; not LifeMate',arch_class='omni conditional generation',transformers_ok='Gemma4 support; integration test',vllm_ok='version-dependent')
setrow('speech_llm','Qwen/Qwen2.5-Omni-3B',params_breakdown='thinker=4703464448;talker=384604928;token2wav=449051296',vietnamese_evidence='Vietnamese speech quality unverified',arch_class='thinker + talker + vocoder',transformers_ok='Qwen omni support; integration test',vllm_ok='version-dependent')

TECHNIQUES=[
 ('vision_tower_removal','https://huggingface.co/docs/transformers/main/model_doc/qwen3_5','Qwen3.5 native text-only loader'),
 ('vocabulary_trimming','https://arxiv.org/abs/2305.15020','multilingual embedding pruning; domain parity untested'),
 ('whisper_decoder_pruning','https://huggingface.co/openai/whisper-large-v3-turbo','32 to 4 decoder layers precedent'),
 ('whisper_encoder_pruning','https://arxiv.org/abs/2609.27980','six layers pruned; WER tradeoff'),
 ('minitron_pruning_distillation','https://arxiv.org/abs/2408.11796','8B to 4B published'),
 ('ngram_speculative_decoding','https://docs.vllm.ai/en/stable/features/speculative_decoding/n_gram/','draft-free speed method'),
 ('xgrammar_constrained_decoding','https://docs.vllm.ai/en/stable/features/structured_outputs/','schema-constrained JSON'),
 ('lora_soup','https://arxiv.org/abs/2410.13025','merge adapters; no LifeMate evidence'),
 ('ties_dare_merge','https://arxiv.org/abs/2306.01708','task vector merge; no LifeMate evidence'),
 ('rover_asr','https://www.isca-archive.org/asru_1997/fiscus97_asru.html','ASR hypothesis voting'),
 ('asr_nbest_correction','https://arxiv.org/abs/2309.15701','generative error correction'),
 ('contextual_biasing_whisper','https://arxiv.org/search/?query=contextual+biasing+Whisper&searchtype=all','hotword prompt; domain test needed'),
 ('shallow_fusion_ngram','https://arxiv.org/search/?query=shallow+fusion+speech+recognition&searchtype=all','LM-assisted ASR decoding'),
 ('dual_asr_consensus','https://www.isca-archive.org/asru_1997/fiscus97_asru.html','ROVER variant; latency risk'),
 ('multi_lora_routing','https://arxiv.org/abs/2410.13025','separate adapters for roles'),
 ('depth_upscaling','https://arxiv.org/abs/2312.15166','SOLAR; needs released checkpoint'),
]
for name,url,claim in TECHNIQUES:
    r=dict.fromkeys(fields,'');r.update(component='technique',repo_id=name,family=name,license_ok='ask_btc',key_benchmarks=claim,status='reported',url=url,accessed='2026-11-08')
    if ('technique',name) not in by:
        rows.append(r)

with P.open('w',newline='',encoding='utf-8') as fp:
    w=csv.DictWriter(fp,fieldnames=fields);w.writeheader();w.writerows(rows)
print('rows',len(rows))
