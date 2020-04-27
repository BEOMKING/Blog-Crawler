from konlpy.tag import Okt

f = open("crawl_result.txt", 'r', encoding='UTF-8')
lines = f.read()

okt = Okt()
#okts = okt.pos(lines, join=True, stem=True)
okts = okt.morphs(lines, stem=True)

w = open("recrawl_result.txt", 'w', encoding='UTF-8')
'''for sentence in okts:
    # 공백줄 건너뛰기
    if sentence == '\u200b':
        continue
    w.write(sentence + '\n')'''
w.write(str(okts))
w.close()