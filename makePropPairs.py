import re, csv, sys
import JoostKit
from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions

linenum = 0
max = -1

ensparql = SPARQLWrapper("http://dbpedia.org/sparql")
nlsparql = SPARQLWrapper("http://nl.dbpedia.org/sparql")
ensparql.setReturnFormat(JSON)
nlsparql.setReturnFormat(JSON)

def doQuery(query,sparql):
    sparql.setQuery(query)
    results = None
    while results == None:
        try:
            results = sparql.query().convert()["results"]["bindings"]
        except Exception as e:
            print("FAILED, retrying!")
    return results

def getLanguage(uri):
    #return the domain the uri is from (nl/en)
    if uri.startswith('http://nl.dbpedia.org'):
        return 'nl'
    elif uri.startswith('http://dbpedia.org'):
        return 'en'
    else:
        # print("Unknown source domain for " + uri)
        return None

def getDutchResource(srcUri):
    #go from a English source to the Dutch counterpart
    query = 'select ?p where {<' + srcUri + '> <http://www.w3.org/2002/07/owl#sameAs> ?p .}'
    results = doQuery(query,ensparql)
    resources = []
    for r in results:
        p = r['p']['value']
        if p.startswith('http://nl.dbpedia.org'):#filter Dutch resources
            resources.append(p)
    return resources
    
def getEnglishResource(srcUri):
    #go from a Dutch source to the English counterpart
    query = 'select ?p where {<' + srcUri + '> <http://www.w3.org/2002/07/owl#sameAs> ?p .}'
    results = doQuery(query,nlsparql)
    resources = []
    for r in results:
        p = r['p']['value']
        if p.startswith('http://dbpedia.org'):#filter Dutch resources
            resources.append(p)
    return resources
    
def getOtherResource(srcUri):
    #automatically determine if you're going from English to Dutch or vice versa
    if getLanguage(srcUri) == 'nl':
        return getEnglishResource(srcUri)
    elif getLanguage(srcUri) == 'en':
        return getDutchResource(srcUri)
        
def getSameAs(srcUri):
    results = []
    source = getRelations(srcUri)
    for p,r in source:
        if 'sameAs' in p:
            results.append(r)
    return results
    
def isURI(s):
    #determine whether string s is a URI (rather than a data value)
    return s.startswith('http://')#TODO (good enough?)
    
def isDBPedia(s):
    #determine whether URI is from DBPedia
    return isURI(s) and 'dbpedia' in s
    
def isInScope(s):
    #further limit resources we're looking at by filtering only the Dutch and English resources
    return isDBPedia and (s.startswith('http://dbpedia.org') or s.startswith('http://nl.dbpedia.org'))
    
def URIname(uri):
    #get the printable name from a URI
    return uri[uri.rfind('/')+1:]
    
def printMatch(o1,p1,r1,o2,p2,r2):
    JoostKit.tablePrint('origin\tproperty\ttarget\n%s\t%s\t%s\n%s\t%s\t%s'%(o1,p1,r1,o2,p2,r2))
    
def readProppairs(filename):
    reader = csv.reader(open(filename,'r',encoding='utf-8',newline=''),delimiter='\t')
    proppairs = {}
    for line in reader:
        assert(len(line)==3)
        proppairs[(line[0],line[1])] = int(line[2])
    return proppairs
    
def writeMatches(filename,proppairs):
    writer = csv.writer(open(filename,'w',encoding='utf-8',newline=''),delimiter='\t')
    for match in proppairs:
        writer.writerow([match[0],match[1],proppairs[match]])
        
filename = sys.argv[1]
proppairs = readProppairs(sys.argv[2])
for line in open(filename,'r',encoding='utf-8'):
    try:
        line = line.rstrip(' .\n')
        triple = re.findall('<(.+?)>',line)#also filters out data values, only keeps the templates
        if len(triple) == 3:
            o1, p1, r1 = triple
            if isInScope(o1) and isInScope(r1) and not 'wiki' in p1:
                #This line can and will be used
                o2s = getOtherResource(o1)
                if o2s == []:
                    o2s = [o1]
                r2s = getOtherResource(r1)
                if r2s == []:
                    r2s = [r1]
                for o2 in o2s:
                    for r2 in r2s:
                        results = doQuery('select ?p where {<%s> ?p <%s> .}'%(o2,r2),nlsparql)
                        for r in results:
                            p2 = r['p']['value']
                            if 'wiki' not in p2:
                                printMatch(o1,p1,r1,o2,p2,r2)
                                match = tuple(sorted((p1,p2)))#assures a certain ordering for easy lookup
                                if match in proppairs:
                                    proppairs[match] += 1
                                else:
                                    proppairs[match] = 1
                if linenum == max:
                    break
                else:
                    linenum += 1
    except KeyboardInterrupt:
        print("EMERGENCY BREAK")#still write to file before continuing with the abort
        writeMatches(sys.argv[2], proppairs)        
        raise
writeMatches(sys.argv[2], proppairs)