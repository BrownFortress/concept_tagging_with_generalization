import re
import pprint
import numpy as np
from collections import Counter
from random import randrange, uniform
import pywrapfst as fst
import pynini
import math
import shlex, subprocess
import os
from tqdm import tqdm
from stanford_nlp.nlp import StanfordNLP
from multiprocessing import Process, Manager
from dataset.data_manager import DataManager
import sys
from argparse import ArgumentParser
class Processing():
    def __init__(self):
        self.dataset_folder = "dataset/"
        dm = DataManager()
        self.data_manager = dm

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
    def load_data_keeping_sentences(self, filename):
        s = re.compile(r'\t+|\n+')
        with open(self.dataset_folder + filename, "r") as f:
            content = f.readlines()
        if "\t" in content[0]:
            labels = []
            text = []
            sentence_labels = []
            sentence_text = []
            for line in content:
                if len(s.split(line))>1 and s.split(line)[1] != "" and s.split(line)[0] != "":
                    sentence_labels.append(s.split(line)[1])
                    sentence_text.append(s.split(line)[0])
                else:
                    labels.append(sentence_labels)
                    text.append(sentence_text)
                    sentence_labels = []
                    sentence_text = []
            if len(sentence_text)>0:
                labels.append(sentence_labels)
                text.append(sentence_text)
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

    def evaluation_print(self, predicted, test_file):
        labels, tokens = self.load_data_keeping_sentences(test_file)
        output = ""
        for id, sentece in enumerate(tokens):
            if len(predicted) > id:
                for sub_id, w in enumerate(sentece):
                    if len(predicted[id]) > sub_id:
                        output += w + " " + labels[id][sub_id] + " " + predicted[id][sub_id] + "\n"
                    else:
                        output += w + " " + labels[id][sub_id] + " O\n"
                output += "-X- -X- -X-\n"
        return output

    def build_lexicon(self, feature_file, lower_bound=None, upper_bound=None, stop_words=None):
        labels, tokens = self.load_data(feature_file)
        unique_labels = Counter(labels)
        unique_tokens = Counter(tokens)
        removed_words = []
        if lower_bound != None or upper_bound!= None:
            print("Cut off")
            for k, v in unique_tokens.items():
                if lower_bound != None:
                    if v <= lower_bound:
                        removed_words.append(k)
                        del unique_tokens[k]
                if upper_bound != None:
                    if v >= upper_bound:
                        removed_words.append(k)
                        del unique_tokens[k]
            print("Words removed : " + str(len(removed_words)) + " " + ",".join(removed_words))
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
    def get_bayeisan_values(self, x, y):
        pair = []
        all_labels = []
        for id, lab in enumerate(y):
            for sub_id, l in enumerate(lab):
                pair.append(x[id][sub_id] + " " + l)
                all_labels.append(x[id][sub_id])
        c_label = Counter(all_labels)
        c_pair = Counter(pair)
        for k, v in c_pair.items():
            token, lab = k.split(" ")
            c_pair[k] = v / float(c_label[token])
        return c_pair
    def get_regex(self, tokens):
        temp_to_reg = []
        for name in tokens:
            sub_list = []
            for x in name.split(" "):
                if "." not in x:
                    sub_list.append(x)
            temp_to_reg.append("\\b" + " ".join(sub_list) + "\\b")

        return "(" + "|".join(temp_to_reg) + ")"


    def intermedium_set(self, data_file, feature_file, to_generalize,  flag_norm=True, flag_ner = False):
        corpus = []
        with open(self.dataset_folder + "/" + data_file, "r") as file:
            lines = file.readlines()
            for line in lines:
                corpus.append(line.strip())

        labels, tokens = self.load_data_keeping_sentences(feature_file)
        ner_labels, tok = self.load_data_keeping_sentences(feature_file.split(".")[0].split("_")[0] +  "_ner.txt")
        new_labels = []
        new_tokens = []
        if len(to_generalize.values()) > 0:
            for k, v in to_generalize.items():
                reg = re.compile(self.get_regex(v))
                for idl, line in enumerate(corpus):
                    matched = filter(None, reg.findall(line.strip()))
                    sentence_list = []
                    id = 0
                    for w in reg.sub(k, line.strip()).split(" "):
                        if w == k:
                            if labels[idl][id] != "O":
                                for t in matched[id].split(" "):
                                    sentence_list.append(k)
                                id += 1
                            else:
                                for t in matched[id].split(" "):
                                    sentence_list.append(t)
                                id += 1
                        else:
                            sentence_list.append(w)
                    corpus[idl] = " ".join(sentence_list)
                tokens = []
                for utterance in corpus:
                    tokens.append(utterance.split(" "))

        for id, sentence_labels in enumerate(labels):
            sub_new_label = []
            sub_new_tokens = []
            for sub_id, label in enumerate(sentence_labels):
                l = ""
                if label != "O":
                    l = label.split("-")[-1]
                else:
                    l = label
                if ner_labels[id][sub_id] != "O" and flag_ner:
                #if ner_labels[id][sub_id] == "NATIONALITY" and flag_ner:
                    sub_new_tokens.append(ner_labels[id][sub_id])
                    sub_new_label.append(ner_labels[id][sub_id])
                else:
                    sub_new_tokens.append(tokens[id][sub_id])
                    sub_new_label.append(tokens[id][sub_id])
            new_labels.append(sub_new_label)
            new_tokens.append(sub_new_tokens)

        with open(self.dataset_folder + "first_part_" + feature_file.split(".")[0] + ".txt", "w") as file:
            for id, sentence_label in enumerate(new_labels):
                for sub_id, label in enumerate(sentence_label):
                    file.write(tokens[id][sub_id] + "\t" + label + "\n")
                file.write("\n")
        new_labels2 = []
        new_tokens_cleaned = []
        # Compactation
        for id, sentence_t in enumerate(new_tokens):
            sub_new_tokens = []
            sub_new_labels = []
            for sub_id, t in enumerate(sentence_t):
                if len(sub_new_tokens) == 0:
                     sub_new_tokens.append(t)
                     sub_new_labels.append(labels[id][sub_id])
                else:
                    sub_new_tokens.append(t)
                    sub_new_labels.append(labels[id][sub_id])
            new_labels2.append(sub_new_labels)
            new_tokens_cleaned.append(sub_new_tokens)

        c_concept_tag_pair = self.get_bayeisan_values(new_tokens_cleaned, new_labels2)
        with open(self.dataset_folder + "second_part_" + feature_file.split(".")[0] + ".txt", "w") as file:
            for id, sentence_tokens in enumerate(new_tokens_cleaned):
                for ids, token in enumerate(sentence_tokens):
                    key = token + " " +  new_labels2[id][ids]
                    if flag_norm and new_labels2[id][ids] == "O" and c_concept_tag_pair[key]>0.07:
                        file.write(token + "\t" + token + "\n")
                    else:
                        file.write(token + "\t" + new_labels2[id][ids] + "\n")
                file.write("\n")

    def file_for_ngram_model(self, feature_file, lexicon_file_name, folder, ):
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

        with open("bin/" + folder + "_data_for_ngram.txt", "w") as file:
            for f in features:
                file.write(f+"\n")
        if folder == "second":
            reverse_features = []
            for f in features:
                if "." in f.split(" ")[0]:
                    reverse_features.append(" ".join(list(reversed(f.split(" ")))))
                else:
                    reverse_features.append(f)
            with open("bin/third_data_for_ngram.txt", "w") as file:
                for f in reverse_features:
                    file.write(f+"\n")
            bashCommand = "./exec/compile.sh  bin/" + lexicon_file_name.split(".")[0] + " bin/third_data_for_ngram smooths third"
            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
        if os.path.exists("bin/" + folder + "_data_for_ngram.txt"):
            print("File created, launch compose.sh")

        bashCommand = "./exec/compile.sh  bin/" + lexicon_file_name.split(".")[0] + " bin/" + folder + "_data_for_ngram smooths " + folder
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
    def save_ner(self, input_file, output_file):
        corpus = []
        with open(self.dataset_folder + input_file) as file:
            for l in file.readlines():
                corpus.append(l.strip())

        nlp = StanfordNLP()
        with open(self.dataset_folder + output_file, "w") as file:
            for c in corpus:
                for w, l in nlp.ner(c):
                    file.write(w + "\t" + l + "\n")
                file.write("\n")

    def __filter(self, word, lexicon):
        if lexicon.member(word):
            return word
        else:
            return "<unk>"
    def eval(self, filename):
        s = re.compile(r'\t+|\n+|\s+')
        with open(filename, "r") as f:
            content = f.readlines()

        true_labels = [s.split(x)[1].strip() for x in content if x.strip() != "-X- -X- -X-"]
        pred_labels =  [s.split(x)[2].strip() for x in content if x.strip() != "-X- -X- -X-"]
        errors = 0
        for id, x in enumerate(true_labels):
            if x != pred_labels[id]:
                errors += 1
        print("Errors :" + str(errors / float(len(pred_labels))))

    def sanity_check(self, old_string, new_string, class_cluster): # Adjust miss predicted words not generalization
        for id, w in enumerate(new_string):
            if w not in class_cluster.values():
                if w != old_string[id] and w.islower():
                    new_string[id] = old_string[id]
        return new_string

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
        with open("bin/automa.txt", "w") as file:
            file.write(corpus)
        automaton = compiler.compile()
        return automaton

    def compute_tagging(self, corpus, first_lex_in, first_lex_out, second_lex_in,
    second_lex_out, automaton1, automaton2, class_cluster, trials1, trials2, result, key):
        results = []
        smooth1 = fst.Fst.read(trials1)
        smooth2 = fst.Fst.read(trials2)
        for idc, l in enumerate(corpus):
            acceptor = self.far_compile_string(l, first_lex_in, "<unk>")
            cv = fst.compose(acceptor, automaton1)
            res = fst.compose(cv, smooth1)
            res = res.rmepsilon()
            res = fst.shortestpath(res)
            res = res.topsort()
            res = self.fst_print(res, first_lex_out)
            compact_res = []
            res = self.sanity_check(l.split(" "), res, class_cluster)
            first_o = " ".join(res)


            acceptor = self.far_compile_string(first_o, second_lex_in, "<unk>")
            cv = fst.compose(acceptor, automaton2)
            res = fst.compose(cv, smooth2)
            res = res.rmepsilon()
            res = fst.shortestpath(res)
            res = res.topsort()
            output = [x if "." in x else "O" for x in self.fst_print(res, second_lex_out)]

            results.append(output)
        result[key] = results
    def build_generalization_set(self, sub_mode, entities):
        tmp = sub_mode.split("#")
        operand = tmp[0]
        operators = tmp[1:]
        to_gen = None
        if operand == "intersection":
            for id, s in enumerate(operators):
                if to_gen == None:
                    to_gen = set(entities[s]).intersection(set(entities[operators[id + 1]]))
                else:
                    if id != 1:
                        to_gen = to_gen.intersection(set(entities[s]))
        else:
            if operand == "union":
                for id, s in enumerate(operators):
                    if to_gen == None:
                        to_gen = set(entities[s]).union(set(entities[operators[id + 1]]))
                    else:
                        if id != 1:
                            to_gen = to_gen.union(set(entities[s]))
            else:
                print("Only union and intersection are allowed!")
                sys.os(2)
        return to_gen



if __name__ == "__main__":
    processing = Processing()
    class_cluster = {}
    mode = "base"
    sub_mode = ""
    parser = ArgumentParser()
    parser.add_argument("-mode", default = "base")
    parser.add_argument("-sub_mode", default = "")
    parser.add_argument("-flag_ner", default= "False")
    parser.add_argument("-flag_norm", default="True")
    args = vars(parser.parse_args(sys.argv[1:]))
    mode = args["mode"]
    sub_mode = args["sub_mode"]
    flag_ner = args["flag_ner"] in ("True")
    flag_norm = args["flag_norm"] in ("True")
    print flag_ner
    dm = DataManager()
    to_generalize= {}

    if mode == "nationality":
        print("Nationality generalization")
        class_cluster["actor.nationality"] = "person.nationality"
        class_cluster["producer.nationality"] = "person.nationality"
        class_cluster["director.nationality"] = "person.nationality"
        class_cluster["movie.language"] = "person.nationality"
        entities = dm.extract_entities(class_cluster.keys(), "train_features.txt")
        if sub_mode != "":
            to_generalize["person.nationality"] = processing.build_generalization_set(sub_mode, entities)
        else:
            to_gen1 = set(entities["actor.nationality"]).union(set(entities["producer.nationality"])).union(set(entities["director.nationality"])).union(set(entities["movie.language"]))
            print(len(to_gen1))
            to_gen2 = set(entities["movie.location"]).union(set(entities["movie.release_region"]))
            to_generalize["person.nationality"] = to_gen1
            #to_generalize["person.name"] = set(entities["actor.name"])
            #to_generalize["country.name"] = to_gen2
        print("Elements to generalize : " + str(len(to_generalize["person.nationality"])))

    if mode == "country":
        print("Country generalization")
        class_cluster["movie.release_region"] = "country.name"
        class_cluster["country.name"] = "country.name"
        class_cluster["movie.location"] = "country.name"
        class_cluster["movie.language"] = "country.name"
        entities = dm.extract_entities(class_cluster.keys(), "train_features.txt")
        if sub_mode != "":
            to_generalize["country.name"] = processing.build_generalization_set(sub_mode, entities)
        else:
            to_gen2 = set(entities["movie.location"]).union(set(entities["movie.release_region"]))
            # Put here custom experiments
        print("Elements to generalize : " + str(len(to_generalize["country.name"])))

    if mode == "name":
        print("Name generalization")
        class_cluster["actor.name"] = "actor.name"
        class_cluster["producer.name"] = "producer.name"
        class_cluster["director.name"] = "director.name"
        class_cluster["person.name"] = "person.name"
        entities = dm.extract_entities(class_cluster.keys(), "train_features.txt")

        if sub_mode != "":
            to_generalize["person.name"] = processing.build_generalization_set(sub_mode, entities)
        else:
            # Put here custom experiments
            to_gen1 = set(entities["actor.name"]).intersection(set(entities["director.name"])) # No effect
            union = set(entities["actor.name"]).union(set(entities["director.name"]))
            to_gen2 = set(entities["person.name"]).intersection(to_gen1) # No effect
            to_gen3 = set(entities["person.name"]).intersection(union) # No effect
            all_names = set(entities["actor.name"]).union(set(entities["director.name"]).union(entities["person.name"]))
            to_generalize = all_names.difference(set(entities["producer.name"])).difference(set(entities["person.name"]))
            #to_generalize["a.name"] = union.difference(to_gen1) 82.45
            #to_generalize = to_gen3 # 82.59 problem with person.name
            #to_generalize = all_names.difference(to_gen2) 82.54
            #to_generalize = all_names.difference(set(entities["producer.name"])).difference(set(entities["person.name"])) 82.50
            to_generalize = all_names.intersection(set(entities["producer.name"])).intersection(set(entities["person.name"]))
            to_generalize = {}
            z =  set(entities["actor.name"]).intersection(set(entities["person.name"]))
            x = set(entities["director.name"]).intersection(set(entities["person.name"]))
            person = Counter(entities["person.name"])
            pprint.pprint(Counter(entities["actor.name"]))
            #k = filter(lambda x: person[x]>6, entities["person.name"])
            to_generalize["a.person"] = set(entities["person.name"]).union(set(entities["actor.name"]))
            #to_generalize["d.person"] = set(entities["director.name"]).intersection(set(entities["producer.name"]))
            #to_generalize["p.person"] = set(entities["actor.name"]).union(set(entities["director.name"])).difference(z.union(x))
            #print(to_generalize["p.person"])
            #to_generalize["a.person"] = set(entities["producer.name"]).intersection(entities["person.name"]).union(set(entities["director.name"]).intersection(set(entities["producer.name"]))).union(set(entities["actor.name"]).intersection(set(entities["person.name"])))
            #to_generalize["p.person"] = set(entities["actor.name"]).union(entities["director.name"]).difference(entities["person.name"]).difference(entities["producer.name"])
            to_generalize["person.name"] = to_gen
        print("Elements to generalize : " + str(len(to_generalize["person.name"])))



    # Creation of two traning set one for WFST words to generalization and one for WFST from generalization to concpets
    if flag_ner:
        if not os.path.exists(processing.dataset_folder + "training_ner.txt"):
            processing.save_ner("train_set.txt", "training_ner.txt")

    processing.intermedium_set("train_set.txt", "train_features.txt", to_generalize,  flag_norm=flag_norm, flag_ner=flag_ner)


    first_lex_in, first_lex_out = processing.build_lexicon("first_part_train_features.txt")


    first_lex_in.write_text("bin/lex_in_f1.txt")
    first_lex_out.write_text("bin/lex_out_f1.txt")

    processing.file_for_ngram_model("first_part_train_features.txt", "lex_out_f1.txt", "first")

    automaton1 = processing.build_automa("first_part_train_features.txt", first_lex_in, first_lex_out)

    second_lex_in, second_lex_out = processing.build_lexicon("second_part_train_features.txt")

    second_lex_in.write_text("bin/lex_in_f2.txt")
    second_lex_out.write_text("bin/lex_out_f2.txt")

    processing.file_for_ngram_model("second_part_train_features.txt", "lex_out_f2.txt", "second")

    automaton2 = processing.build_automa("second_part_train_features.txt", second_lex_in, second_lex_out)

    trials1 = []
    for folder in os.listdir("smooths/first/"):
            for filename in os.listdir("smooths/first/" + folder):
                trials1.append("smooths/first/" + folder + "/" + filename)
    trials2 = []
    for folder in os.listdir("smooths/second/"):
            for filename in os.listdir("smooths/second/" + folder):
                trials2.append("smooths/second/" + folder + "/" + filename)
    trials3 = []
    for folder in os.listdir("smooths/third/"):
            for filename in os.listdir("smooths/third/" + folder):
                trials3.append("smooths/third/" + folder + "/" + filename)
    corpus = []

    with open(processing.dataset_folder + "test_set.txt") as file:
        for l in file.readlines():
            corpus.append(l.strip())



    manager = Manager()
    returns = manager.dict()
    for id in tqdm(range(0, len(trials1), 5)):

        results = []
        ids = id
        p1 = Process(target=processing.compute_tagging, args=(corpus, first_lex_in, first_lex_out, second_lex_in,
    second_lex_out, automaton1, automaton2, class_cluster, trials1[ids], trials2[ids], returns, trials1[ids]))
        p1.start()
        ids += 1
        p2 = Process(target=processing.compute_tagging, args=(corpus, first_lex_in, first_lex_out, second_lex_in,
    second_lex_out, automaton1, automaton2, class_cluster, trials1[ids], trials2[ids], returns, trials1[ids]))
        p2.start()
        ids += 1
        p3 = Process(target=processing.compute_tagging, args=(corpus, first_lex_in, first_lex_out, second_lex_in,
    second_lex_out, automaton1, automaton2, class_cluster, trials1[ids], trials2[ids],  returns, trials1[ids]))
        p3.start()
        ids += 1
        p4 = Process(target=processing.compute_tagging, args=(corpus, first_lex_in, first_lex_out, second_lex_in,
    second_lex_out, automaton1, automaton2, class_cluster, trials1[ids], trials2[ids],  returns, trials1[ids]))
        p4.start()
        ids += 1
        p5 = Process(target=processing.compute_tagging, args=(corpus, first_lex_in, first_lex_out, second_lex_in,
    second_lex_out, automaton1, automaton2, class_cluster, trials1[ids], trials2[ids], returns, trials1[ids]))
        p5.start()

        p1.join()
        p2.join()
        p3.join()
        p4.join()
        p5.join()

    for k, v in returns.items():
        r = processing.evaluation_print(v, "test_features.txt")
        folder1, folder2, folder3, filename = k.split("/")
        r_folder = mode
        if sub_mode != "":
            r_folder = mode + "_" + sub_mode.replace("#", "_")
        if flag_ner:
            r_folder = mode + "_with_ner_" + sub_mode.replace("#", "_")
        if not flag_norm:
            r_folder = mode + "_not_norm_" + sub_mode.replace("#", "_")
        if flag_ner and not flag_norm:
            r_folder = mode + "_not_norm_with_ner_" + sub_mode.replace("#", "_")

        if not os.path.exists("results/"+ r_folder + "/" + folder3 + "/"):
            os.makedirs("results/"+ r_folder + "/" + folder3 + "/")
        filename = filename.split(".")[0]


        with open("results/"+ r_folder + "/" + folder3 + "/" + filename + "_result.txt", "w") as file:
            file.write(r)
