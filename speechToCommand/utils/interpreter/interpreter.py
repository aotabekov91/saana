import os
import yaml
import inspect
import pickle
import pandas as pd
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from Levenshtein import distance as levenshtein_distance

class Interpreter:

    def __init__(self, path=None):
        self.data_path=path
        self.set_similarity()
        self.load_model()

    def get_similarity(self, t1, t2):
        if (t1, t2) in self.similarity or (t2, t1) in self.similarity:
            return 0
        else:
            return levenshtein_distance(t1, t2)

    def set_similarity(self):
        if self.data_path is None:
            file_path=os.path.abspath(inspect.getfile(self.__class__))
            mode_path=os.path.dirname(file_path).replace('\\', '/')
            self.data_path=f'{mode_path}/model/data.sav'

        dt=yaml.safe_load(open(self.data_path))
        d=pd.DataFrame([{s:d} for s in dt for d in dt[s]]).melt()
        d=d.drop_duplicates()
        d=d[d.notna().all(axis=1)]
        d['similarity']=0
        self.similarity=d.set_index(['variable', 'value']).to_dict()['similarity']

    def set_model(self, save_model=True):
        self.model = LogisticRegression(multi_class='multinomial', solver='lbfgs', max_iter=10000)


        dt=yaml.safe_load(open(self.data_path))
        d=pd.DataFrame([{s:d} for s in dt for d in dt[s]]).melt()
        d=d.drop_duplicates()
        d=d[d.notna().all(axis=1)]

        y=d.variable.values
        x=d.value.values

        self.vectorizer=TfidfVectorizer(min_df=1)
        self.vectorizer.fit(x)
        X=self.vectorizer.transform(x).toarray()

        d['similarity']=0
        self.similarity=d.set_index(['variable', 'value']).to_dict()['similarity']

        d['tmp']=d.variable
        d=d.pivot(columns='tmp', values='similarity', index=['variable', 'value'])
        s=d.apply(lambda r: [self.get_similarity(r.name[1], i) for i in r.index], axis=1).to_dict()
        s=pd.DataFrame(s).T

        D=s.values

        self.A=np.concatenate([X, D], axis=1)
        self.y=y
        self.model.fit(self.A, self.y)

        if save_model:
            file_path=os.path.abspath(inspect.getfile(self.__class__))
            mode_path=os.path.dirname(file_path).replace('\\', '/')
            path=f'{mode_path}/model/model.sav'
            pickle.dump(self.model, open(path, 'wb'))
            path=f'{mode_path}/model/vectorizer.sav'
            pickle.dump(self.vectorizer, open(path, 'wb'))

    def load_model(self):
        file_path=os.path.abspath(inspect.getfile(self.__class__))
        mode_path=os.path.dirname(file_path).replace('\\', '/')
        model_path=f'{mode_path}/model/model.sav'
        vectorizer_path=f'{mode_path}/model/vectorizer.sav'
        if os.path.exists(model_path) and os.path.exists(vectorizer_path):
            self.model=pickle.load(open(model_path, 'rb'))
            self.vectorizer=pickle.load(open(vectorizer_path, 'rb'))
        else:
            self.set_model()

    def predict(self, sentence, prob=0.3):
        words=[]
        raw_data=sentence.split(' ')
        i=0
        while i<len(raw_data):

            success=False
            for j in range(i+1, len(raw_data)+1):
                text=' '.join(raw_data[i:j])

                word=None
                if text in self.model.classes_:
                    word=text
                else:
                    found=False
                    for (item, value), similarity in self.similarity.items():
                        if text==value:
                            word=item
                            found=True
                            break

                    if not found:
                        features=self.vectorizer.transform([text]).toarray()
                        t_length=np.array([self.get_similarity(t1, text) for t1 in self.model.classes_])
                        t_length=t_length.reshape((1,len(t_length)))
                        data=np.concatenate([features, t_length], axis=1)
                        prediction=self.model.predict(data)
                        if prediction:
                            probability=np.max(self.model.predict_proba(data))
                            if prob<probability:
                                word=prediction[0]

                if word:
                    words+=[word]
                    i=j
                    success=True
                    break

            if not success:
                words+=[raw_data[i]]
                i+=1

        new_sentence=' '.join(words)
        print(f'Interpreter [{sentence}]: {new_sentence}')
        return new_sentence


if __name__=='__main__':
    i=Interpreter()
    i.set_model()
