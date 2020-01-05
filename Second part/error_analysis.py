import re
import operator
class ErrorAnalysis():
    def __init__(self):
        pass
    def load_data(self, data_path):

        with open(data_path, "r") as f:
            content = f.readlines()
        tokens = []
        true_labels = []
        predictions = []
        for line in content:
            if "-X-" not in line:
                token, true_label, prediction =  line.strip().split(" ")
                tokens.append(token)
                if true_label != "O":
                    true_labels.append(true_label.split("-")[-1])
                else:
                    true_labels.append(true_label)
                if prediction != "O":
                    predictions.append(prediction.split("-")[-1])
                else:
                    predictions.append(prediction)
        return tokens, true_labels, predictions
    def evaluation(self, data_path):
        tokens, true_labels, predictions = self.load_data(data_path)
        evaluations = {}
        tok = {}
        for id, t_l in enumerate(true_labels):
            if t_l not in evaluations.keys():
                evaluations[t_l] = {}
                tok[t_l] = {}
            if predictions[id] not in evaluations[t_l].keys():
                evaluations[t_l][predictions[id]] = 0
                tok[t_l][predictions[id]] = []
            evaluations[t_l][predictions[id]] += 1
            tok[t_l][predictions[id]].append(tokens[id])
        return tok, evaluations
if __name__ == "__main__":
    eval = ErrorAnalysis()
    tok, code = eval.evaluation("results/name_union_director.name_producer.name/4/kneser_ney_result.txt")
    print sorted(code["actor.name"].items(), key=operator.itemgetter(1), reverse = True)
    print tok["actor.name"]["person.name"]
    print sorted(code["director.name"].items(), key=operator.itemgetter(1), reverse = True)
    print sorted(code["producer.name"].items(), key=operator.itemgetter(1), reverse = True)
    print sorted(code["person.name"].items(), key=operator.itemgetter(1), reverse = True)

    #tok, code = eval.evaluation("results/base/4/kneser_ney_result.txt")
    print sorted(code["actor.name"].items(), key=operator.itemgetter(1), reverse = True)
    print sorted(code["director.name"].items(), key=operator.itemgetter(1), reverse = True)
    print sorted(code["producer.name"].items(), key=operator.itemgetter(1), reverse = True)
    print sorted(code["person.name"].items(), key=operator.itemgetter(1), reverse = True)
