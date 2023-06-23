### This folder is for prepocessing datasets which are useful when creating the Top n Word’s Frequency Race Diagram

\textbf{commonWords.csv}
commonWords.csv is created by dataprocesing.py, which is used to store the most common words in the abstract part of collected papers in the selected time slot. This dataset is useful for generating the wordCount.csv.

\textbf{wordCount.csv}
wordCount.csv is created by dataprocessing.py. Each row in the dataset is the word count the most common words in the abstract part of all the papers published on that date. This datset is useful for generating the Word Frequency Race Diagram.

\textbf{stop_words.csv}
stop_words.csv is a collection of stop words. Usually, stop words are the words that are too common and may appear in all papers. Thus, we can barelly get usefully insights from thesse words and want to exlude them. This dataset is used in dataprocessing.py to filter out the stop words in the abstract part of the papers.

stopwordsCleaner.ipynb is used for customizing the stop words list. User can add or remove words from the list and then run the notebook to remove the duplicated words, sort the list, and save the list to stop_words.csv.
