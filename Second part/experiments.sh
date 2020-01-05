
python processing.py
python processing.py -flag_ner=True
python processing.py -flag_norm=False

python processing.py -mode=name -sub_mode=union#actor.name#director.name
python processing.py -mode=name -sub_mode=intersection#actor.name#person.name
python processing.py -mode=name -sub_mode=intersection#director.name#producer.name
python processing.py -mode=nationality -sub_mode=union#actor.nationality#producer.nationality#director.nationality#movie.language

python processing.py -mode=country -sub_mode=union#country.name#movie.release_region#movie.language
python processing.py -mode=country -sub_mode=union#country.name#movie.language

python processing.py -mode=name -sub_mode=union#actor.name#director.name -flag_ner=True
python processing.py -mode=name -sub_mode=intersection#actor.name#person.name -flag_ner=True
python processing.py -mode=name -sub_mode=intersection#director.name#producer.name -flag_ner=True
python processing.py -mode=nationality -sub_mode=union#actor.nationality#producer.nationality#director.nationality#movie.language -flag_ner=True
python processing.py -mode=country -sub_mode=union#country.name#movie.release_region#movie.language -flag_ner=True
python processing.py -mode=country -sub_mode=union#country.name#movie.language -flag_ner=True

python processing.py -mode=name -sub_mode=union#actor.name#director.name -flag_ner=True -flag_norm=False
python processing.py -mode=name -sub_mode=intersection#actor.name#person.name -flag_ner=True -flag_norm=False
python processing.py -mode=name -sub_mode=intersection#director.name#producer.name -flag_ner=True -flag_norm=False
python processing.py -mode=nationality -sub_mode=union#actor.nationality#producer.nationality#director.nationality#movie.language -flag_ner=True -flag_norm=False
python processing.py -mode=country -sub_mode=union#country.name#movie.release_region#movie.language -flag_ner=True -flag_norm=False
python processing.py -mode=country -sub_mode=union#country.name#movie.language -flag_ner=True -flag_norm=False

python processing.py -mode=name -sub_mode=union#actor.name#director.name -flag_norm=False
python processing.py -mode=name -sub_mode=intersection#actor.name#person.name  -flag_norm=False
python processing.py -mode=name -sub_mode=intersection#director.name#producer.name  -flag_norm=False
python processing.py -mode=nationality -sub_mode=union#actor.nationality#producer.nationality#director.nationality#movie.language  -flag_norm=False
python processing.py -mode=country -sub_mode=union#country.name#movie.release_region#movie.language  -flag_norm=False
python processing.py -mode=country -sub_mode=union#country.name#movie.language  -flag_norm=False

python processing.py -mode=name -sub_mode=union#actor.name#person.name
python processing.py -mode=name -sub_mode=union#actor.name#person.name -flag_ner=True
python processing.py -mode=name -sub_mode=union#actor.name#person.name -flag_ner=True -flag_norm=False
python processing.py -mode=name -sub_mode=union#actor.name#person.name -flag_norm=False

python processing.py -mode=name -sub_mode=union#director.name#producer.name
python processing.py -mode=name -sub_mode=union#director.name#producer.name -flag_ner=True
python processing.py -mode=name -sub_mode=union#director.name#producer.name -flag_ner=True -flag_norm=False

python processing.py -mode=name -sub_mode=union#director.name#producer.name -flag_norm=False

python processing.py -mode=name -sub_mode=union#director.name#person.name
python processing.py -mode=name -sub_mode=union#director.name#person.name -flag_ner=True
python processing.py -mode=name -sub_mode=union#director.name#person.name -flag_ner=True -flag_norm=False

python processing.py -mode=name -sub_mode=union#director.name#person.name -flag_norm=False
