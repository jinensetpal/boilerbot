import spacy
import numerizer

nlp = spacy.load('en_core_web_trf')
stop_words = nlp.Defaults.stop_words

print("Spacy en_core_web_trf model loaded!")


def remove_stop_words(text):
  text = str(text).lower().split()

  for word in text:
    if word in stop_words:
      text.remove(word)
  
  return " ".join(text)


def get_noun_phrases(text):
  doc = nlp(text.lower())

  res = []

  noun_phrases = list(doc.noun_chunks)
  for word in noun_phrases:
    if word not in stop_words:
      word = remove_stop_words(word)
      if word != "":
        res.append(word)

  return list(set(res))


def get_number(text):
  doc = nlp(text.lower())

  numerized = doc._.numerize()
  
  res = []

  for key in numerized.keys():
    res.append(str(numerized[key]))

  return res