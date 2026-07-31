import math

def bm25(reverse_index, kw, dl, avdl, k1 = 1.5, b = 0.75):
  # kw = keyword
  # n = number of documents
  # n_kw = number of documents matching query term
  # dl = dictionary of url document lengths
  # avdl = average document length
  # k1 = 1.5, b = 0.75
  n = len(dl)
  n_kw = len(reverse_index[kw])
  result = {}
  idf = math.log((n - n_kw + 0.5) / (n_kw + 0.5) + 1)
  for url, freq in reverse_index[kw].items(): # get_urls: function that shows keyword frequency by url
    numerator = freq * (k1 + 1)
    denominator = freq + k1 * (1 +  b + b * dl[url] / avdl)
    result[url] = idf * numerator / denominator 
  return result
