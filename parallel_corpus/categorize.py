# Program to categorize sentences into honorific and non-honorific.
import MeCab

tagger = MeCab.Tagger('-Osu')

file_name = input("Path to file of sentences to categorize:\n")
in_f = open(file_name, 'r')
lines = in_f.readlines()
in_f.close()

# Words to distinguish honorific sentences (丁寧語)　＝＞　[です、ます、くださる]
hon_words = set(["デス", "マス", "クダサル"])

file_name = input("Path to output honorific sentences:\n")
reg_name = input("Path to output regular/non-honorific sentences:\n")

with open(file_name, "w") as out_hon, open(reg_name, "w") as out_reg:
    for line in lines:
        res = set(tagger.parse(line).split())
        if hon_words.intersection(res): 
            out_hon.write(line)
        else:
            out_reg.write(line)

