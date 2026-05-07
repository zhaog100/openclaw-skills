#!/bin/bash
# QMD 搜索脚本 - 使用 MiniLM embedding

export PYTHONPATH=/home/zhaog/.local/lib/python3.14/site-packages:$PYTHONPATH

python3 << 'PYEOF'
from qmd.core.embedding import Embedder
Embedder._shared_model = None
Embedder.MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
Embedder.DIM = 384

import qmd
import sys

query = sys.argv[1] if len(sys.argv) > 1 else ""
top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 5

client = qmd.connect()
coll = client.collection("knowledge")

results = coll.hybrid_search(query, top_k=top_k)
for r in results:
    print(f"[{r.chunk_ref.document_id}] score={r.score:.3f}")
    print(f"  {r.text[:200]}...")
    print()
PYEOF
