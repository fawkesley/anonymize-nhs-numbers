#!/usr/bin/python

# FilterNHSNumbers.py
#
# This script looks through any given files and looks for 10 digit numbers
# which are a valid NHS number.
#
# It then attempts to replace each individual NHS number with a pseudonym,
# which it reads from pseudonyms.csv (and writes back afterwards)

import csv
import os
import random
import sys

LOOKUP = {}
GENERATE_NEW = False


def main():
    load_pseudonyms()

    if len(sys.argv) > 1:
        for fn in sys.argv[1:]:
            filter_file(fn)
    else:
        dirList = os.listdir(os.path.dirname(sys.argv[0]))
        for fname in dirList:
            split = os.path.splitext(fname)
            if (split[1].lower() == '.csv' and split[0].upper()[:5] != 'ANON_'
                    and split[0] != 'pseudonyms'):
                filter_file(fname)

    save_pseudonyms()


def filter_file(fn):
    print("Scanning %s..." % fn)
    locations = find_nhs_numbers(fn)
    if locations is None:
        print("Failed to open.")
        return False
    nhs_numbers = []

    try:
        f = open("DEP2.CSV", 'rb')
    except IOError:
        return

    for location in locations:
        f.seek(location)
        nhs_numbers.append(f.read(10))
    f.close()

    print("found %d valid NHS numbers" % len(locations))

    replace_nhs_numbers(fn, locations)


def find_nhs_numbers(fn):
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
        ascii_ = ord(c)

        if ascii_ in (48, 49, 50, 51, 52, 53, 54, 55, 56, 57):
            num += 1
        else:
            if num == 10:
                startLocation = f.tell() - 11
                f.seek(startLocation)
                if validate_nhs_number(f.read(10)):
                    locations.append(startLocation)
            num = 0
    return locations


def validate_nhs_number(num):
    s = str(num)
    if len(s) != 10:
        return False

    tot = 0
    for i in range(9):
        dig = int(s[i])
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


def replace_nhs_numbers(fn, locations):

    outFn = os.path.join(os.path.dirname(fn), "ANON_" + os.path.basename(fn))
    with open(fn, 'rb') as f, open(outFn, 'wb') as out:

        for location in locations:
            buf = f.read(location - f.tell())
            out.write(buf)

            pseudo = str(get_pseudonym((int(f.read(10)))))
            out.write(pseudo)

        out.write(f.read())


def get_pseudonym(nhs_number):
    global GENERATE_NEW

    pseudo = LOOKUP.get(nhs_number)
    if pseudo is not None:
        return pseudo

    if GENERATE_NEW is not True:
        print("I have encountered a new NHS number (%d) with no pseudonym.\n"
              "Should I generate new ones for any new NHS numbers I find "
              "from now on?" % nhs_number)
        response = raw_input("type y or n:")
        if response == 'y':
            GENERATE_NEW = True
        else:
            print("In that case, I will exit now.")
            exit()

    while True:
        digits = []
        s = ''
        tot = 0
        for i in range(9):
            if i == 0:
                digit = random.randint(1, 9)
            else:
                digit = random.randint(0, 9)
            digits.append(digit)
            s += str(digit)
            tot += digit * (10 - i)  # (10 - i) is the weighting factor

        checksum = 11 - (tot % 11)

        if checksum == 11:
            checksum = 0
        if checksum != 10:  # 10 is an invalid nhs number
            s += str(checksum)

            pseudo = int(s)
            LOOKUP[nhs_number] = pseudo

            return pseudo


def load_pseudonyms():
    global GENERATE_NEW
    dirs = [os.path.abspath(os.path.dirname(fn)) for fn in sys.argv]

    dirs = list(set(dirs))

    for dir_ in dirs:
        fn = os.path.join(dir_, "pseudonyms.csv")
        try:
            reader = csv.reader(open(fn, 'r'))
        except IOError:
            continue

        print("Reading pseudonyms from %s" % fn)
        for line in reader:
            if len(line) > 0:
                try:
                    LOOKUP[int(line[0])] = int(line[1])
                except ValueError:
                    pass

    num_loaded = len(LOOKUP)

    if num_loaded == 0:
        print("I haven't loaded any pseudonyms, should I just generate a "
              "pseudonym for every NHS number I encounter?")
        if raw_input("Type y or n: ") == 'y':
            GENERATE_NEW = True
    else:
        print("Loaded %d pseudonyms NHS numbers." % num_loaded)
        GENERATE_NEW = False


def save_pseudonyms():
    fn = os.path.abspath("pseudonyms.csv")
    print("Saving %d unique NHS Number pseudonyms to %s" % (len(LOOKUP), fn))

    f = open(fn, "w")
    f.write("Real_NHS_Number,Pseudonym_NHS_Number\n")
    for nhs_number in LOOKUP.keys():
        f.write("%d,%d" % (nhs_number, LOOKUP[nhs_number]) + "\n")


main()
