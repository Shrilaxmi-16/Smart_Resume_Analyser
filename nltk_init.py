import nltk
import spacy

def download_nltk_resources():
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

def download_spacy_model():
    try:
        spacy.load('en_core_web_sm')
    except OSError:
        spacy.cli.download('en_core_web_sm')

if __name__ == "__main__":
    download_nltk_resources()
    download_spacy_model()
