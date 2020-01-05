import shlex, subprocess
import os
import sys
import pprint
import operator

commands = ""

for mode in os.listdir("results/"):
    for dir1 in os.listdir("results/" + mode):
        for filename in os.listdir("results/" + mode + "/" + dir1):
            path = "scores/"+ mode + "/" + dir1 + "/" + filename
            if not os.path.exists("scores/"+ mode + "/" + dir1):
                os.makedirs("scores/"+ mode + "/" + dir1)

            commands += "rm " + path + "\n"
            commands += "perl ./conlleval.pl < " + "results/" + mode + "/" + dir1 + "/" + filename + " >> " + path + "\n"
with open("eval.sh", "w") as file:
    file.write('#!/bin/sh \n')
    file.write(commands)

bashCommand = "./eval.sh"
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
