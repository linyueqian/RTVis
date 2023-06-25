### This folder is for preprocessing datasets which are helpful when creating the Top n Word’s Frequency Race Diagram

<strong>commonWords.csv</strong>
commonWords.csv is created by dataprocesing.py, which stores the most common words in the abstract part of collected papers in the selected time slot. This dataset is useful for generating the wordCount.csv.

<strong>wordCount.csv</strong>
wordCount.csv is created by dataprocessing.py. Each row in the dataset is the most common word count in the abstract part of all the papers published on that date. This dataset is useful for generating the Word Frequency Race Diagram.

<strong>stop_words.csv</strong>
stop_words.csv is a collection of stop words. Usually, stop words are the words that are too common and may appear in all papers. Thus, we can barely get useful insights from these words and want to exclude them. This dataset is used in dataprocessing.py to filter out the stop words in the abstract part of the papers.

stopwordsCleaner.ipynb is used for customizing the stopwords list. Users can add or remove words from the list and then run the notebook to remove the duplicated words, sort the list, and save the list to stop_words.csv.
