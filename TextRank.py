# -*- coding: utf-8 -*-
from newspaper import Article
from konlpy.tag import Kkma
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize
import numpy as np

kkma = Kkma()
okt = Okt()
stopwords = ['중인' ,'만큼', '마찬가지', '꼬집었', "연합뉴스", "기자",
            "아", "휴", "아이구", "아이쿠", "아이고", "어", "나", "우리", "저희", "따라", "의해", "을", "를", "에", "의", "가",
            "보기", "기타", "복사", "번역", "본문", "비타민", "때문", "무엇", "생각", "보자기", "유포", "출처", "분한",
            "월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일", "영아", "구가", "물어", "비교", "인쇄",
            "오늘", "아빠", "다른", "태풍", "꼼짝", "주말", "평일", "시피", "보통"]
tfidf = TfidfVectorizer()
cnt_vec = CountVectorizer()
graph_sentence = []

def url2sentences(url):
    '''
    url 주소를 받아 기사내용(article.text)을 추출하여
    Kkma.sentences()를 이용하여 문장단위로 나누어 준 후
    senteces를 return 해 준다.
    '''
    article = Article(url, language='ko')
    article.download()
    article.parse()
    sentences = kkma.sentences(article.text)

    for idx in range(0, len(sentences)):
        if len(sentences[idx]) <= 10:
            sentences[idx-1] += (' ' + sentences[idx])
            sentences[idx] = ''

    return sentences

def get_nouns(sentences):
    '''
    sentences를 받아 Okt.nouns()를 이용하여
    명사를 추출한 뒤 nouns를 return 한다.
    '''
    nouns = []
    for sentence in sentences:
        if sentence is not '':
            nouns.append(' '.join([noun for noun in okt.nouns(str(sentence)) if noun not in stopwords and len(noun) > 1]))

    return nouns

def build_sent_graph(sentence):
    '''
    명사로 이루어진 문장을 입력받아
    sklearn의 TfidfVectorizer.fit_transform을 이용하여
    tfidf matrix를 만든 후 Sentence graph를 return 한다.
    '''
    tfidf_mat = tfidf.fit_transform(sentence).toarray()
    graph_sentence = np.dot(tfidf_mat, tfidf_mat.T)
    return graph_sentence

def build_words_graph(sentence):
    '''
    명사로 이루어진 문장을 입력받아
    sklearn의 CountVectorizer.fit_transform을 이용하여
    matrix를 만든 후 word graph와 {idx: word}형태의 dictionary를 return 한다.
    '''
    cnt_vec_mat = normalize(cnt_vec.fit_transform(sentence).toarray().astype(float), axis=0)
    vocab = cnt_vec.vocabulary_
    return np.dot(cnt_vec_mat.T, cnt_vec_mat), {vocab[word] : word for word in vocab}

def get_ranks(graph, d=0.85):       # d = damping factor
    '''
    TextRank 알고리즘 식을 구현한 부분이며,
    {idx : rank 값} 형태의 dictionary를 return 한다.
    '''
    A = graph
    matrix_size = A.shape[0]
    for id in range(matrix_size):
        A[id, id] = 0               # diagonal 부분을 0으로
        link_sum = np.sum(A[:,id])  # A[:, id] = A[:][id]
        if link_sum != 0:
            A[:, id] /= link_sum
        A[:, id] *= -d
        A[id, id] = 1

    B = (1-d) * np.ones((matrix_size, 1))
    ranks = np.linalg.solve(A, B)   # 연립방정식 Ax = b
    return {idx: r[0] for idx, r in enumerate(ranks)}

def summarize(sentences, sorted_sent_rank_idx ,sent_num=3):
    summary = []
    index=[]
    for idx in sorted_sent_rank_idx[:sent_num]:
        index.append(idx)

    index.sort()
    for idx in index:
        summary.append(sentences[idx])

    return summary

def keywords(words_graph, idx2word, word_num=10):
    rank_idx = get_ranks(words_graph)
    sorted_rank_idx = sorted(rank_idx, key=lambda k: rank_idx[k], reverse=True)
    
    keywords = []
    index=[]
    for idx in sorted_rank_idx[:word_num]:
        index.append(idx)

    #index.sort()
    for idx in index:
        keywords.append(idx2word[idx])

    return keywords

def get_keywords(sentences):
    nouns = get_nouns(sentences)

    sent_graph = build_sent_graph(nouns)
    words_graph, idx2word = build_words_graph(nouns)

    return keywords(words_graph, idx2word, 10)

def main(sentences):
    nouns = get_nouns(sentences)

    sent_graph = build_sent_graph(nouns)
    words_graph, idx2word = build_words_graph(nouns)

    sent_rank_idx = get_ranks(sent_graph)
    sorted_sent_rank_idx = sorted(sent_rank_idx, key=lambda k: sent_rank_idx[k], reverse=True)

    word_rank_idx = get_ranks(words_graph)
    sorted_word_rank_idx = sorted(word_rank_idx, key=lambda k: word_rank_idx[k], reverse=True)

    for row in summarize(sentences, sorted_sent_rank_idx, 10):
        print(row)
