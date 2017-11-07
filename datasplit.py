linenum = 0
max = -1

hit = 0
target = ['http://dbpedia.org/resource/Perryville,_Missouri','http://dbpedia.org/property/county','http://dbpedia.org/resource/Perry_County,_Missouri']

filenum = 1
linesPerFile = 5000
lineCounter = 0
filename = 'data/infobox_properties_en_part%d.ttl'%filenum 
file = open(filename,'w',encoding='utf-8')

def isURI(s):
    #determine whether string s is a URI (rather than a data value)
    return s.startswith('http://')#TODO (good enough?)
    
def isDBPedia(s):
    #determine whether URI is from DBPedia
    return isURI(s) and 'dbpedia' in s

for line in open('../infobox_properties_en.ttl','r',encoding='utf-8'):
    line = line.rstrip(' .\n')
    triple = line.split()
    if len(triple) == 3:
        o1, p1, r1 = triple
        o1 = o1.lstrip('<').rstrip('>')
        r1 = r1.lstrip('<').rstrip('>')
        if isDBPedia(o1) and isDBPedia(r1) and not 'wiki' in p1:#filters out data values and non dbpedia sources
            print(triple)
            file.write(line)
            lineCounter += 1
            if lineCounter == linesPerFile:
                file.close()
                filenum += 1
                filename = 'data/infobox_properties_en_part%d.ttl'%filenum 
                file = open(filename,'w',encoding='utf-8')
                lineCounter = 0
            else:
                file.write('\n')
    if linenum == max:
        break
    else:
        linenum += 1
print(linenum)