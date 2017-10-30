linenum = 0
max = 100
for line in open('infobox_properties_en.ttl','r',encoding='utf-8'):
    print(line)
    if linenum == 100:
        break
    else:
        linenum += 1