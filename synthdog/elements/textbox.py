"""
Donut
Copyright (c) 2022-present NAVER Corp.
MIT License
"""
import string

import numpy as np
from synthtiger import layers


class TextBox:
    def __init__(self, config):
        self.fill = config.get("fill", [1, 1])

    def generate(self, size, text, font):
        width, height = size

        char_layers, chars = [], []
        word_quads = []
        fill = np.random.uniform(self.fill[0], self.fill[1])
        width = np.clip(width * fill, height, width)
        font = {**font, "size": int(height)}
        left, top = 0, 0

        while True:
            # construct a full word:
            # take from the text iterator until a whitespace occurs
            word = []
            while (char := next(text)) not in string.whitespace:
                word.append(char)
            word = ''.join(word).strip()
            if not word:
                continue  # discard empty words

            char_layer = layers.TextLayer(word, **font)
            char_scale = height / char_layer.height
            char_layer.bbox = [left, top, *(char_layer.size * char_scale)]
            if char_layer.right > width:
                # if box would get overfilled, reset the iterator to the beginning of the word and break
                for _ in word + " ":
                    text.prev()
                break

            char_layers.append(char_layer)
            chars.append(word)
            word_quads.append(char_layer.quad)
            left = char_layer.right

            # draw a whitespace but don't add to the list of quads
            char_layer = layers.TextLayer(' ', **font)
            char_scale = height / char_layer.height
            char_layer.bbox = [left, top, *(char_layer.size * char_scale)]
            if char_layer.right > width:
                break

            char_layers.append(char_layer)
            left = char_layer.right

        text = chars
        if len(char_layers) == 0 or len(text) == 0:
            return None, None, None

        text_layer = layers.Group(char_layers).merge()

        return text_layer, text, word_quads
