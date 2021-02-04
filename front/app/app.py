from flask import Flask, render_template, request
#from flask import url_for, flash, redirect
import pickle
from nltk import pos_tag as postag
from nltk import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.snowball import FrenchStemmer
from nltk.stem import PorterStemmer, WordNetLemmatizer
import spacy
import nltk
#nltk.download('averaged_perceptron_tagger')
#dans console
#python -m spacy download fr_core_news_sm
from spacy_lefff import LefffLemmatizer, POSTagger
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from textblob import TextBlob

app = Flask(__name__)
model_fr = pickle.load(open('model_fr.pkl','rb'))
model_en = pickle.load(open('model_en.pkl','rb'))
class_review = ["neutral", "positive", "negative"]
sws_fr = stopwords.words('french')#stopwords fr
sws_en = stopwords.words('english')#stopwords en
list_sw_en_more = ["n't", "not", "no"]
sws_en = sws_en + list_sw_en_more
FrenchStemmer = SnowballStemmer("french") #stemming fr
porter = PorterStemmer() #stemming en


WNlemmatizer = WordNetLemmatizer()#lem en en
nlp = spacy.load("fr_core_news_sm")#lem en fr
pos = POSTagger()
french_lemmatizer = LefffLemmatizer(after_melt=True)
nlp.add_pipe(pos, name='pos', after='parser')
nlp.add_pipe(french_lemmatizer, name='lefff', after='pos')

@app.route('/')
def home():
    name = "nao"
    return render_template('home.html', name=name)

@app.route('/test',methods = ['POST'])
def test():
    result = request.form
    r = result['review']
    #prediction = "positive"
    r_array = [r]
    prediction = pred(r)
    pb_detect = None
    
    if prediction == "oups":
        pb_detect = "exist"
    return render_template('test.html', review=r, prediction=prediction, langue=TextBlob(r).detect_language(), pb_detect=pb_detect)

@app.route('/analyse_2',methods = ['POST'])
def analyse_2():
    result = request.form
    r = result['review']
    l = result['language']
    #prediction = "positive"
    if l == "English":
      prediction = pred_en(r)
    elif l == "French":
      prediction = pred_fr(r)
    return render_template('test.html', review=r, prediction=prediction, langue=l)

def pred_fr(r):
    #ici mettre le code du bon modele de ml en français
    #si ni lemm ni stem
    #r_array = [r]

    text = r
    text = " ".join(x for x in text.split() if (x not in sws_fr and len(x) > 1))
    #si stem
    """
    text = r
    #FrenchStemmer = SnowballStemmer("french")
    wt = word_tokenize(text)
    st = [FrenchStemmer.stem(token) for token in wt ]
    st = ' '.join(st)
    r_array = [st]
    """
    #si lem
    doc = nlp(text)   
    lt=''
    for d in doc:
        #print(d.text, d.pos_, d._.lefff_lemma, d.tag_, d.lemma_)
        lt = lt + " " + d.lemma_
    r_array = [lt]
    
    pred  = model_fr.predict(r_array)[0]
    return class_review[pred]

def pred_en(r):
    #ici mettre le code du bon modele de ml en anglais
    text = r
    text = " ".join(x for x in text.split() if (x not in sws_en and len(x) > 1))
    
    #si stem
    text = r
    wt = word_tokenize(text)
    st = [porter.stem(token) for token in wt ]
    st = ' '.join(st)
    r_array = [st]
    
    
    #si lem
    """
    doc = word_tokenize(text)   
    lt=''
    for d in doc:
        lt = lt + " " + WNlemmatizer.lemmatize(d, get_wordnet_pos(d))
    r_array = [lt]
    """

    pred  = model_en.predict(r_array)[0]
    return class_review[pred]
    

# Définition d'une fonction qui fait le mapping entre les 'POS' de NLTK et ceux de wordnet
def get_wordnet_pos(word):
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)


def pred(r):
    name = None
    if TextBlob(r).detect_language() == "fr":
      return pred_fr(r)
    elif TextBlob(r).detect_language() == "en":
      return pred_en(r)
    else:
      #ni anglais ni francais detecte
      return "oups"
      #return 'Difficultés rencontrés pour détécter la langue. Commentaire trop petit'


if __name__ == '__main__':
	app.run(debug=True)

