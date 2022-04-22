# Program to apply rule-based conversion from honorific to non-honorific form.

import MeCab
import json
from globals import NOUNS, NOUN_VERBS, VERBS, KANJI, REPLACE, SPECIAL, E_SOUNDS

def parse(sent):
    ''' Parse sentence using part of speech tagger and morphological analyzer and return a list of the original input, original form, part of speech, and conjugation for each word in the sentence.'''
    tagger = MeCab.Tagger('-Ochasen')
    node = tagger.parseToNode(sent)
    sentence, genkei, hinshi, hinshi2, katsuyo, row = [], [], [], [], [], []
    while node:
        word = node.surface
        wclass = node.feature.split(",")
        # print(wclass)
        if not wclass[0] == "BOS/EOS":
            # Extract necessary details about the words using MeCab
            sentence.append(word) # Input sentence
            genkei.append(None if len(wclass) <= 7 else wclass[7]) # Original word form
            hinshi.append(None if len(wclass) <= 0 else wclass[0]) # Part of speech
            hinshi2.append(None if len(wclass) <= 2 else wclass[2]) # Part of speech type (extra detail)
            katsuyo.append(None if len(wclass) <= 5 else wclass[5]) # Conjugation
            row.append(None if len(wclass) <= 4 else wclass[4]) # Word row (eg. か行)
        node = node.next
    return sentence, genkei, hinshi, hinshi2, katsuyo, row

def initial_replace(sent):
    '''Delete and make replacements for words unique to honorifics'''
    # 例えば　よろしくお願い致します　＝＞　よろしく
    # String replace special phrases
    for word in REPLACE.keys():
        if word in sent:
            sent = sent.replace(word, REPLACE[word])
    return sent

def modify_katsuyo(genkei, katsuyo, verb_index):
    ''' Select the correct conjugation type of regular verb by looking at conjugation type of honorific verb and following words'''
    # print("Modify")
    if katsuyo[verb_index] == "終止形-一般" or katsuyo[verb_index] == "連体形-一般":
        return "基本形"
    elif katsuyo[verb_index] == "未然形-一般":
        return "未然形"
    elif katsuyo[verb_index] == "連用形-促音便":
        return "連用タ接続"
    elif katsuyo[verb_index] in ["連用形-一般", "連用形-イ音便", "連用形-撥音便"]:
        if katsuyo[verb_index + 1] == "命令形" or genkei[verb_index + 1] == "た" or genkei[verb_index + 1] == "て":
            return "連用タ接続"
        elif katsuyo[verb_index + 1] == "終止形-一般":
            return "基本形"
        elif genkei[verb_index + 1] == "ます":
            if genkei[verb_index + 2] == "た" or genkei[verb_index + 2] == "て":
                return "連用タ接続"
            else:
                return "基本形"
        else:
            return "連用形"
    elif katsuyo[verb_index] == "命令形":
        return "命令ｅ"
    elif katsuyo[verb_index] == "意志推量形":
        return "未然ウ接続"
    return "基本形"

def hon_verb(word):
    ''' Look up honorific verb and return original if not present in dictionary.'''
    return VERBS[word] if word in VERBS else word

def lookup(verb, katsuyo):
    '''Lookup verb with correct conjugation in verb conjugation dictionary Return original verb if conjugation not present in dictionary'''
    # print(verb, katsuyo)
    if verb in CONJ:
        if katsuyo == "未然ウ接続":
            if katsuyo in CONJ[verb]:
                return CONJ[verb]["未然ウ接続" if katsuyo in CONJ[verb] else "未然形"] + 'う'
        elif katsuyo in CONJ[verb]:
            return CONJ[verb][katsuyo]
        elif katsuyo == "連用タ接続" and "連用形" in CONJ[verb]:
            return CONJ[verb]["連用形"]
    return verb

def delete(sentence, genkei, hinshi, hinshi2, katsuyo, row, s, e):
    del sentence[s:e]
    del genkei[s:e]
    del hinshi[s:e]
    del hinshi2[s:e]
    del katsuyo[s:e]
    del row[s:e]
    return sentence, genkei, hinshi, hinshi2, katsuyo, row

def convert(sent):
    parsed = initial_replace(sent)
    fin_sent = []
    print(parsed)
    sentence, genkei, hinshi, hinshi2, katsuyo, row = parse(parsed)
    # print(sentence)
    # print(genkei)
    # print(hinshi)
    # print(hinshi2)
    # print(katsuyo)
    # print(row)
    remove_ka = True
    i = 0
    while i < len(sentence):
        # Handle Mecab formatting (sometimes genkei form doesn't exist or contains extra information not necessary)
        if not genkei[i]: genkei[i] = sentence[i]
        if '-' in genkei[i]:
            genkei[i] = genkei[i].split('-')[0]
        
        # Revert unnatural kanji (converted by Mecab) back into hiragana or into correct kanji
        if genkei[i] in KANJI.keys():
            genkei[i] = KANJI[genkei[i]]
        
        # Handle special phrases spanning multiple parts of speech
        # Unique case of どういたしまして, a phrase which only has an honorific form
        if sentence[i] == 'どう' and sentence[i+1] == 'いたし' and sentence[i+2] == 'まし' and sentence[i+3] == 'て':
            fin_sent.append("どういたしまして") 
            i += 4
            continue
        # Special case of 良かった
        if (sentence[i] == "良かっ" or sentence[i] == "よかっ") and (sentence[i+1] == "た" or sentence[i+1] == "たら"):
            fin_sent.append(sentence[i])
            fin_sent.append(sentence[i+1])
            i += 2
            continue

        # Handle different parts of speech separately
        if hinshi[i] == '接頭辞' and genkei[i] == 'お' or genkei[i] == '御':
            # Deal with special cases
            # ご苦労様（です）
            if genkei[i+1] == "苦労" and genkei[i+2] == "様":
                fin_sent.append("ご苦労")
                i += 4 if genkei[i+3] == "です" else 3
                continue
            # お疲れ様（です・でした）
            if genkei[i+1] == "疲れ" and genkei[i+2] == "様":
                fin_sent.append("お疲れ")
                if sentence[i+3] == "です":
                    i += 4
                elif sentence[i+3] == "でし" and sentence[i+4] == "た":
                    i += 5
                else:
                    i += 3
                continue
            # お願い
            elif genkei[i+1] == "願う":
                fin_sent.append("お願い")
                i += 2
                continue
            # お互い様
            elif genkei[i+1] == "互い" and genkei[i+2] == "様":
                fin_sent.append("お互い様")
                i += 3
                continue
            # お考えです
            elif genkei[i+1] == "考え" and genkei[i+2] == "です": #お考えですか
                fin_sent.append("考えてる")
                i += 3
                continue
            # ご存知です　＝＞　知ってる
            elif genkei[i+1] == "存知":
                fin_sent.append("知ってる")
                i += 3 if genkei[i+2] == "です" or genkei[i+2] == "の" else 2
                continue
            # お目にかかる
            elif genkei[i+1] == "目" and genkei[i+2] == "に" and genkei[i+3] == "掛かる":
                # Change verb to 会う and modify katsuyo to be the same as 掛かる
                sentence[i+1], genkei[i+1], hinshi[i+1] = "会う", "会う", "動詞" # Make it a verb
                katsuyo[i+1] = katsuyo[i+3]
                sentence, genkei, hinshi, hinshi2, katsuyo, row = delete(sentence, genkei, hinshi, hinshi2, katsuyo, row, i+2, i+4) 
                i += 1
                continue
            # お会いできる
            elif genkei[i+1] == "会う" and genkei[i+2] == "出来る":
                fin_sent.append("会える")
                i += 3
                continue

            # Deal with special case of お・ご（接頭辞） + 名詞　＋　動詞　or になる
            elif hinshi[i+1] == "名詞":
                if hinshi[i+2] == "動詞":
                    if hinshi2[i+1] == "サ変可能" and hon_verb(genkei[i+2]) != "為る": # 動詞がするの意味を持つ場合以外してを足す　（例）ご相談頂く＝＞相談してもらう
                        fin_sent.append(sentence[i+1]) # Add noun
                        fin_sent.append("して")
                        i += 2
                        continue
                    elif hinshi2[i+1] == "一般": #「を」を足す（例）お礼申し上げる　＝＞　礼を言う
                        fin_sent.append(sentence[i+1]) # Add noun
                        fin_sent.append("を")
                        i += 2
                        continue
            
            # Deal with special case of お・ご（接頭辞） + 動詞　＋　になる・致す・出来る
            elif hinshi[i+1] == "動詞":
                if hon_verb(genkei[i+2]) == "為る":
                    katsuyo[i+1] = katsuyo[i+2] # Modify conjugation of verb to be that of the following verb
                    sentence, genkei, hinshi, hinshi2, katsuyo, row = delete(sentence, genkei, hinshi, hinshi2, katsuyo, row, i+2, i+3) # Delete following verb
                    sentence[i+1] = genkei[i+1]
                elif genkei[i+2] == "に" and genkei[i+3] == "成る":
                    katsuyo[i+1] = katsuyo[i+3]
                    sentence, genkei, hinshi, hinshi2, katsuyo, row = delete(sentence, genkei, hinshi, hinshi2, katsuyo, row, i+2, i+4)
                elif genkei[i+2] == "出来る":
                    # eg. お送り出来る　＝＞　送れる
                    fin_sent.append(lookup(genkei[i+1], "仮定形"))
                    fin_sent.append("る")
                    i += 3
                    continue
                elif hinshi[i+2] == "動詞":
                    verb_conj = lookup(hon_verb(genkei[i+1]), "連用タ接続")
                    fin_sent.append(verb_conj)
                    fin_sent.append("て")
                    i += 2
                    continue
            # Don't append beautification prefixes
            i += 1
            continue

        elif hinshi[i] == '接尾辞' and (genkei[i] == 'さん' or genkei[i] == '様'):
            # Don't append beautification suffixes
            i += 1
            continue

        elif hinshi[i] == '動詞':
            # Handle 連体形 verbs first (not in Verbs.csv so must change genkei)
            if katsuyo[i] == '連体形-一般' and sentence[i] in CONJ:
                genkei[i] = sentence[i]

            add_ru = False # Marker to keep track of whether to add る at end of sentence

            # In the case that the verb is in honorific form, lookup regular form of verb in verb dictionary and lookup correct conjugated form of that verb
            regular_verb = hon_verb(genkei[i])
    
            # Set default conjugation form to original returned by Mecab
            new_katsuyo = katsuyo[i]

            #Handle special cases for when (auxiliary) verb follows verb
            if hinshi[i+1] == "助動詞" or hinshi[i+1] == "動詞" or hinshi[i+1] == "形容詞":
                # Special case for verb of 居る
                if genkei[i] == "居る": 
                    new_katsuyo = "連用形"
                    if genkei[i+1] == "ます":
                        add_ru = True
                # Special case for verb phrase される・なされる
                elif (sentence[i] == 'さ' or sentence[i] == 'なさ') and genkei[i+1] == "れる" and i > 0 and hinshi[i-1] == "名詞":
                    fin_sent.append('さ')
                    i += 1
                    continue
                # Special case for verb followed by られ
                elif genkei[i+1] == "られる":
                    fin_sent.append(sentence[i])
                    fin_sent.append(sentence[i+1])
                    i += 2
                    continue
                # Special case for verbs followed by てる (eg. 作ってる)
                elif genkei[i+1] == "てる": 
                    fin_sent.append(sentence[i])
                    fin_sent.append(sentence[i+1])
                    i += 2
                    continue
                # Special case for verbs followed by たい (eg. 頂きたい)
                elif genkei[i+1] == "たい": 
                    new_katsuyo = "連用形"
                # Special case for verbs followed by ない (eg. いない)
                elif genkei[i+1] == "ない" or genkei[i+1] == "無い": 
                    new_katsuyo = "未然形"
                # Special case for verbs followed by なら (eg. 考えるなら)
                elif sentence[i+1] == "なら":
                    new_katsuyo = "基本形"
                # Special case for verbs followed by た
                elif genkei[i+1] == "た":
                    if katsuyo[i+1] == "連体形-一般":
                        new_katsuyo = modify_katsuyo(genkei, katsuyo, i)
                    else:
                        new_katsuyo = "連用タ接続"
                # Special case for hypothetical verbs (which can't be distinguished by Mecab) followed by ます
                elif genkei[i+1] == 'ます' and katsuyo[i+1] == '終止形-一般' and sentence[i][-1] in E_SOUNDS:
                    # Set conjugation type for verbs ending in え to 仮定系 and add sentence ending る
                    new_katsuyo = "仮定形"
                    add_ru = True
                # All other cases 
                else:
                    # Modify conjugation of verb to be that of the following (auxiliary) verb
                    katsuyo[i] = katsuyo[i+1]
                    sentence, genkei, hinshi, hinshi2, katsuyo, row = delete(sentence, genkei, hinshi, hinshi2, katsuyo, row, i+1, i+2)
                    new_katsuyo = modify_katsuyo(genkei, katsuyo, i)
           
            # Case of verb followed by ば
            elif hinshi[i+1] == "助詞":
                if genkei[i+1] == 'ば' and sentence[i][-1] in E_SOUNDS:
                    new_katsuyo = "仮定形"  # Set conjugation type for verbs ending in え to 仮定系
                else:
                    new_katsuyo = modify_katsuyo(genkei, katsuyo, i)

            else:
                new_katsuyo = modify_katsuyo(genkei, katsuyo, i)

            # Handle verbs with multiple possible meanings
            if genkei[i] == "頂く" and i-2 >= 0 and sentence[i-2] == "し" and sentence[i-1] == "て" and hinshi[i+1] != "助動詞": # 頂く＝＞くれて when した　＋　頂く　＋　non-助動詞（例）して頂いてありがとうございます
                fin_sent.append("くれて")
                i += 1
                continue

            # Conjugate verb and add to output sentence
            verb_conj = lookup(regular_verb, new_katsuyo)
            fin_sent.append(verb_conj)

            if add_ru: #例）思えます=>思える
                fin_sent.append('る')

            i += 1
            continue

        elif hinshi[i] == '名詞' or hinshi[i] == '代名詞':
            # Handle special cases
            # ご覧になる
            if genkei[i] == '御覧' and genkei[i+1] == 'に' and genkei[i+2] == '成る':
                # Skip ご覧 + に and change 成る to 見る keeping the katsuyo the same
                genkei[i+2] = "見る"
                i += 2
                continue
            # Check if honorific noun that gets converted into regular verb
            elif genkei[i] in NOUN_VERBS:
                if genkei[i+1] == "為る":
                    # eg. 拝見する・拝読する　＝＞　見る・読む
                    # Modify verb katsuyo to be that of 為る and delete 為る
                    katsuyo[i] = katsuyo[i+1]
                    sentence, genkei, hinshi, hinshi2, katsuyo, row = delete(sentence, genkei, hinshi, hinshi2, katsuyo, row, i+1, i+2)
                    new_katsuyo = modify_katsuyo(genkei, katsuyo, i)
                    verb_conj = lookup(NOUN_VERBS[genkei[i]], new_katsuyo)
                    fin_sent.append(verb_conj)
                    i += 1
                    continue
                elif genkei[i+1] == "に" and genkei[i+2] == "成る":
                    # eg. お考えになる・お座りになる
                    # Change the next word, i.e. に, to be the regular verb form of the noun and modify the katsuyo to be the same as 成る
                    sentence[i+1], genkei[i+1], hinshi[i+1] = NOUN_VERBS[genkei[i]], NOUN_VERBS[genkei[i]], "動詞" # Make it a verb
                    katsuyo[i+1] = katsuyo[i+2]
                    sentence, genkei, hinshi, hinshi2, katsuyo, row = delete(sentence, genkei, hinshi, hinshi2, katsuyo, row, i+2, i+3) 
                    i += 1
                    continue
            # Otherwise, if noun is in honorific form, replace with regular form
            fin_sent.append(NOUNS[genkei[i]] if genkei[i] in NOUNS else sentence[i])
            i += 1
            continue

        elif hinshi[i] == '助動詞':
            # Handle special auxiliary verbs appropriately
            # Keep か at end of sentence if preceded by だろう
            if sentence[i] == "だろう":
                remove_ka = False
            # Change です＝＞だ avoiding special cases where sentence ends in ですか or preceded by たい
            if genkei[i] == 'です':
                if hinshi[i-1] != "形容詞" and sentence[i-1] != 'た':
                    if sentence[i+1] == 'た':
                        fin_sent.append('だっ')
                    elif sentence[i+1] == 'の':
                        fin_sent.append('な')
                    elif sentence[i+1] == 'か':
                        if hinshi[i-1] not in ["名詞", "代名詞"]:
                            remove_ka = False
                    elif not (sentence[i-1] == 'たい' or sentence[i+1] == 'よ' or sentence[i+1] == 'ね' or (sentence[i+1] == 'し' and hinshi[i-1] == '形容詞')):
                        fin_sent.append('だ')
            # Change なので to だから
            elif sentence[i] == 'な' and genkei[i+1] == 'の' and sentence[i+2] == 'で' and genkei[i+2] == 'だ':
                fin_sent.append('だから')
                i += 2
            # Remove ます
            elif genkei[i] == 'ます':
                if katsuyo[i-1] == '連用形-一般' and fin_sent[-1][-1] in E_SOUNDS:
                    fin_sent.append("る") 
            else:
                fin_sent.append(sentence[i])
            i += 1
            continue

        elif hinshi[i] == '助詞':
            # Remove か if at end of sentence
            if genkei[i] == 'か' and i+2 == len(sentence) and remove_ka:
                i += 1
            # Change ん to の
            elif sentence[i] == 'ん':
                fin_sent.append(genkei[i])
                i += 1
            # Change ので to から
            elif genkei[i] == 'の' and sentence[i+1] == 'で' and genkei[i+1] == 'だ':
                fin_sent.append('から')
                i += 2
            else:
                fin_sent.append(sentence[i])
                i += 1
            continue

        else:
            # For all other parts of speech
            # If word is in honorific form, replace with regular form
            # Append to final sentence
            fin_sent.append(SPECIAL[genkei[i]] if genkei[i] in SPECIAL else sentence[i])
            i += 1

    # print(fin_sent)
    # print('\n')

    #Post edit た to だ　and て to で for words like 読んで
    final = []
    sentence, genkei, hinshi, hinshi2, katsuyo, row = parse(''.join(fin_sent))
    j = 0
    while j < len(sentence):
        if j > 0 and (row[j-1] == "五段-マ行" or row[j-1] == "五段-バ行"):
            if sentence[j] == "た":
                final.append("だ")
            elif sentence[j] == "て":
                final.append("で")
            else:
                final.append(sentence[j])
        else:
            final.append(sentence[j])
        j+=1

    return ''.join(final)


if __name__ == "__main__":
    file_name = input("Path to file of honorific sentences to convert:\n")
    in_f = open(file_name, 'r')
    lines = in_f.readlines()
    in_f.close()

    with open('conjugated_verbs.json', 'r') as json_file:
        global CONJ
        CONJ = json.load(json_file)

    data = {"data": []}
    for l in lines:
        data["data"].append({"hon": l[:-1], "reg": convert(l)})
    
    out_f_name = input("Name of output file:\n")
    with open(out_f_name, "w") as out_f:
        json.dump(data, out_f, ensure_ascii=False)

