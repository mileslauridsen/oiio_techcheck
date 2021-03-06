import argparse
import oiio_techcheck as oiiotc

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser(description="Check for files of type: "
                                         "'.exr', '.tif', '.hdr', '.jpg', '.png'"
                                         "in input directory.\n"
                                         "Detect stats with oiiotool and return "
                                         "original stats along with a summary of "
                                         "overall min/max and frame numbers of "
                                         "any nans or infs.\n"
                                         "Save each detected sequence's stats as "
                                         "as a JSON file",
                             formatter_class=argparse.RawTextHelpFormatter)

ap.add_argument("-d", "--dirpath",
                required=True,
                help="Path to the directory to check for valid files")

ap.add_argument("-o", "--outpath",
                required=True,
                help="Path to the output directory to save analysis")

arguments = ap.parse_args()

seqdict = oiiotc.seq_stats_checker(arguments.dirpath)

for key in seqdict.keys():
    if key != "path":
        seqdict[key] = oiiotc.find_min_max(seqdict[key])
        seqdict[key] = oiiotc.find_nan_frames(seqdict[key])
        seqdict[key] = oiiotc.find_inf_frames(seqdict[key])
oiiotc.save_techchecks(seqdict, arguments.outpath)
