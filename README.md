<div align="center">

# Bitrecs Recommendation Engine 

<img src="docs/light-logo.svg#gh-light-mode-only" width="400" height="auto" alt="Bitrecs Logo"/>
<img src="docs/dark-logo.svg#gh-dark-mode-only" width="400" height="auto" alt="Bitrecs Logo"/>

[![Discord Chat](https://img.shields.io/discord/308323056592486420.svg)](https://discord.gg/bittensor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 

[Discord](https://discord.gg/bittensor) • [Network](https://taostats.io/) • [Research](https://bittensor.com/whitepaper)
</div>

## Introduction
Btrecs is an enterprise grade recommendation engine build on the bittensor network. Our implementation provides a framework for serving e-commerce recommendations (recs) via various state of the art LLMs (large language models). Miners are encouraged to experiement with their own implementations to improve latency and quality. 

## Product
The subnet operates through an incentive mechanism where miners produce arrays of product SKUs from a given input SKU and a catalogue of store inventory and (when applicable) supplementary user browsing history. The protocol enables:

- Easy integration for e-commerce shop owners through free propriatary WooCommerce and Shopify plugins
- Base miner class with support for several popular LLM models and providers, out of the box
- API layer serving requests from our plugins to the bittensor network

## Incentive
The incentive mechanism ranks miner responses by qualitative metrics and sales events such as

- Latency to response
- Quality of responses (recs cannot be hallucinated, recs cannot be dupes, etc) 
- Were any products added to cart, clicked on, purchased

## Getting Started

### Mining
want to earn tao by mining? check out our [mining guide](docs/running_miner.md) to get started.

### Validating 
interested in running a validator? see our [validator setup instructions](docs/running_validator.md) for details.

## License

This repository is licensed under the MIT License.
```text
# The MIT License (MIT)
# Copyright © 2024 Yuma Rao
# Copyright © 2024 Macrocosmos AI

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
```
