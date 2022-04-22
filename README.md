# Honorific Translator

This is the repository for a project to create a neural Japanese style translator to convert from regular-styled Japanese sentences to honorific-styled Japanese sentences. Please the report in the repository for more details.

## Repository Structure

### Data Directory (data)
This directory contains the pseudo-parallel dataset that I have created. They are split according to the corpora from which I retreived the original sentences, as well as by the train, dev, test splits used for training the neural models.

### Parallel Corpus (parallel_corpus)
This directory contains the files needed to apply the rule-based conversion to honorific sentences to retrieve the regular sentences (rule_convert.py), which is part of the process that I used to create the parallel corpus. The markdown file, rules.md, contains a description of the rules encoded in this file. There is also a categorization algorithm (categorize.py) which is the program I used to distinguish honorific sentences from the corpora. Please install the Japanese morphological analyzer, MeCab to run the programs.

### Neural Models (neural_models)
This directory contains Python notebooks to train the three neural translation models (OpenNMT's LSTM and Transformer from scratch, Finetuned GPT-II). It is recommended to run them on Colab to use their GPU. It is indicated in the notebooks where to modify for your own use (specify paths).
