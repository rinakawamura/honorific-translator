# Rules Encoded In rule_convert.py

Describes how the conversion algorithm in rule_convert.py works by describing the rules encoded in the algorithm.

## Algorithm

1. First, replace specific honorific phrases in the sentence with their regular versions.

2. Then, parse sentence using Mecab and split into parts of speech.
  - Handle Mecab formatting issues
    - Some words, such as English characters do not have a genkei (original) form. Set the genkei form equal to the word itself.
    - Some genkei forms have extra information which we do not need so remove any supplementary info.
    - Some genkei forms have unnatural kanji, incorrect kanji or kanji that is not regularly used, so fix the kanji or revert back to hiragana by looking at the KANJI dict.

3. Handle special phrases spanning multiple parts of speech first.
  - どういたしまして、良かった

4. Iterate over each part and handle according to its part of speech:

* If honorific prefix, i.e. 接頭辞 of お or 御:
  - First handle special phrases
      - ご苦労さま（です）、お疲れ様（です・でした）、お願い、お互い様、お考えです、ご存知です、お目にかかる、お会いできる
  - Then, handle special structures of 
      - お・ご（接頭辞） + 名詞　＋　になる
      - お・ご（接頭辞） + 名詞　＋　動詞
      - お・ご（接頭辞） + 動詞　＋　になる・致す・出来る
  - For everything else, simply remove the honorific prefix

* If honorific suffix, i.e. 接尾辞 of さん or 様 (i.e. honorific address):
  - Remove the honorific suffix

* If verb:
  - In the case that verb is an honorific verb look up regular form of verb
  - Modify katsuyo, i.e. conjugation form, appropriately by first handling all special cases then calling the default modify_katsuyo() function.
      - If verb followed by another verb or an auxiliary verb (助動詞):
          - Handle special cases of verbs of 居る、さ＋れる、なさ＋れる
          - Handle special cases of verbs followed by られる、てる、たい、ない、なら、た、ます
          - For all other cases, modify conjugation of verb to be that of following (auxiliary) verb
      - If verb followed by particle (助詞):
          - Check if verb is in hypothetical form (仮定系)
          - If not apply default conversion (described below)
      - For all other cases, apply default conversion (modify_katsuyo):
          - Look at conjugation type of verb parsed by Mecab and modify to type consistent with Verb.csv conjugation types
  - Handle verbs with multiple possible meanings
      - 頂く = もらう vs. くれる
  - For all other verbs, lookup the verb with the modified conjugation type in the dictionary (created from Verb.csv)
  - Append modified verb to sentence
  - Add る at end of sentence if marker set

* If noun (名詞) or proper noun (代名詞):
  - Handle special case of ご覧になる　＝＞　見る
  - Check if noun is an honorific noun that becomes a verb in regular form in NOUN_VERBS dictionary.
      - Check if word is followed by する or になる and handle these cases appropriately.
  - For all other cases,
      - Check if noun is an honorific noun in which case, convert to regular form
      - Append original or converted noun to final sentence

* If auxiliary verb (助動詞):
  - Handle special auxiliary verbs of だろう、です、な（のです）、ます
  - For all other cases,
      - Append word as is to final sentence

* If particle (助詞):
  - Remove か from end of sentence when appropriate (indicated by marker and position in sentence)
  - Change ん to の
  - Change ので to から
  - For all other cases,
      - Append word as is to final sentence

* For all other parts of speech:
  - Check if word in honorific form and convert to regular form if it is
  - Append converted word or word as is to final sentence

5. Post-edit sentence.
  - Fix た to be だ and て to be で if following words that end in 五段-マ行 or 五段-バ行 (eg. 読んで)

## Other Notes on Conversion Program
- Input sentence must have punctuation at the end because some cases check position of words in sentence (eg. If word is last word in sentence.)

