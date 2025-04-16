# Improving Planning with User-Led Learning (ULL)

This project demonstrates Portia's User-Led Learning (ULL) feature, which allows agents to learn from example plans and improve their planning capabilities over time. By providing examples of well-structured plans, you can guide the agent to create more effective plans for similar tasks in the future.

## Scripts Overview

This directory contains a series of scripts that progressively demonstrate how ULL works:

1. [01_ull_vague_prompt_no_examples.py](./01_ull_vague_prompt_no_examples.py) - Shows how Portia handles a vague prompt without any example plans, resulting in potentially suboptimal planning.

2. [02_ull_good_prompt_no_examples.py](./02_ull_good_prompt_no_examples.py) - Demonstrates how improving the prompt with more specific instructions can lead to better plans, even without examples.

3. [03_ull_static_example_plans.py](./03_ull_static_example_plans.py) - Introduces the concept of providing a static example plan to guide Portia's planning process.

4. [04_ull_create_example_plans.py](./04_ull_create_example_plans.py) - Shows how to create and store multiple example plans that can be used for future planning tasks.

5. [05_ull_vague_with_examples.py](./05_ull_vague_with_examples.py) - Demonstrates how even with a vague prompt, Portia can create effective plans by leveraging previously stored example plans.

## Getting Started

To run these examples, you'll need to have the Portia SDK installed and configured. Each script can be run independently to see the progression of planning capabilities as more examples are provided.

The examples use a refund processing scenario to demonstrate how ULL can improve an agent's ability to handle complex workflows involving customer service, policy review, and payment processing.
