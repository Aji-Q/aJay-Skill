#!/usr/bin/env python3
"""Compose local Vision masks into lossless, original-pixel RGBA speaker PNGs.

Usage: python compose_speaker_cutouts.py --masks /tmp/jtrader-masks
Requires Pillow + NumPy; no external model, upload, or image regeneration.
Run create_speaker_masks.m for each source before invoking this composer.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import time

import numpy as np
from PIL import Image, ImageDraw

IDS = ('buffett', 'simons', 'graham', 'lynch', 'munger', 'soros', 'dalio', 'livermore')
HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def compose(mask_dir):
    started = time.monotonic()
    records = []
    for name in IDS:
        source = ASSETS / ('ajay-brand' if name in IDS[:2] else 'ajay-council') / f'{name}-portrait.png'
        rgb = Image.open(source).convert('RGB')
        mask_path = mask_dir / f'{name}.png'
        mask = Image.open(mask_path).convert('L')
        if mask.size != rgb.size:
            raise ValueError(f'Mask dimensions differ: {name}, {mask.size}, {rgb.size}')
        alpha = np.asarray(mask, dtype=np.float64).copy()
        # Remove negligible background noise and make confident interiors fully
        # opaque. Keep Vision's soft silhouette; never globally fade the face.
        alpha[alpha <= 3] = 0
        alpha[alpha >= 248] = 255
        height = rgb.height
        # Only the lower 17% dissolves into the report. Smoothstep's zero slope
        # at both ends avoids a visible horizontal join in the suit.
        t = np.clip((np.arange(height) - height * .83) / (height * .17 - 1), 0, 1)
        bottom_fade = 1 - (t * t * (3 - 2 * t))
        # The source frame clips different shoulders at different heights.
        # A fixed-width fade creates vertical rectangular sides. Instead, find
        # each cropped side and progressively widen a curved, soft edge toward
        # the lower torso. This only changes silhouette alpha, never face/body
        # RGB or the opaque central torso. Natural, uncropped outlines remain.
        side_fade = np.ones_like(alpha)
        side_profiles = {}
        yy = np.arange(height)
        xx = np.arange(rgb.width)[None, :]
        for right in (False, True):
            strip = alpha[:, -3:] if right else alpha[:, :3]
            hits = np.where(np.max(strip, axis=1) > 80)[0]
            touch = int(hits[0]) if len(hits) else height
            distance = rgb.width - 1 - xx if right else xx
            if touch < height * .88:
                progress = np.clip((yy - (touch - .03 * height)) /
                    (height * .96 - (touch - .03 * height)), 0, 1)
                progress = progress * progress * (3 - 2 * progress)
                inset = rgb.width * .035 * progress
                feather = rgb.width * (.025 + .12 * progress)
                edge_t = np.clip((distance - inset[:, None]) /
                    feather[:, None], 0, 1)
                side_profiles['right' if right else 'left'] = {
                    'frame_crop_y': touch, 'curve_applied': True,
                    'max_inset_fraction': .035,
                    'feather_fraction_range': [.025, .145],
                }
            else:
                edge_t = np.clip(distance / (rgb.width * .012), 0, 1)
                side_profiles['right' if right else 'left'] = {
                    'frame_crop_y': touch if touch < height else None,
                    'curve_applied': False,
                    'frame_feather_fraction': .012,
                }
            side_fade *= edge_t * edge_t * (3 - 2 * edge_t)
        alpha = np.rint(alpha * bottom_fade[:, None] * side_fade).astype(np.uint8)
        rgba = rgb.convert('RGBA')
        rgba.putalpha(Image.fromarray(alpha))
        output = HERE / f'{name}.png'
        rgba.save(output, optimize=True)
        # RGB is byte-identical even beneath alpha. Facial detail is not edited.
        assert np.array_equal(np.asarray(rgb), np.asarray(rgba)[..., :3])
        assert int(alpha.min()) == 0 and int(alpha.max()) == 255
        assert np.count_nonzero(alpha == 0) > alpha.size * .1
        assert np.count_nonzero(alpha == 255) > alpha.size * .2
        records.append({
            'id': name,
            'source': str(source.relative_to(ASSETS)),
            'source_sha256': digest(source),
            'output': str(output.relative_to(ASSETS)),
            'output_sha256': digest(output),
            'mask_sha256': digest(mask_path),
            'dimensions': list(rgba.size),
            'mode': 'RGBA',
            'method': 'Apple Vision VNGeneratePersonSegmentationRequest revision 1, accurate quality, native-size person mask; local alpha composition',
            'network_upload': False,
            'source_rgb_preserved_exactly': True,
            'alpha_min': int(alpha.min()), 'alpha_max': int(alpha.max()),
            'transparent_percent': round(np.mean(alpha == 0) * 100, 3),
            'opaque_percent': round(np.mean(alpha == 255) * 100, 3),
            'soft_edge_and_bottom_percent': round(np.mean((alpha > 0) & (alpha < 255)) * 100, 3),
            'bottom_fade_start_fraction': .83,
            'silhouette_treatment': 'adaptive_curved_crop_fade_v2',
            'side_profiles': side_profiles,
            'background_mask_threshold': 3,
            'opaque_mask_threshold': 248,
        })
    elapsed = round(time.monotonic() - started, 3)
    old = json.loads((HERE / 'manifest.json').read_text())
    old.update({
        'status': 'eight_local_rgba_cutouts_complete',
        'note': 'Local matting explicitly authorized by the user. Original RGB pixels preserved exactly; true alpha background and soft lower-torso fade. Prior rejected image-generation attempts retained below as provenance.',
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'method_documentation': 'https://developer.apple.com/documentation/vision/vngeneratepersonsegmentationrequest',
        'not_started': [],
        'speakers': records,
        'composition_elapsed_seconds': elapsed,
        'visual_review': {'status': 'pending_contact_sheet_review', 'themes': ['#0b1b26', '#edf2f3']},
        'limitations': [
            'Fine individual flyaway hairs may be lost by automatic segmentation; the original photographs remain available.',
            'Original portraits were already frame-cropped at shoulders/torso. The cutout preserves that source composition rather than inventing anatomy.'
        ],
    })
    (HERE / 'manifest.json').write_text(json.dumps(old, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'elapsed_seconds': elapsed, 'speakers': records}, indent=2))


def contact_sheets():
    # Actual 200px desktop and 120px mobile assets, without image enlargement.
    for theme, color, ink in [('dark', '#0b1b26', '#d9e6eb'), ('light', '#edf2f3', '#183141')]:
        sheet = Image.new('RGB', (1440, 750), color)
        draw = ImageDraw.Draw(sheet)
        for i, name in enumerate(IDS):
            image = Image.open(HERE / f'{name}.png').convert('RGBA')
            origin_x, origin_y = (i % 4) * 360, (i // 4) * 375
            draw.text((origin_x + 8, origin_y + 6), name.upper() + ' / RGBA', fill=ink)
            for size, offset in [(200, 8), (120, 224)]:
                preview = image.resize((size, int(size * 1.5)), Image.Resampling.LANCZOS)
                x, y = origin_x + offset, origin_y + 30
                sheet.paste(preview, (x, y), preview)
                draw.text((x, y + preview.height + 8), f'{size}px', fill=ink)
        sheet.save(HERE / f'contact-sheet-{theme}.png', optimize=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--masks', type=Path, required=True)
    args = parser.parse_args()
    compose(args.masks)
    contact_sheets()
