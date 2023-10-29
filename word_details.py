import requests
from bs4 import BeautifulSoup
import os
import logging.config
import nltk
from nltk.corpus import wordnet


script_dictionary = os.path.dirname(os.path.abspath(__file__))
config_folder = os.path.normpath(os.path.join(script_dictionary, 'config'))
log_config_path = os.path.normpath(os.path.join(config_folder, 'logs.conf'))
logging.config.fileConfig(log_config_path, disable_existing_loggers=False)

logger = logging.getLogger("WrdDetail")


class WordDetail:
    def __init__(self, word):
        self.word = word

    def call_methods(self):
        logger.info("call_methods START")
        meaning = self.get_definition(self.word)
        meaning = 'WORD MEANING:\n{}'.format(meaning)
        type_of_word = self.thesaurus(self.word)

        type_of_word['synonyms'] = 'SYNONYMS:\n{}'.format(type_of_word['synonyms'])
        type_of_word['antonyms'] = 'ANTONYMS:\n{}'.format(type_of_word['antonyms'])

        sentence = self.sentence_dict(self.word)
        sentence = 'SENTENCES:\n{}'.format(sentence)

        data_dict = {'meaning': meaning, 'type_of_word': type_of_word, 'sentence': sentence}
        # data_dict = {'meaning': 'meaning', 'type_of_word': 'type_of_word', 'sentence': 'sentence'}
        logger.info("call_methods END")
        return data_dict

    def get_definition(self, word):
        logger.info("get_dictionary.com START")
        meanings = list()
        word_meaning = None

        try:
            sm_code = requests.get("https://www.dictionary.com/browse/{}".format(word))
            soup = BeautifulSoup(sm_code.text, 'html.parser')
            top_definitions_section = soup.find(id='top-definitions')
            for i in top_definitions_section.contents:
                j = i.contents[0]
                for t in j.contents:
                    if t.name == 'div':
                        for w in t.contents:
                            if w.name == 'div':
                                print(w.text)
                                meanings.append(w.text)
            if meanings.__len__() > 0:
                word_meaning = "\n".join(meanings)
        except Exception as e:
            pass
            # dictionary = PyDictionary()
            # word_meaning = dictionary.meaning(word)

        logger.info("get_dictionary.com END")
        return word_meaning

    def get_word_with_nltk(self, word):
        antonyms = []
        synonyms = []
        nltk.download('wordnet')
        # Get the synsets (sets of synonyms) for the given word
        synsets = wordnet.synsets(word)
        for synset in synsets:
            for lemma in synset.lemmas():
                # Iterate through the antonyms of each lemma
                antonyms.extend(lemma.antonyms())
                synonyms.append(lemma.name())

        # Extract the antonym words from the antonyms list
        antonym_words = [antonym.name() for antonym in antonyms]
        return antonym_words, synonyms

    def thesaurus(self, word):
        # print(self.word_with_nltk(word))
        logger.info("thesaurus START")
        actions = {'synonyms': None, 'antonyms': None}
        try:
            sm_code = requests.get("https://www.thesaurus.com/browse/{}".format(word))
            soup = BeautifulSoup(sm_code.text, 'html.parser')
            for key, value in actions.items():
                main_list = list()
                try:
                    tag = soup.find(id=value)
                    tag = tag.find('div', {'data-testid': 'word-grid-container'})
                    for string in tag.strings:
                        if string.__len__() > 1:
                            main_list.append(string)
                    words = set(main_list)
                    actions[key] = ' | '.join(words)
                except AttributeError as e:
                    words = None
                    logger.exception("Error got for {} \n{}".format(key, str(e)))
                    if key == 'antonyms' and actions['antonyms'] is None:
                        actions['antonyms'] = ", ".join(list(set(self.get_word_with_nltk(word)[0])))

                    if key == 'synonyms' and actions['synonyms'] is None:
                        actions['synonyms'] = ", ".join(list(set(self.get_word_with_nltk(word)[1])))

        except Exception as e:
            antonyms, synonyms = self.get_word_with_nltk(word)
            actions['antonyms'] = ", ".join(list(set(antonyms)))
            actions['synonyms'] = ", ".join(list(set(synonyms)))

        logger.info("thesaurus END")
        return actions

    def sentence_dict(self, word):
        logger.info("sentence_dict START")
        main_list = list()
        sm_code = requests.get("https://sentencedict.com/{}.html".format(word))
        soup = BeautifulSoup(sm_code.text, 'html.parser')

        tag = soup.find(id='all')
        for sub_tag in tag.contents:
            if sub_tag.text != '':
                main_list.append(sub_tag.text)
        main_list = '\n'.join(main_list)
        logger.info("sentence_dict END")
        return main_list
