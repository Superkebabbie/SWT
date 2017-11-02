linenum = 0
max = 5
for line in open('infobox_properties_en.ttl','r',encoding='utf-8'):
    print(line)
    if linenum == max:
        break
    else:
        linenum += 1