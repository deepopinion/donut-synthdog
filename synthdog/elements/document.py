"""
Donut
Copyright (c) 2022-present NAVER Corp.
MIT License
"""
import numpy as np
from synthtiger import components

from elements.content import Content
from elements.paper import Paper

from synthtiger.layers import Group
import cv2

class Document:
    def __init__(self, config):
        self.fullscreen = config.get("fullscreen", 0.5)
        self.landscape = config.get("landscape", 0.5)
        self.short_size = config.get("short_size", [480, 1024])
        self.aspect_ratio = config.get("aspect_ratio", [1, 2])
        self.paper = Paper(config.get("paper", {}))
        self.content = Content(config.get("content", {}))
        self.effect = components.Iterator(
            [
                components.Switch(components.ElasticDistortion()),
                components.Switch(components.AdditiveGaussianNoise()),
                components.Switch(
                    components.Selector(
                        [
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                        ]
                    )
                ),
            ],
            **config.get("effect", {}),
        )

    def generate(self, size):
        width, height = size
        fullscreen = np.random.rand() < self.fullscreen

        if not fullscreen:
            landscape = np.random.rand() < self.landscape
            max_size = width if landscape else height
            short_size = np.random.randint(
                min(width, height, self.short_size[0]),
                min(width, height, self.short_size[1]) + 1,
            )
            aspect_ratio = np.random.uniform(
                min(max_size / short_size, self.aspect_ratio[0]),
                min(max_size / short_size, self.aspect_ratio[1]),
            )
            long_size = int(short_size * aspect_ratio)
            size = (long_size, short_size) if landscape else (short_size, long_size)

        text_layers, texts, word_quads = self.content.generate(size)
        paper_layer = self.paper.generate(size)
        meta = self.effect.apply([*text_layers, paper_layer])

        def apply_to_quads(quads, layers, meta=None):
            """
            Adapted from synthtiger.components.Perspective().apply.

            Use the meta dict given back by the effect function to calculate the effect on the word bounding quads.
            """

            pxs = meta["pxs"]
            percents = meta["percents"]
            aligns = meta["aligns"]

            aligns = np.tile(aligns, 4)[:4]
            if pxs is not None:
                pxs = np.tile(pxs, 4)[:4]
            if percents is not None:
                percents = np.tile(percents, 4)[:4]

            group = Group(layers)
            sizes = np.tile(group.size, 2)
            new_sizes = np.tile(group.size, 2)

            if pxs is not None:
                new_sizes += pxs
            elif percents is not None:
                new_sizes *= percents

            values = (sizes - new_sizes) / 2
            aligns *= np.abs(values)
            offsets = [
                [values[0] + aligns[0], values[3] + aligns[3]],
                [-values[0] + aligns[0], values[1] + aligns[1]],
                [-values[2] + aligns[2], -values[1] + aligns[1]],
                [values[2] + aligns[2], -values[3] + aligns[3]],
            ]

            origin = group.quad
            quad = np.array(origin + offsets, dtype=np.float32)
            matrix = cv2.getPerspectiveTransform(origin, quad)

            transformed_quads = []
            for q in quads:
                q = np.append(q, np.ones((4, 1)), axis=-1).dot(matrix.T)
                transformed_quads.append(q[..., :2] / q[..., 2, np.newaxis])

            return transformed_quads

        transformed_quads = apply_to_quads(word_quads, [*text_layers, paper_layer], meta=meta['metas'][2]['meta']['meta'])

        return paper_layer, text_layers, texts, transformed_quads
