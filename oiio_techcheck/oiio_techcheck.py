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
FILETYPES = ['.exr', '.tif', '.hdr', '.jpg', '.png']


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


def seq_stats_checker(dirpath):
    seqdict = dict()
    if os.path.isdir(dirpath):
        log.info("Checking dirpath: {0}".format(dirpath))
        seqdict['path'] = dirpath
        seqs = pyseq.get_sequences(dirpath)
        if seqs:
            for seq in seqs:
                seqkey = os.path.basename(seq.name).split('.')[0]
                seqdict[seqkey] = dict()
                seqdict[seqkey]['frames'] = dict()
                seqdict[seqkey]['path'] = os.path.join(seqdict['path'], str(seq))
                for file in seq:
                    if Path(file.path).suffix.lower() in FILETYPES:
                        frame = str(file.frame).zfill(file.pad)
                        seqdict[seqkey]['frames'][frame] = dict()
                        if os.path.isfile(file.path):
                            statsdict = get_oiio_stats(file.path)
                            seqdict[seqkey]['frames'][frame]['stats'] = statsdict

    # remove empty items
    for item in list(seqdict):
        if not seqdict[item]:
            seqdict.pop(item)
    return seqdict


def find_min_max(seqdetect):
    if seqdetect:
        maxred = [seqdetect['frames'][x]['stats']['max'][0] for x in seqdetect['frames']]
        maxgreen = [seqdetect['frames'][x]['stats']['max'][1] for x in seqdetect['frames']]
        maxblue = [seqdetect['frames'][x]['stats']['max'][2] for x in seqdetect['frames']]
        minred = [seqdetect['frames'][x]['stats']['min'][0] for x in seqdetect['frames']]
        mingreen = [seqdetect['frames'][x]['stats']['min'][1] for x in seqdetect['frames']]
        minblue = [seqdetect['frames'][x]['stats']['min'][2] for x in seqdetect['frames']]

        seqdetect['maximum'] = max(maxred), max(maxgreen), max(maxblue)
        seqdetect['minimum'] = min(minred), min(mingreen), min(minblue)

        return seqdetect


def find_nan_frames(seqdetect):
    seqdetect['nans'] = list()
    if seqdetect:
        for frame in seqdetect['frames']:
            if int(max(seqdetect['frames'][frame]['stats']['nan'])) > 0:
                seqdetect['nans'].append(frame)
    return seqdetect


def find_inf_frames(seqdetect):
    seqdetect['infs'] = list()
    if seqdetect:
        for frame in seqdetect['frames']:
            if int(max(seqdetect['frames'][frame]['stats']['inf'])) > 0:
                seqdetect['infs'].append(frame)
    return seqdetect


def save_techcheck(seqdetect, outpath):
    outfilename = os.path.basename(seqdetect['path']).split('.')[0]
    outfilepath = os.path.join(outpath, "{0}_{1}.json".format(outfilename, "techcheck"))
    with open(outfilepath, 'w') as outfile:
        json.dump(seqdetect, outfile, indent=4)


if __name__ == "__main__":
    dirpath = sys.argv[1]
    outpath = sys.argv[2]
    seqdict = seq_stats_checker(dirpath)

    for key in seqdict.keys():
        if key != "path":
            seqdict[key] = find_min_max(seqdict[key])
            seqdict[key] = find_nan_frames(seqdict[key])
            seqdict[key] = find_inf_frames(seqdict[key])
            save_techcheck(seqdict[key], outpath)
