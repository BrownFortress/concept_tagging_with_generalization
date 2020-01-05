import re
import pprint
import numpy as np
from collections import Counter
from random import randrange, uniform
import pywrapfst as fst
import pynini
import math
import shlex, subprocess
import os, sys
from tqdm import tqdm

class Processing():
    def __init__(self):
        self.dataset_folder = "dataset/"

    def load_data(self, filename):
        s = re.compile(r'\t+|\n+')
        with open(self.dataset_folder + filename, "r") as f:
            content = f.readlines()
        if "\t" in content[0]:
            labels = [s.split(x)[1] for x in content if len(s.split(x)) > 1 and s.split(x)[1]!=""]
            text =  [s.split(x)[0] for x in content if len(s.split(x)) > 1 and s.split(x)[0]!=""]
            return labels, text
        else:
            text =  [x.strip("\n") for x in content]
            return text
    def far_compile_string(self, string, lex_in, unknown_symbol):
        new_string = ""
        for w in string.split(" "):
            if not lex_in.member(w):
                new_string += unknown_symbol + " "
            else:
                new_string += w + " "
        new_string = new_string.strip()
        a = pynini.acceptor(new_string, token_type=lex_in)

        return a
    def fst_print(self, automa, lex_out):
        result = []
        for state in automa.states():
            for arc in automa.arcs(state):
                result.append(lex_out.find(arc.olabel))
        return result

    def evaluation_print(self, result, test_file):
        labels, tokens = self.load_data(test_file)
        id = 0
        output = ""

        for sentece in result:
            for w in sentece:
                output += tokens[id] + " " + labels[id] + " " + w + "\n"
                id += 1
            output += "-X- -X- -X-\n"
        return output

    def build_lexicon(self, feature_file, lower_bound=None, upper_bound=None, stop_words=None):
        labels, tokens = self.load_data(feature_file)
        unique_labels = Counter(labels)
        unique_tokens = Counter(tokens)
        removed_words = []
        print("Number of unique tokens : " +  str(len(unique_tokens)))
        if lower_bound != None or upper_bound!= None:
            print("Cut off")
            print("Upper bound: " + str(upper_bound))
            print("Lower bound: " + str(lower_bound))
            for k, v in unique_tokens.items():
                if lower_bound != None:
                    if v <= lower_bound:
                        removed_words.append(k)
                        del unique_tokens[k]
                if upper_bound != None:
                    if v >= upper_bound:
                        removed_words.append(k)
                        del unique_tokens[k]
            print("Words removed : " + str(len(removed_words)))
        print("Number of unique tokens : " +  str(len(unique_tokens)))

        lex_in = fst.SymbolTable()
        lex_in.add_symbol("<eps>", 0)
        id = 1
        for t in unique_tokens.keys():
            lex_in.add_symbol(t, id)
            id += 1
        lex_in.add_symbol("<unk>", id)

        lex_out = fst.SymbolTable()
        lex_out.add_symbol("<eps>", 0)
        id = 1
        for t in unique_labels.keys():
            lex_out.add_symbol(t, id)
            id += 1
        lex_out.add_symbol("<unk>", id)
        return lex_in, lex_out

    def file_for_ngram_model(self, feature_file, lexicon_file_name):
        corpus = []
        features = []
        s = re.compile(r'\t+|\n+')
        with open(self.dataset_folder + feature_file) as file:
            sentence = []
            for l in file.readlines():
                if l != "\n":
                    token, label = s.split(l.strip())
                    corpus.append(l.strip().split(" "))
                    sentence.append(label.strip())
                else:
                    features.append(" ".join(sentence))
                    sentence = []
            if len(sentence) > 0:     # Catch the last line
                features.append(" ".join(sentence))

        with open("bin/data_for_ngram.txt", "w") as file:
            for f in features:
                file.write(f+"\n")
        if os.path.exists("bin/data_for_ngram.txt"):
            print("File created, launch compose.sh")

        bashCommand = "./exec/compile.sh  bin/" + lexicon_file_name.split(".")[0] + " bin/data_for_ngram smooths"
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

    def __filter(self, word, lexicon):
        if lexicon.member(word):
            return word
        else:
            return "<unk>"
    def build_automa(self, features_file, lex_in, lex_out):
        labels, tokens = self.load_data(features_file)
        #corpus = load_data(text_file)
        token_label_pair = [self.__filter(token, lex_in) + " " + labels[id] for id, token in enumerate(tokens)]
        labels_counter = Counter(labels)
        token_label_pair_counter = Counter(token_label_pair)

        mean = np.asarray(list(token_label_pair_counter.values())).mean()
        sum = np.asarray(list(token_label_pair_counter.values())).sum()
        std = np.asarray(list(token_label_pair_counter.values())).std()
        # Compute probabilities
        token_label_pair_probabilities = {}
        for pair, count in token_label_pair_counter.items():
            token, label = pair.split(" ")
            token_label_pair_probabilities[pair] = -math.log(float(count) / float(labels_counter[label]))

        for label in labels:
            key = "<unk> " + label
            if key not in token_label_pair_probabilities.keys():
                token_label_pair_probabilities["<unk> " + label] = -math.log(1/  float(len(labels_counter)))
                #token_label_pair_probabilities["<unk> "+label] = -math.log(uniform(mean, std) / float(labels_counter[label]))


        compiler = fst.Compiler(isymbols=lex_in, osymbols=lex_out)
        corpus = ""
        for pair, prob in token_label_pair_probabilities.items():
            token, label = pair.split(" ")
            corpus += "0 0 {0} {1} {2}\n".format(token, label, str(prob))

        print >> compiler, corpus
        print >> compiler, "0\0"

        automaton = compiler.compile()
        return automaton

if __name__ == "__main__":
    lower_bound = None
    upper_bound = None
    if len(sys.argv) > 1:
        if sys.argv[1] != "None":
            lower_bound = int(sys.argv[1])
        if len(sys.argv)> 2:
            if sys.argv[2] != "None":
                upper_bound = int(sys.argv[2])

    p = Processing()
    lex_in, lex_out = p.build_lexicon("train_features.txt", upper_bound=upper_bound, lower_bound=lower_bound)

    lex_in.write_text("bin/lex_in.txt")
    lex_out.write_text("bin/lex_out.txt")

    p.file_for_ngram_model("train_features.txt", "lex_out.txt")

    automaton = p.build_automa("train_features.txt", lex_in, lex_out)

    trials = []
    for folder in os.listdir("smooths"):
        for filename in os.listdir("smooths/" + folder):
            trials.append("smooths/" + folder + "/" + filename)
    corpus = []

    with open(p.dataset_folder + "test_set.txt") as file:
        for l in file.readlines():
            corpus.append(l.strip())

    for t in tqdm(trials):
        results = []
        for l in corpus:
            acceptor = p.far_compile_string(l, lex_in, "<unk>")
            cv = fst.compose(acceptor, automaton)
            smooth = fst.Fst.read(t)
            res = fst.compose(cv, smooth)
            res = res.rmepsilon()
            res = fst.shortestpath(res)
            res = res.topsort()
            results.append(p.fst_print(res, lex_out))
        r = p.evaluation_print(results, "test_features.txt")
        folder1, folder2, filename = t.split("/")
        filename = filename.split(".")[0]
        if not os.path.exists("results/cut_off_lb_" + str(lower_bound) + "_ub_" + str(upper_bound) + "/" + folder2):
            os.makedirs("results/cut_off_lb_" + str(lower_bound) + "_ub_" + str(upper_bound) + "/" + folder2)

        with open("results/cut_off_lb_" +  str(lower_bound) + "_ub_" + str(upper_bound) + "/" + folder2 + "/" + filename + "_result.txt", "w") as file:
            file.write(r)

    #fst.print(result, isymbols=lex_in, osymbols=lex_out)
