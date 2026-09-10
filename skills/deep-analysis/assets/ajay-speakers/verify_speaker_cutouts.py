#!/usr/bin/env python3
"""Verify installed portrait RGBA assets against unchanged source photographs."""
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent
manifest = json.loads((HERE / 'manifest.json').read_text())
expected = {'buffett', 'simons', 'graham', 'lynch', 'munger', 'soros', 'dalio', 'livermore'}
assert {row['id'] for row in manifest['speakers']} == expected
for row in manifest['speakers']:
    source = ASSETS / row['source']
    output = ASSETS / row['output']
    assert sha256(source.read_bytes()).hexdigest() == row['source_sha256']
    assert sha256(output.read_bytes()).hexdigest() == row['output_sha256']
    with Image.open(source) as src, Image.open(output) as out:
        assert out.mode == 'RGBA'
        assert out.size == src.size == (1024, 1536)
        original = np.asarray(src.convert('RGB'))
        actual = np.asarray(out)
    assert np.array_equal(actual[..., :3], original), row['id'] + ': RGB changed'
    alpha = actual[..., 3]
    assert alpha.min() == 0 and alpha.max() == 255
    assert (alpha[0, :] == 0).all(), row['id'] + ': opaque top background'
    assert (alpha[-1, :] == 0).all(), row['id'] + ': no bottom fade'
    assert (alpha[:, 0] == 0).all() and (alpha[:, -1] == 0).all()
    # Manually checked central face region shared by these fixed portraits.
    assert (alpha[400:580, 450:600] == 255).all(), row['id'] + ': translucent face'
    assert (alpha[900:1180, 440:600] == 255).all(), row['id'] + ': translucent central torso'
    assert row['silhouette_treatment'] == 'adaptive_curved_crop_fade_v2'
    for key, measure in [('transparent_percent', alpha == 0),
                         ('opaque_percent', alpha == 255),
                         ('soft_edge_and_bottom_percent', (alpha > 0) & (alpha < 255))]:
        assert abs(round(float(measure.mean()) * 100, 3) - row[key]) < .001
    print(row['id'], 'RGBA/source/alpha/opaque-face/hash PASS')
print('8 / 8 installed speaker assets verified.')
