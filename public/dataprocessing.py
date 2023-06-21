from collections import Counter
import pandas as pd

stopwords = pd.read_csv('./assets/data/stop_words.csv')
sw = stopwords['0'].tolist()
sw.append('0')

df = pd.read_csv('./demo_dataset.csv')
dframe = df[['Date','Abstract']]
dframe = dframe.dropna()
dframe['Abstract'] = dframe['Abstract'].apply(lambda x: ''.join([i.lower() for i in x if i.isalpha() or i == " "]) if x != None else x)\
                                      .apply(lambda x: ' '.join([i for i in x.split() if i not in sw]) if x != None else x)\
                                      .apply(lambda x: ' '.join(list(set(x.split()))) if x != None else x)
                                      
# save to csv
dframe.to_csv('./assets/data/processed_data.csv', index=False)
                                      
#for each row, append to a string str
str = ''
for index, row in dframe.iterrows():
    str = str + row['Abstract']
    
#counter the words
c = Counter(str.split())
df3 = pd.DataFrame.from_dict(c, orient='index').reset_index()
df3.columns = ['word', 'count']
df3 = df3.sort_values(by=['count'], ascending=False)
df3 = df3.head(500)
df3 = df3.reset_index(drop=True)

#make a dictionary with key as words and value as 0
d = dict.fromkeys(df3['word'].tolist(), 0)
# save dictionary to csv, without the value
df3.to_csv('./assets/data/commonWords.csv', index=False, columns=['word'])


df3 = dframe.groupby('Date')
df3 = df3.apply(lambda x: x.sort_values(['Date'], ascending=[True]))
df3 = df3.reset_index(drop=True)

#connect all abstracts in the same date to one string
df4 = df3.groupby('Date')['Abstract'].apply(lambda x: "%s" % ' '.join(x))
df4 = pd.DataFrame(df4)
#reset index
df4 = df4.reset_index()

#new df to create barcharrace
df5 = pd.DataFrame(columns=['Date', 'Word', 'Count'])


#for each abstract, call remove function to remove stopwords and punctuations
for index, row in df4.iterrows():
    #for each word in the abstract, add 1 to the dictionary
    for word in row['Abstract'].split():
        #if wor in the dictionary, add 1
        if word in d:
            d[word] += 1

    df5 = pd.concat([df5, pd.DataFrame([[row['Date'], list(d.keys()), list(d.values())]], columns=['Date', 'Word', 'Count'])])
    
df5.to_csv('./assets/data/wordCount.csv', index=False)
