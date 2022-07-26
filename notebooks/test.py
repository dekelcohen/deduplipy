from deduplipy.datasets import load_data
df = load_data(kind='voters')

df.head(2)


from deduplipy.deduplicator import Deduplicator
myDedupliPy = Deduplicator(['name', 'suburb', 'postcode'])


myDedupliPy.fit(df)


res = myDedupliPy.predict(df)
res.sort_values('deduplication_id').head(10)