"""Fixed seeds for inference, as the organisers' guide asks (Docker guide 04/11/2026, p. 15-16).

Decoding is greedy everywhere (ASR and agent), so no output should depend on a seed; this pins whatever is random by
accident (library defaults, hash order). Seed 0 is the one training uses (lifemate.train --seed 0).
"""
from __future__ import annotations

import os
import random

DEFAULT_SEED = 0


def seed_everything(seed: int = DEFAULT_SEED) -> None:
    """The organisers' seed_everything (guide p. 16) with the team's seed. PYTHONHASHSEED set here reaches only
    child processes; predict.sh and start_jupyter.sh export it before Python starts. Torch is optional, so runs
    without a model (oracle backend) still work where torch is missing. cudnn.deterministic only restricts
    convolution algorithms; forward convolutions in cuDNN are deterministic already, so inference outputs
    should not change."""
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except ImportError:
        pass
    try:
        import torch
    except ImportError:
        return
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)  # lazy: no CUDA context is created here
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
