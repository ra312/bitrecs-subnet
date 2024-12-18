<div align="center">

# Bitrecs Subnet 

<img src="docs/light-logo.svg#gh-light-mode-only" width="400" height="auto" alt="Bitrecs Logo"/>
<img src="docs/dark-logo.svg#gh-dark-mode-only" width="400" height="auto" alt="Bitrecs Logo"/>

[![Discord Chat](https://img.shields.io/discord/308323056592486420.svg)](https://discord.gg/bittensor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 

[Discord](https://discord.gg/bittensor) • [Network](https://taostats.io/) • [Research](https://bittensor.com/whitepaper)
</div>

## Introduction
Bitrecs is a novel recommendation engine built on the Bittensor network. Our implementation provides a framework for serving e-commerce recommendations via the latest LLMs. Miners are encouraged to experiement with their own implementations to improve latency and quality. 

## Product
The subnet operates through an incentive mechanism where miners produce arrays of product SKUs from a given input SKUs, a catalogue of store inventory and (when applicable) supplementary user browsing history. The protocol enables:

- Easy integration for e-commerce shop owners through our propriatary WooCommerce and Shopify plugins
- Base miner class with support for several popular LLM models and providers
- API proxy layer serving requests from ecommerce sites to the bittensor network

## Incentive
The incentive mechanism ranks miner responses by qualitative metrics and sales events like

- Diversity of recs
- Latency to response
- Quality of responses (recs cannot be hallucinated, recs cannot be dupes, etc)
- Coherence to prompt parameters (seasonality, gender etc)
- End user actions such as add to cart and order checkout

## Getting Started

### Mining
Want to earn tao by mining? Check out our [mining guide](docs/running_miner.md) to get started.

### Validating 
Interested in running a validator? See our [validator setup instructions](docs/running_validator.md) for details.

### Testing

``` 
Ensure you have the sample .json and .csv files in the /tests/data folder

pytest ./tests/test_json.py -s
pytest ./tests/test_llm.py -s
pytest ./tests/test_llm.py -s -k 'test_call_local_llm_with_20k'
 ```


## License

This repository is licensed under the MIT License.
```text
# The MIT License (MIT)
# Copyright © 2024 Yuma Rao
# Copyright © 2024 Bitrecs

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
