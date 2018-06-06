from forpaper import *
def scale_by_max(file_name, sep = ' '):
    f = ""
    try:
        f = open(file_name, 'r')
    except:
        print ('open {} failed'.format(file_name))
        return

    content = f.readlines()
    f.close()
    content = [x.strip() for x in content]
    lines = []
    for cont in content:
        lines.append(cont.split(sep))

    for line in lines:
        line[1] = float(line[1])

    max_val = max([x[1] for x in lines])
    for line in lines:
        line[1] = float(line[1]) / float(max_val)

    list2file(lines, '{}.salced'.format(file_name), line_type = 'list', sep = ': ')
    return lines


scale_by_max('./cookiechangetogether', sep = ': ')
