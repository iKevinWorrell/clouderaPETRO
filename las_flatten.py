__author__ = 'kw@cloudera.com'
import time
import sys
import re
import uuid

if len(sys.argv) < 3:
    sys.stderr.write('Usage: python las_flatten.py myLASfile myLASoutput delimiter')
    sys.exit(1)

print('#' * 14 + ' Your Command Arguments ' + '#' * 14)
print "\n".join(sys.argv)
print('#' * 52)

print ('Start Time - ' + time.strftime("%d/%m/%Y %H:%M:%S"))

delim = str(sys.argv[3])
curr_block = None
metainfo = []
curveinfo = []
otherinfo = []
asciiinfo = []

with open(str(sys.argv[1]), 'r') as fLAS:
    for line in fLAS:
        if line.startswith('~'):

            if line.startswith('~VERSION'):
                curr_block = 'VERSION'

            elif line.startswith('~WELL'):
                curr_block = 'WELL'

            elif line.startswith('~CURVE'):
                curr_block = 'CURVE'

            elif line.startswith('~O'):
                curr_block = 'OTHER'

            elif line.startswith('~A'):
                curr_block = 'DATA'

        elif curr_block == 'VERSION' and line.startswith('#') is False:
            myline = line.rsplit(':')
            #print('Processing -----> VERSION')
            metainfo.append((curr_block, myline[0].strip(), myline[1].strip()))

        elif curr_block == 'WELL' and line.startswith('#') is False:
            myline = line.rsplit(':')
            #print('Processing -----> WELL')
            metainfo.append((curr_block, myline[0].strip(), myline[1].strip()))

        elif curr_block == 'OTHER' and line.startswith('#') is False:
            myline = line.rsplit(':')
            #print('Processing -----> OTHER')
            otherinfo.append((curr_block, myline[0].strip()))

        elif curr_block == 'CURVE' and line.startswith('#') is False:
            myline = line.rsplit(':')
            #print('Processing -----> CURVE')
            curveinfo.append((myline[0].strip(), myline[1].strip()))

        elif curr_block == 'DATA' and line.startswith('#') is False:
            myline = re.split(r'[ \t]+', line.strip())
            asciiinfo.append((myline))

        elif line.startswith('#'):
            None

        else:
            raise Exception("Unknown section '%s'" % line)
fLAS.close()

with open(str(sys.argv[2]), 'w+') as fLASflat:

    rowheader = 'unique_id'
    for i, e in enumerate(metainfo):
        #    print ('|' + '%03d) %s' % (i, ', '.join(e)))
        rowheader = rowheader + delim + str(e[2].replace(' ', '_')).strip()

    for i, e in enumerate(curveinfo):
        #    print ('|' + '%03d) %s' % (i, ', '.join(e)))
        rowheader = rowheader + delim + str(e[1].replace(' ', '_')).strip()
    fLASflat.write(rowheader + '\n')

    uniqueid = uuid.uuid4()
    rowdata = ''


    for a, ae in enumerate(asciiinfo):
        rowdata = rowdata + str(a + 1) + '-' + str(uniqueid)

        rowmeta = ''
        for b, be in enumerate(metainfo):
        #    print ('|' + '%03d) %s' % (i, ', '.join(e)))
            rowmeta = rowmeta + delim + str(be[1]).strip()

        fLASflat.write((str(a) + '-' + str(uniqueid) + rowmeta + delim + ae[0] + delim + ae[1] + delim + ae[2] + delim + ae[3] + delim + ae[4] + delim + ae[5] + delim + ae[6] + delim + ae[7] + delim + ae[8] + delim + ae[9] + '\n'))

fLASflat.close()






