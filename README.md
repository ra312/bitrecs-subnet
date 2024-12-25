<div align="center">

# Bitrecs Subnet 

<img src="docs/light-logo.svg#gh-light-mode-only" width="400" height="auto" alt="Bitrecs Logo"/>
<img src="docs/dark-logo.svg#gh-dark-mode-only" width="400" height="auto" alt="Bitrecs Logo"/>

[![Discord Chat](https://img.shields.io/discord/308323056592486420.svg)](https://discord.gg/bittensor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 

[Discord](https://discord.gg/bittensor) • [Network](https://taostats.io/) • [Research](https://bittensor.com/whitepaper)
</div>

## Introduction
Bitrecs is a novel <a href="https://www.perplexity.ai/search/recommendation-engine-NpaNi7MHQ5OFA.btgIQ4QQ" target="_blank">recommendation engine</a> built on the Bittensor network. Our implementation provides a framework for serving e-commerce recommendations via the latest LLMs. Miners are encouraged to experiment with their own implementations to improve latency and quality. 

## Goal
**Maximize sales for online retailers (merchants)**

Common objectives shared by merchants:

1) Increase add to carts (engagement)
2) Increase the number of customers who complete an order (conversion rate)
3) Increase the average size of cart (average order value)

This subnet is dedicated to maximizing these 3 goals for online merchants using existing store data and traffic (onsite). 

## Problem
Global e-commerce is a ~20T market with a 15% CAGR. A large portion of online sales are directly attributed to onsite recommendations (e.g customers who bought x also bought y, bundled products, last minute checkout items etc). Famously, Amazon attributes <a href="https://www.perplexity.ai/search/how-much-does-amazon-product-r-ccxRVV5OReGL_12_QzBGzQ" target="_blank">35% of their total online sales</a> to their proprietary recommendation engine.  Unfortunately this engine is out of reach for most online retailers who are operating on smaller platforms (e.g Shopify, Woocommerce etc) which have their own recommendation solutions and widgets, often using older rules-based technology.

This problem is a subset of the much larger General Recommendation space which powers most of the Internet today (think Netflix movie recommendations, TikTok reels, Google search suggestions, etc)

We are addressing a more narrow but equally important area of e-commerce - [onsite product recommendations for merchants](https://www.perplexity.ai/search/onsite-product-recommendations-PmY8e84GSxavnmdSW9934A)

## Solution
Bitrecs aims to tap into the intelligence of the Bittensor network to service product recommendations for retailers directly via miners using novel methods. 

Our first generation solution uses prompting and ICL to coerce recs from the latest LLMs. We believe LLM's are best suited for this task as they excel at cold-start, one/zero shot learning which is often the weakness of legacy rec engines using older methods (collaborative filtering, content-based filtering etc).

Additionally, many LLM's have encoded valuable information about shopping cohorts, seasonality, brand affinities, customer journeys etc which we try to unlock using prompting.  The recent advances in context window size has opened up the door for this type of solution as we essentially ask 'given this customer scenario and this set of products, pick X next products the customer would buy'. 

As we evolve this network we get closer to **1-to-1 marketing** which is viewed as the holy grail of marketing (imagine every product page you view on the web as personalized just for you, without being invasive or exploitive).  Amazon is close to this experience but falls short in many areas - not to any fault of their own, but they often sell the same products their merchants sell and this creates a conflict of interest.  

Smaller retailers need access to this technology to remain competitive, and our solution is built to work with existing onsite catalogs (we never recommend 3rd party products or divert traffic to other sites - this is critical to winning merchants trust)

Everything has been designed to offer the merchant a free and simple plugin that works out of the box on product pages, while hiding all the complexity and abstractions of Bittensor away from them so they can continue to focus on selling and running an online business.  Doing so allows our miners focus on competing and evolving the prompting science to product increasingly valuable and timely product recommendations.


## Product
The subnet operates through an incentive mechanism where miners produce arrays of product SKUs from a given input SKUs, a catalog of store inventory and (when applicable) supplementary user order history. The protocol enables:

- Easy integration for e-commerce shop owners through our WooCommerce and Shopify plugins
- Base miner class with support for several popular LLM models and providers
- Validator API proxy for marshalling requests between e-commerce sites and the bittensor network

## Incentive
The incentive mechanism ranks miner responses by performance metrics and sales events such as:

- Latency to response
- Diversity of recs
- Quality of responses (recs cannot be hallucinated, recs cannot be dupes, etc)
- Coherence to prompt parameters (seasonality, gender etc)
- End user actions such as add to cart and order checkout

## Opportunity

We think this is a great opportunity to showcase the power of Bittensor incentives with e-commerce and to create a fully aligned network of parties and incentives - an elegant flywheel of value. The barrier to entry for miners is low on this network as a GPU is **not required** to mine. Miners are allowed (and often encouraged) to call LLMs via APIs as the initial bootstrap of the network will mostly be driven for speed and accuracy.

Over time, as the baseline gets set (i.e quality recs at a max request time < 3 seconds) the sales focused incentive mechanism drives miners to search and compete for more impactful recommendations. We hope that we can fine tune and balance the incitive mechanism to achieve a network that is always performing a 'best effort' on every request, with outsized rewards given to top performers which drive real, measurable value for merchants and helping them compete with the incumbents - a win for every party invovled.


## Roadmap

### Q1 2025

Testnet (Jan)
- launch testnet with v1 engine supporting Shopify/Woocommerce
- iterate, refine and balance incentive mechanism
- complete merchant/miner/validator portal for easy onboarding

Mainnet (Feb-March)

- launch on mainnet baring any critical design/incentive flaws
- establish baselines for quality of service and uptime across the subnet
- improve and harden onsite metrics tracking

### Q2 2025

- aggressively market and onboard merchants
- integrate additional platforms (magento, bigcommerce, wix)
- evolve the V1 engine with new prompting and models, miner innovations

### Q3 2025

- explore potential Fiber rewrite / V2


## Getting Started

### Mining
Want to earn tao by mining? Check out our [mining guide](docs/running_miner.md) to get started.

### Validating 
Interested in running a validator? See our [validator setup instructions](docs/running_validator.md) for details.

### Testing

``` 
Ensure you have the sample .json and .csv files in the /tests/data folder

pytest ./tests/test_json.py -s --durations=0
pytest ./tests/test_llm.py -s --durations=0
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
