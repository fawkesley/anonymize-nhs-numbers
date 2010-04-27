#!/usr/bin/python

# FilterNHSNumbers.py
#
# This script looks through any given files and looks for 10 digit numbers which are
# a valid NHS number.
#
# It then attempts to replace each individual NHS number with a pseudonym, which it reads from
# pseudonyms.csv (and writes back afterwards)

import os
import sys
import csv

LOOKUP       = {}
GENERATE_NEW = False

def main():
    loadPseudonyms()

    if len(sys.argv) > 1:
        for fn in sys.argv[1:]:
            filterFile( fn )
    else:
        dirList = os.listdir( os.path.dirname(sys.argv[0]) )
        for fname in dirList:
            split = os.path.splitext(fname)
            if split[1].lower() == '.csv' and split[0].upper()[:5] != 'ANON_' and split[0] != 'pseudonyms':
                filterFile( fname )

    savePseudonyms()

def filterFile( fn ):
    print "Scanning %s..." % fn,
    locations = findNHSNumbers( fn )
    if locations is None:
        print "Failed to open."
        return False
    nhsNumbers = []

    try:
        f = open( "DEP2.CSV", 'rb' )
    except IOError:
        return

    for location in locations:
        f.seek(location)
        nhsNumbers.append( f.read(10) )
    f.close()
        
    print "found %d valid NHS numbers" % (len(locations))
    
    replaceNHSNumbers(fn, locations)
    highlightNHSNumbers(fn, locations)

    
def findNHSNumbers( fn ):
    try:
        f = open(fn, 'rb')
    except IOError:
        return None
    locations = []
    num = 0
    while True:
        c = f.read(1)
        if c == '':
            break
        ascii = ord( c )
        
        if ascii in (48,49,50,51,52,53,54,55,56,57):
            num += 1
        else:
            if num == 10:
                startLocation = f.tell() - 11
                f.seek( startLocation )
                if validateNhsNum( f.read(10) ):
                    locations.append( startLocation )
            num = 0
    return locations


def validateNhsNum(num):
    s = str(num)
    if len(s) != 10:
        return False

    tot = 0
    for i in range(9):
        dig = int( s[i] )
        tot += dig * (10-i)
        
    tmp = tot % 11
    if tmp == 0:
        checksum = 0
    else:
        checksum = 11 - (tot % 11)

    if checksum == 10 or checksum != int(s[9]):
        return False
    else:
        return True


def highlightNHSNumbers(fn, locations):
    outFn = os.path.join( os.path.dirname(fn), os.path.basename(fn) + ".html")
    out = open(outFn, 'wb')

    f = open(fn, 'rb')

    out.write("<PRE>");
    for location in locations:
        buf = f.read(location - f.tell())
        out.write( buf )
        nhsNum = f.read(10)
        pseudo = str( getPseudonym( int(nhsNum)))
        out.write("<span style='background-color: Red'>" + nhsNum + "</span>")
        out.write(" => <span style='background-color: LawnGreen'>" + pseudo + "</span>");

    out.write( f.read() )
    out.write(" </pre>");
    out.close()

def replaceNHSNumbers( fn, locations ):
    f = open(fn, 'rb')

    outFn = os.path.join( os.path.dirname(fn), "ANON_" + os.path.basename(fn))
    out = open(outFn, 'wb')

    for location in locations:
        buf = f.read(location - f.tell())
        out.write( buf )

        pseudo = str( getPseudonym( (int(f.read(10))) ) )
        out.write( pseudo )
        
    out.write( f.read() )
    out.close()
    f.close()


def getPseudonym( nhsNum ):
    global GENERATE_NEW

    pseudo = LOOKUP.get( nhsNum )
    if pseudo is not None:
        return pseudo
    
    if GENERATE_NEW is not True:
        print ("I have encountered a new NHS number (%d) with no pseudonym.\nShould I generate " 
        "new ones for any new NHS numbers I find from now on?") % nhsNum
        response = raw_input("type y or n:")
        if response == 'y':
            GENERATE_NEW = True
        else:
            print "In that case, I will exit now."
            exit()

    while True:
        digits = []
        s = ''
        tot = 0
        for i in range(9):
            if i == 0:
                digit = random.randint(1,9)
            else:
                digit = random.randint(0,9)
            digits.append( digit )
            s += str( digit )
            tot += digit * (10 - i) # (10 - i) is the weighting factor

        
    
    # add checksum digit to the end

        checksum = 11 - (tot % 11)

        if checksum == 11:
            checksum = 0
        if checksum != 10: # 10 is an invalid nhs number
            s += str( checksum )

            pseudo = int(s)
            LOOKUP[ nhsNum ] = pseudo
    
            return pseudo


    
def loadPseudonyms():
    global GENERATE_NEW
    dirs = [os.path.abspath( os.path.dirname(fn) ) for fn in sys.argv]
    
    dirs = list(set(dirs))

    for dir in dirs:
        fn = os.path.join(dir, "pseudonyms.csv")
        try:
            reader = csv.reader( open(fn, 'r') )
        except IOError:
            continue

        print "Reading pseudonyms from %s" %fn
        for line in reader:
            if len(line) > 0:
                try:
                    LOOKUP[ int(line[0]) ] = int(line[1])
                except ValueError:
                    pass

    numLoaded = len(LOOKUP)


    if numLoaded == 0:
        print ("I haven't loaded any pseudonyms, should I just generate a pseudonym for every "
               "NHS number I encounter?");
        if raw_input("Type y or n: ") == 'y':
            GENERATE_NEW = True
    else:
        print "Loaded %d pseudonyms NHS numbers." % numLoaded
        GENERATE_NEW = False
    
        

def savePseudonyms():
    fn = os.path.abspath("pseudonyms.csv")
    print "Saving %d unique NHS Number pseudonyms to %s" % (len(LOOKUP), fn)

    f = open(fn, "w")
    f.write("Real_NHS_Number,Pseudonym_NHS_Number\n")
    for nhsNum in LOOKUP.keys():
        f.write("%d,%d" % (nhsNum, LOOKUP[nhsNum] ) + "\n")


main()
