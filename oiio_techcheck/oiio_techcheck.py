import subprocess
import re
import os
import logging
import datetime
import json
from pathlib import Path
import pyseq

# set logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# create formatter
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s",
                              "%Y-%m-%d %H:%M:%S")

logdir = os.path.join(Path.home(), "oiio_techcheck")
if not os.path.isdir(logdir):
    os.makedirs(logdir)
LOGNAME = "oiio_techcheck_{}.log".format(datetime.datetime.now().strftime("%Y%m%d"))
logfile = os.path.join(logdir, LOGNAME)
output_file_handler = logging.FileHandler(logfile)
output_file_handler.setFormatter(formatter)
log.addHandler(output_file_handler)

OIIOTOOL = "/usr/local/bin/oiiotool"
FILETYPES = ['.exr', '.tif', '.hdr', '.jpg', '.png']


def get_oiio_stats(filepath):
    """
    Get stats and hash for an input file
    Args:
        filepath (str): File path string

    Returns:
        dict: dictionary of file stats and hash
    """
    oiiostats = subprocess.Popen([OIIOTOOL, '--hash', '--stats', filepath],
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
    """
    Check a directory for valid files and return detections for sequences found
    Args:
        dirpath (str): Directory path

    Returns:
        dict: dictionary of sequence file stats and hash
    """
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
    else:
        log.error("Path is not a directory: {0}".format(dirpath))

    # remove empty items
    for item in list(seqdict):
        if not seqdict[item]:
            seqdict.pop(item)
    return seqdict


def find_min_max(seqdetect):
    """
    Check for overall min/max values in input seqdetect frames
    Args:
        seqdetect (dict): dictionary of file stats

    Returns:
        dict: seqdetect with overall min/max for each channel
    """
    if seqdetect['frames']:
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
    """
    Check for any nan values in input seqdetect frames
    Args:
        seqdetect (dict): dictionary of file stats

    Returns:
        dict: seqdetect with frame numbers of any nan's detected
    """
    if seqdetect['frames']:
        seqdetect['nans'] = list()
        for frame in seqdetect['frames']:
            if int(max(seqdetect['frames'][frame]['stats']['nan'])) > 0:
                seqdetect['nans'].append(frame)
    return seqdetect


def find_inf_frames(seqdetect):
    """
    Check for any inf values in input seqdetect frames
    Args:
        seqdetect (dict): dictionary of file stats

    Returns:
        dict: seqdetect with frame numbers of any inf's detected
    """
    if seqdetect['frames']:
        seqdetect['infs'] = list()
        for frame in seqdetect['frames']:
            if int(max(seqdetect['frames'][frame]['stats']['inf'])) > 0:
                seqdetect['infs'].append(frame)
    return seqdetect


def save_techchecks(seqdict, outpath):
    """
    Save all dicts in seqdict to json file
    Args:
        seqdict (dict): dict of sequence stats
        outpath (str): output directory to save files to

    Returns:
        None

    """
    for key in seqdict.keys():
        if key != "path":
            if seqdict[key]['frames']:
                outfilename = os.path.basename(seqdict[key]['path']).split('.')[0]
                outfilepath = os.path.join(outpath, "{0}_{1}.json".format(outfilename, "techcheck"))
                with open(outfilepath, 'w') as outfile:
                    json.dump(seqdict[key], outfile, indent=4)
                    log.info("Saved stats file: {0}".format(outfilepath))
