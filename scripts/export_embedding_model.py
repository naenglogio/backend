#!/usr/bin/env python3
"""facebook/dinov2-small을 pooler_output까지 포함해 ONNX로 1회 export한다.

왜 직접 export하나: HF에 이미 올라와 있는 onnx-community/dinov2-small의 기본
export는 last_hidden_state만 내놓고 최종 LayerNorm이 빠져 있어, CLS 토큰을
직접 꺼내면 같은 상품 사진끼리도 유사도가 거의 0으로 나온다(검증 중 실측 확인).
pooler_output(=layernorm(sequence_output)[:, 0])을 그래프에 명시적으로 포함시켜
이 문제를 피한다.

이 스크립트는 build-time 전용이다(Docker 멀티스테이지 빌드의 model-export
스테이지에서 실행). PyTorch/transformers는 여기서만 필요하고, 런타임
이미지에는 결과 .onnx(.data) 파일과 onnxruntime만 들어간다.

사용:
    python scripts/export_embedding_model.py [출력 디렉터리, 기본 var/models]
"""

from __future__ import annotations

import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    import torch
    from transformers import Dinov2Model

    out_dir = Path(argv[0]) if argv else Path("var/models")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "dinov2_small_pooled.onnx"

    model = Dinov2Model.from_pretrained("facebook/dinov2-small")
    model.eval()

    class PooledDinov2(torch.nn.Module):
        def __init__(self, base: Dinov2Model) -> None:
            super().__init__()
            self.base = base

        def forward(self, pixel_values: torch.Tensor) -> torch.Tensor:
            return self.base(pixel_values=pixel_values).pooler_output

    wrapped = PooledDinov2(model)
    wrapped.eval()

    dummy = torch.randn(1, 3, 224, 224)
    torch.onnx.export(
        wrapped,
        dummy,
        str(out_path),
        input_names=["pixel_values"],
        output_names=["pooled_output"],
        dynamic_axes={"pixel_values": {0: "batch"}, "pooled_output": {0: "batch"}},
        opset_version=18,
    )

    # 빌드가 조용히 깨진 그래프를 만들지 않도록, 방금 만든 파일로 바로 추론해 검증한다.
    import numpy as np
    import onnxruntime as ort

    with torch.no_grad():
        expected = wrapped(dummy).numpy()
    sess = ort.InferenceSession(str(out_path), providers=["CPUExecutionProvider"])
    actual = sess.run(["pooled_output"], {"pixel_values": dummy.numpy()})[0]
    max_diff = float(np.abs(expected - actual).max())
    print(f"exported {out_path} (verify max_diff={max_diff:.2e})")
    if max_diff > 1e-3:
        print("ERROR: onnx output diverges from torch output beyond tolerance", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
