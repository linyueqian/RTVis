from collections import Counter
import pandas as pd

stopwords = pd.read_csv('./assets/data/stop_words.csv')
sw = stopwords['0'].tolist()
sw.append('0')

df = pd.read_excel('./demo_dataset.xlsx')
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