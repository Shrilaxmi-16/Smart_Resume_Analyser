import nltk

def download_nltk_resources():
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

if __name__ == "__main__":
    download_nltk_resources()
