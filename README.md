# Language Understanding System First Project
## Usage
The python version used is 2.7 since the library pywrapfst does not work with the newest version. All libraries related to OpenFst and OpenGrm must be installed. Charts are drawn with Plotly, however this library is not
necessary to run the most important scripts.
## Organization
At the top there are two folders First Part and Second Part containing respectively the first and the
second part of the project. Each one of them contains the following folders:
- **bin**: it contains lexicon in and out of automatons. It contains also the files needed to compute the Language Model, their suffix is "\_data_for\_ngram".
- **chart**: this folder is present only in the Second Part and it contains charts showed in the report.
- **dataset**: it contains the data sets used. It contains the original version of NLSPARQL files. However, the program uses two other version of them: training\_set, test\_set, train_features, test_features. The files with suffix "set" contains the entire utterances without labels while, in the files with "features" suffix are contained words with relative concepts divided by "\\t". In the second part, the dataset folder contains the "training_ner.txt" file, it has the same form of a "features" file but the concepts come from StanfordNLP tagger, it is automatically generated if it does not exist. Furthermore, celebrities and movies are two folders that contain data coming from IMDB that are used to build gazetteers. It contains also a python class data_manager.py. It is used to extract tokens based on the specified concepts, which should be generalized.      
- **exec**: the functionality used for building the language model is not supported by pywrapfst thus, the file contained, compile.sh, is a bash script, in which are written the necessary Ngrm commands for generation the language model needed. Therefore, smooths or ngrams desired should be modified in this file. The compile.sh file is automatically called by the main class Processing, when language models are needed.
- **results**:the folder contains the results produced by the program. The names of sub folder are generated in base of the conducted experiment. Every experiment folder contains four folders numbered form 1 to 4. The number represents the ngram used. Every ngram folder contains the results file one for each smooth. The result file has the following structure: token true label prediction. Furthermore, at the end of each sentence is present the special token "-X -X- -X-". This format is used in accordance with conlleval.pl script specifictions, which is used to compute scores.
- **scores**: this folder has the same structure of result folder, but the files contain the score for that particular result file. The score is the output of conlleval.pl script.
- **smooths**: this folder contains different language models differentiated by ngram. It is overwritten at each execution of the program.
- **stanford_nlp**: this is present only in the second part folder. It contains the StanfordNLP server which is launched by coreNLP.sh. More details on StanfordNLP can be found at https://nlp.stanford.edu/software/CRF-NER.shtml. Furthermore, to run the server this package must be donwloaded http://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-05.zip. Unzip this file in stanford_nlp. If it is necessary update the path in coreNLP.sh.

The prefixes "first" and "second", which are present in some files in the second part folder, are related to the first WFST and second WFST. Whereas, the prefix "third_" is used for building a language model with utterances to which was inverted the order of words. Nevertheless, this did not produce any relevant result thus, there is no reference in the report.  

## First part
The main class is processing.py. To run it, different methodologies are available:
```python
python processing.py #Run without any cut off
#The desired cut off can be chosen
python processing.py <lower_bound> <upper_bound>
'''
However if lower_bound is not specified it must
be set to None
'''
#upper_bound of 100
python processing.py None 1000
#or lower_bound of 1
python processing.py 1
```
## Second part
To speed up various experiments different configurations are available for running the main class processing.py.
```python
python processing.py -mode=<generalization> -sub_mode=<entities to generalize> -flag_ner=<True or False> -flag_norm=<True or False>
```
### Options
- **mode**: there are four different modes: base, nationality, country and name. The base mode is used as default value when mode is not specified. It run the program without generalization.
Nationality, country and name select a different generalization for each area.
- **sub_mode**: It specifies which action of generalization should the program execute. There are two set operations available: union and intersection. To specify the concepts that should be united or intersected it follows the following rule:
```bash
union#actor.name#person.name
or
intersection#country.name#movie.language
```
Thus the operation is written at the beginning and the concepts are listed after, each one is separated with "#" token.<br>
If the field mode is specified and sub_mode is not then the program will run custom generalizations which must be hard coded in the main class.
- **flag_ner**: if it is true then it enables the program to use ner tagging coming from StanfordNLP. Before setting this flag to true, the StanfordNLP server must be launched running the coreNLP.sh in another bash shell. <br>
If this filed is not present the default value is False
- **flag_norm**: this flag enables or disables the improvement of the language model. By default, it is set to True (enabled).

## Other Files
### First and Second part
Additional files are present in order to speed up evaluations and experiments:
- **evaluation.py:** once the script processing.py has finished its execution in order to obtain the scores, evaluation.py must be launched. Every time, it processes the entire content contained in results folder. It creates and launches the file eval.sh that creates the necessary folders in scores folder and saves the output of conlleval.pl.
- **experiments.sh**: in this file are listed all commands used to get the result presented in the report.
- **conlleval.pl**: this script is used to computer the performance metrics: accuracy, recall, precision and F1. More detail on this script can be found [here](https://www.clips.uantwerpen.be/conll2000/chunking/output.html).

### Only in Second part
- **error_analysis.py**: this class is used to compute the error analysis through building the confusion matrix. In order to use it, the analysis must be hard coded in the main, specifying the file, one from results folder, to analyze and the row of the confusion matrix that is wanted to show. Furthermore, also the relative tokens, which caused the misprediction, can be shown in the same way of the confusion matrix.
- **Lab.ipynb**: it is a jupyter notebook file and it contains some scripts that are useful to inspect the dataset and to print some charts.
