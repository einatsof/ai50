import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }

    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files_dict = {}
    files = os.listdir(directory)
    for file in files:
        with open(os.path.join(directory, file), encoding="utf8") as f:
            files_dict[file] = f.read()
    return files_dict


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    words = nltk.word_tokenize(document.lower())
    tokens = []
    for word in words:
        # Filter out punctuation and stopwords
        if word in string.punctuation or word in nltk.corpus.stopwords.words("english"):
            continue
        tokens.append(word)
    return tokens


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    idf_dict = {}
    for document, words_list in documents.items():
        # Create a list of all words with no duplicates
        words_list_no_duplicates = list(dict.fromkeys(words_list))
        # Update count for each word
        for word in words_list_no_duplicates:
            if word in idf_dict:
                idf_dict[word] += 1
            else:
                idf_dict[word] = 1
    documents_num = len(documents)
    # Calculate idf values
    for word in idf_dict:
        idf_dict[word] = math.log(documents_num / idf_dict[word])
    return idf_dict


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    # A dictionary of tf-idf sum for each file
    files_tfidf = {file: 0 for file in files}
    for file, words_list in files.items():
        for word in query:
            if word in words_list:
                files_tfidf[file] += words_list.count(word) * idfs[word]
    # Sort dictionary by value and convert to a list of keys
    sorted_files = [k for k, v in sorted(files_tfidf.items(), key=lambda x: x[1], reverse=True)]
    return sorted_files[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    # A dictionary of idf sum for each sentence
    sentences_sum = {sentence: 0 for sentence in sentences}
    # A dictionary of query tern density for each sentence
    sentences_qtd = {sentence: 0 for sentence in sentences}
    for sentence, words_list in sentences.items():
        sentence_length = len(sentence)
        for word in query:
            if word in words_list:
                sentences_sum[sentence] += idfs[word]
                sentences_qtd[sentence] += words_list.count(word) / sentence_length
    # Sort idf sum dictionary by value (tie sort by qtd value) and convert to a list of keys
    sorted_sentences = [k for k, v in sorted(sentences_sum.items(), key=lambda x: (x[1], sentences_qtd[x[0]]), reverse=True)]
    return sorted_sentences[:n]


if __name__ == "__main__":
    main()
