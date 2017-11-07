import re

linenum = 0
max = -1

hit = 0
target = ['http://dbpedia.org/resource/Perryville,_Missouri','http://dbpedia.org/property/county','http://dbpedia.org/resource/Perry_County,_Missouri']

for line in open('../infobox_properties_en.ttl','r',encoding='utf-8'):
    line = line.rstrip(' .\n')
    triple = re.findall('<(.+?)>',line)#also filters out data values, only keeps the templates
    if triple == target:
        hit = linenum
        print(hit)
    if linenum == max:
        break
    else:
        linenum += 1
print(linenum)