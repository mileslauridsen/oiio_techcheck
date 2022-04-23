import subprocess
import re
import os
import sys
import logging
import datetime
import json
import pyseq
from pathlib import Path

# set logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# create formatter
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s",
                              "%Y-%m-%d %H:%M:%S")

logdir = os.path.join(Path.home(), "oiio_techcheck")
if not os.path.isdir(logdir):
    os.makedirs(logdir)
logname = "oiio_techcheck_{}.log".format(datetime.datetime.now().strftime("%Y%m%d"))
logfile = os.path.join(logdir, logname)
output_file_handler = logging.FileHandler(logfile)
output_file_handler.setFormatter(formatter)
log.addHandler(output_file_handler)

OIIOTOOL = "/usr/local/bin/oiiotool"


def get_oiio_stats(filename):
    oiiostats = subprocess.Popen([OIIOTOOL, '--hash', '--stats', filename],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)

    stdout, stderr = oiiostats.communicate()

    hash_re = '[A-Z0-9]+'
    number_re = '[0-9.]+'

    statsdict = dict()

    if stdout:
        statsdict['hash'] = re.findall(hash_re, stdout.split('\n')[1].split(':')[1])
        statsdict['min'] = re.findall(number_re, stdout.split('\n')[2])
        statsdict['max'] = re.findall(number_re, stdout.split('\n')[3])
        statsdict['avg'] = re.findall(number_re, stdout.split('\n')[4])
        statsdict['stddev'] = re.findall(number_re, stdout.split('\n')[5])
        statsdict['nan'] = re.findall(number_re, stdout.split('\n')[6])
        statsdict['inf'] = re.findall(number_re, stdout.split('\n')[7])

    if stderr:
        log.error(stderr)

    return statsdict


def seq_checker(dirpath):
    seqdict = dict()
    if os.path.isdir(dirpath):
        seqdict['path'] = dirpath
        for seq in pyseq.get_sequences(dirpath):
            seqkey = os.path.basename(seq.name).split('.')[0]
            seqdict[seqkey] = dict()
            for file in seq:
                frame = str(file.frame).zfill(file.pad)
                seqdict[seqkey][frame] = dict()
                statsdict = get_oiio_stats(file.path)
                seqdict[seqkey][frame]['stats'] = statsdict
    minimum = [1000000.0, 1000000.0, 1000000.0]
    maximum = [0.0, 0.0, 0.0]

    for item in seqdict[list(seqdict.keys())[1]]:
        maxlist = seqdict[list(seqdict.keys())[1]][item]['stats']['max']
        minlist = seqdict[list(seqdict.keys())[1]][item]['stats']['min']
        for i in range(0, 3):
            if float(maxlist[i]) > maximum[i]:
                maxlist[i] = float(maxlist[i])
            if float(minlist[0]) < minimum[i]:
                minimum[i] = float(minlist[i])
        seqdict['maximum'] = maxlist
        seqdict['minimum'] = minlist

    return seqdict


def save_techcheck(seqdict, outpath):
    outfilepath = os.path.join(outpath, "{0}_{1}.json".format(os.path.basename(seqdict['path']), "techcheck"))
    with open(outfilepath, 'w') as outfile:
        json.dump(seqdict, outfile)


if __name__ == "__main__":
    dirpath = sys.argv[1]
    outpath = sys.argv[2]
    seqdict = seq_checker(dirpath)
    save_techcheck(seqdict, outpath)
