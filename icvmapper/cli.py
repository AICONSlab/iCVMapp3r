#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
# coding: utf-8

import argcomplete
import argparse
import logging
import os
import sys
import warnings

from icvmapper import __version__
from icvmapper import gui
from icvmapper.segment import icvmapper
from icvmapper.convert import filetype
from icvmapper.preprocess import biascorr, trim_like
from icvmapper.qc import seg_qc, reg_svg
from icvmapper.stats import summary_icv_vols
from icvmapper.utils.depends_manager import add_paths

warnings.simplefilter("ignore")
# warnings.simplefilter("ignore", RuntimeWarning)
# warnings.simplefilter("ignore", FutureWarning)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = "3"


# --------------
# functions


def run_filetype(args):
    filetype.main(args)


def run_icvmapper(args):
    icvmapper.main(args)


def run_icv_seg_summary(args):
    summary_icv_vols.main(args)


def run_seg_qc(args):
    seg_qc.main(args)

def run_reg_svg(args):
    reg_svg.main(args)

def run_utils_biascorr(args):
    biascorr.main(args)


def run_trim_like(args):
    trim_like.main(args)

# --------------
# parser


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    # --------------

    # seg intracranial volume  (icv)
    icv_parser = icvmapper.parsefn()
    parser_seg_icv = subparsers.add_parser('seg_icv', add_help=False, parents=[icv_parser],
                                            help="Segment intracranial volume using a trained CNN",
                                            usage=icv_parser.usage)
    parser_seg_icv.set_defaults(func=run_icvmapper)

    # --------------

    # seg qc
    seg_qc_parser = seg_qc.parsefn()
    parser_seg_qc = subparsers.add_parser('seg_qc', add_help=False, parents=[seg_qc_parser],
                                          help="Create tiled mosaic of segmentation overlaid on structural image",
                                          usage=seg_qc_parser.usage)
    parser_seg_qc.set_defaults(func=run_seg_qc)

    # --------------

    # utils biascorr
    biascorr_parser = biascorr.parsefn()
    parser_utils_biascorr = subparsers.add_parser('bias_corr', add_help=False, parents=[biascorr_parser],
                                                  help="Bias field correct images using N4",
                                                  usage=biascorr_parser.usage)
    parser_utils_biascorr.set_defaults(func=run_utils_biascorr)

    # --------------

    # filetype
    filetype_parser = filetype.parsefn()
    parser_filetype = subparsers.add_parser('filetype', add_help=False, parents=[filetype_parser],
                                            help="Convert the Analyse format to Nifti",
                                            usage=filetype_parser.usage)
    parser_filetype.set_defaults(func=run_filetype)

    # --------------

    # ICV vol seg
    icv_vol_parser = summary_icv_vols.parsefn()
    parser_stats_icv = subparsers.add_parser('stats_icv', add_help=False, parents=[icv_vol_parser],
                                            help="Generates volumetric summary of ICV segmentations",
                                            usage=icv_vol_parser.usage)
    parser_stats_icv.set_defaults(func=run_icv_seg_summary)

    # --------------

    # trim like
    trim_parser = trim_like.parsefn()

    parser_trim_like = subparsers.add_parser('trim_like', help='Trim or expand image in same space like reference',
                                             add_help=False, parents=[trim_parser],
                                             usage='%(prog)s -i [ img ] -r [ ref ] -o [ out ] \n\n'
                                                   'Trim or expand image in same space like reference')
    parser_trim_like.set_defaults(func=run_trim_like)

    # --------------------

    # version
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {version}'.format(version=__version__))

    return parser


# --------------
# main fn

def main(args=None):
    """ main cli call"""
    if args is None:
        args = sys.argv[1:]

    parser = get_parser()
    argcomplete.autocomplete(parser)
    args = parser.parse_args(args)

    if hasattr(args, 'func'):

        # set filename, file path for the log file
        log_filename = args.func.__name__.split('run_')[1]
        if hasattr(args, 'subj'):
            if args.subj:
                log_filepath = os.path.join(args.subj, 'logs', '{}.log'.format(log_filename))

            elif hasattr(args, 't1w'):
                if args.t1w:
                    log_filepath = os.path.join(os.path.dirname(args.t1w), 'logs', '{}.log'.format(log_filename))

        else:
            log_filepath = os.path.join(os.getcwd(), '{}.log'.format(log_filename))

        os.makedirs(os.path.dirname(log_filepath), exist_ok=True)

        # log keeps console output and redirects to file
        root = logging.getLogger('interface')
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
        handler = logging.FileHandler(filename=log_filepath)
        handler.setFormatter(formatter)
        root.addHandler(handler)

        with add_paths():
            args.func(args)

    else:
        gui.main()


if __name__ == '__main__':
    main()
