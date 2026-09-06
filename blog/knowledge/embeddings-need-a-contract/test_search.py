import pytest
from search import rank


def test_lexical_signed_vector_fusion_and_contract():
    manifest = dict(
        model_revision="fixture-v1",
        tokenizer_revision="none",
        pooling="fixture",
        dimension=2,
    )
    index = dict(
        manifest=manifest,
        documents=[
            dict(id="a", text="byte model", vector=[1, 0]),
            dict(id="b", text="other text", vector=[-1, 0]),
        ],
    )
    result = rank("byte", index, [1, 0], manifest)
    assert result["lexical"][0][0] == "a" and result["vector"][1][1] == -1
    assert result["hybrid"][0][0] == "a"
    with pytest.raises(ValueError):
        rank("byte", index, [1, 0], dict(manifest, model_revision="v2"))
    assert rank("unknown", index)["hybrid"] == []
