import os
import pandas as pd
import re
class DataManager():
    def __init__(self):
        self.regex_movies = ""
        self.regex_celebrities = ""
        self.dataset_folder = "dataset/"
        self.celebrities = []
        self.movies = []
        self.read_movies_and_celebreties()

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
    def extract_entities(self, class_cluster_keys, data):
        labels, tokens = self.load_data_keeping_sentences(data)
        entities = {}
        for c in class_cluster_keys:
            entities[c] = []
        for id, lab in enumerate(labels):
            entity = []
            prev_label = ""
            for sub_id, sub_label in enumerate(lab):
                l = sub_label
                token = tokens[id][sub_id]
                if l != "O":
                    l = l.split("-")[-1]
                if l in class_cluster_keys:
                    if l != prev_label:
                        if len(entity) > 0:
                            entities[prev_label].append(" ".join(entity))
                            entity = []
                            entity.append(token)
                        else:
                            entity.append(token)
                    else:
                        entity.append(token)
                else:
                    if len(entity) > 0:
                        entities[prev_label].append(" ".join(entity))
                        entity = []
                prev_label = l
        for k, v in entities.items():
            entities[k] = list(filter(lambda x: len(x)>1,  v))
        return entities

    def read_movies_and_celebreties(self):
        all_movies = []
        all_celebrities = []
        folder = "dataset/"
        for path in os.listdir(folder + "movies/"):
            f = pd.read_csv(folder + "movies/" + path, encoding='latin-1')
            titles = f["Title"].tolist()
            directors = f["Directors"].tolist()
        for name in titles:
            all_movies.append(name.lower())
        for d in directors:
            if "," in d:
                for name in d.split(","):
                    all_celebrities.append(name.lower().strip())
            else:
                all_celebrities.append(d.lower())

        for path in os.listdir(folder + "celebrities/"):
            f = pd.read_csv(folder + "celebrities/" + path, encoding='latin-1')
            names = f["Name"].tolist()
            movies = f["Known For"].tolist()
            for name in movies:
                all_movies.append(name.lower())
            for d in names:
                all_celebrities.append(d.lower())

        unique_celebrities = set(all_celebrities)
        unique_movies = set(all_movies)
        unique_celebrities_cleaned = []
        unique_movies_cleaned = []
        celebrities = []
        self.celebrities = []
        self.movies = []
        for name in unique_celebrities:
            sub_list = []
            for x in name.split(" "):
                if "." not in x:
                    sub_list.append(x)
            self.celebrities.append(" ".join(sub_list))
            unique_celebrities_cleaned.append("\\b" + " ".join(sub_list) + "\\b")

        for name in unique_movies:
            sub_list = []
            for x in name.split(" "):
                if "." not in x:
                    sub_list.append(x)
            self.movies.append(" ".join(sub_list))
            unique_movies_cleaned.append("\\b" + " ".join(sub_list) + "\\b")

        self.regex_celebrities = "(" + "|".join(unique_celebrities_cleaned) + ")"
        self.regex_movies = "(" + "|".join(unique_movies_cleaned) + ")"
