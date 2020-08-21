#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
# coding: utf-8

import os
import sys
import glob
from datetime import datetime
from pathlib import Path
import argcomplete
import argparse
import numpy as np
import nibabel as nib
from nilearn.image import reorder_img, resample_img, resample_to_img, largest_connected_component_img, smooth_img, \
    math_img
from nipype.interfaces.c3 import C3d
from icvmapper.utils import endstatement
from icvmapper.deep.predict import run_test_case
from icvmapper.preprocess import biascorr
from icvmapper.qc import seg_qc
import subprocess
import warnings
from termcolor import colored

warnings.simplefilter("ignore", RuntimeWarning)
warnings.simplefilter("ignore", FutureWarning)
warnings.simplefilter("ignore", UserWarning)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = "3"

###########################################       Functions        #####################################################
def parsefn():
    parser = argparse.ArgumentParser(usage='%(prog)s -s [ subj ] \n\n'
                                     "Brain extraction (skull-striping) using a trained CNN")

    optional = parser.add_argument_group('optional arguments')

    optional.add_argument('-s', '--subj', type=str, metavar='', help="input subject")
    optional.add_argument('-fl', '--flair', type=str, metavar='', help="input Flair")
    optional.add_argument('-t1', '--t1w', type=str, metavar='', help="input T1-weighted")
    optional.add_argument('-t2', '--t2w', type=str, metavar='', help="input T2-weighted")
    optional.add_argument('-o', '--out', type=str, metavar='', help="output prediction")
    optional.add_argument('-b', '--bias', help="bias field correct image before segmentation",
                          action='store_true')
    optional.add_argument("-rc", "--rmcereb", type=int, metavar='', default=0, help="remove cerebellum")
    optional.add_argument("-ign_ort", "--ign_ort",  action='store_true',
                          help="ignore orientation if tag is wrong")
    optional.add_argument('-f', '--force', help="overwrite existing segmentation", action='store_true')
    optional.add_argument('-n', '--num_mc', type=int, metavar='', help="number of Monte Carlo Dropout samples", default=20)
    optional.add_argument('-th', '--thresh', type=float, metavar='', help="threshold", default=0.5)
    optional.add_argument('-ss', '--session', type=str, metavar='', help="input session for longitudinal studies")

    return parser

def parse_inputs(parser, args):
    if isinstance(args, list):
        args = parser.parse_args(args)
    argcomplete.autocomplete(parser)

    # check if subj or t1w are given
    if (args.subj is None) and (args.t1w is None):
        sys.exit('subj (-s) or t1w (-t1) must be given')

    # get subject dir if cross-sectional or longitudinal
    if args.subj:
        if args.session:
            subj_dir = os.path.abspath(glob.glob(os.path.join(args.subj, '*%s' % args.session))[0])
        else:
            subj_dir = os.path.abspath(args.subj)
    else:
        subj_dir = os.path.abspath(os.path.dirname(args.t1w))

    subj = os.path.basename(subj_dir)
    print('\n input subject:', subj)

    t1 = args.t1w if args.t1w is not None else '%s/%s_T1_nu.nii.gz' % (subj_dir, subj)
    assert os.path.exists(t1), "%s does not exist ... please check path and rerun script" % t1
    if args.subj is not None:
        fl = '%s/%s_T1acq_nu_FL.nii.gz' % (subj_dir, subj)
        t2 = '%s/%s_T1acq_nu_T2.nii.gz' % (subj_dir, subj)
    else:
        fl = args.flair
        t2 = args.t2w

    woc = args.rmcereb

    out = args.out if args.out is not None else None

    bias = True if args.bias else False

    num_mc = args.num_mc

    thresh = args.thresh

    ign_ort = True if args.ign_ort else False

    force = True if args.force else False

    return subj_dir, subj, t1, fl, t2, woc, out, bias, num_mc, thresh, ign_ort, force

def orient_img(in_img_file, orient_tag, out_img_file):
    c3 = C3d()
    c3.inputs.in_file = in_img_file
    c3.inputs.args = "-orient %s" % orient_tag
    c3.inputs.out_file = out_img_file
    c3.run()

def check_orient(in_img_file, r_orient, l_orient, out_img_file):
    """
    Check image orientation and re-orient if not in standard orientation (RPI or LPI)
    :param in_img_file: input_image
    :param r_orient: right ras orientation
    :param l_orient: left las orientation
    :param out_img_file: output oriented image
    """
    res = subprocess.run('c3d %s -info' % in_img_file, shell=True, stdout=subprocess.PIPE)
    out = res.stdout.decode('utf-8')
    ort_str = out.find('orient =') + 9
    img_ort = out[ort_str:ort_str + 3]

    cp_orient = False
    if (img_ort != r_orient) and (img_ort != l_orient):
        print("\n Warning: input image is not in RPI or LPI orientation.. "
              "\n re-orienting image to standard orientation based on orient tags (please make sure they are correct)")

        if img_ort == 'Obl':
            img_ort = out[-5:-2]
            orient_tag = 'RPI' if 'R' in img_ort else 'LPI'
        else:
            orient_tag = 'RPI' if 'R' in img_ort else 'LPI'
        print(orient_tag)
        orient_img(in_img_file, orient_tag, out_img_file)
        cp_orient = True
    return cp_orient

# def resample(image, new_shape, interpolation="continuous"):
#     print("\n resampling ...")
#     input_shape = np.asarray(image.shape, dtype=image.get_data_dtype())
#     ras_image = reorder_img(image, resample=interpolation)
#     output_shape = np.asarray(new_shape)
#     new_spacing = input_shape / output_shape
#     new_affine = np.copy(ras_image.affine)
#     new_affine[:3, :3] = ras_image.affine[:3, :3] * np.diag(new_spacing)
#
#     return resample_img(ras_image, target_affine=new_affine, target_shape=output_shape, interpolation=interpolation)

def cutoff_img(in_file, cutoff_percents, out_file):
    print("\n thresholding ...")
    img = nib.load(in_file)
    data = img.get_data()
    cutoff_low = np.percentile(data, cutoff_percents)
    cutoff_high = np.percentile(data, 100-cutoff_percents)
    new_data = data.copy()
    new_data[new_data > cutoff_high] = cutoff_high
    new_data[new_data < cutoff_low] = cutoff_low
    nib.save(nib.Nifti1Image(new_data, img.affine), out_file)

def normalize_sample_wise_img(in_file, out_file):
    image = nib.load(in_file)
    img = image.get_data()
    # standardize intensity for data
    print("\n standardizing ...")
    std_img = (img - img.mean()) / img.std()
    nib.save(nib.Nifti1Image(std_img, image.affine), out_file)

def resample(img, x, y, z, out, interp=0):
    print("\n resmapling ...")
    c3 = C3d()
    c3.inputs.in_file = img
    c3.inputs.args = "-int %s -resample %sx%sx%s" % (interp, x, y, z)
    c3.inputs.out_file = out
    c3.run()

def trim(in_img_file, out_img_file, voxels=1):
    print("\n cropping ...")
    c3 = C3d()
    c3.inputs.in_file = in_img_file
    c3.inputs.args = "-trim %svox" % voxels
    c3.inputs.out_file = out_img_file
    c3.run()

def trim_like(in_img_file, ref_img_file, out_img_file, interp = 0):
    print("\n cropping ...")
    c3 = C3d()
    c3.inputs.in_file = ref_img_file
    c3.inputs.args = "-int %s %s -reslice-identity" % (interp, in_img_file)
    c3.inputs.out_file = out_img_file
    c3.run()

def copy_orient(in_img_file, ref_img_file, out_img_file):
    print("\n copy orientation ...")
    c3 = C3d()
    c3.inputs.in_file = ref_img_file
    c3.inputs.args = "%s -copy-transform -type uchar" % in_img_file
    c3.inputs.out_file = out_img_file
    c3.run()

def fill_holes(in_img_file, out_img_file):
    c3 = C3d()
    c3.inputs.in_file = in_img_file
    c3.inputs.args = "-holefill 1 0 -type uchar"
    c3.inputs.out_file = out_img_file
    c3.run()

def convert(in_img_file, out_img_file):
    subprocess.run('c3d %s -o %s' % (in_img_file, out_img_file), shell=True, stdout=subprocess.PIPE)

###########################################        Main        #########################################################
def main(args):
    parser = parsefn()
    subj_dir, subj, t1, fl, t2, woc, out, bias, num_mc, thresh, ign_ort, force = parse_inputs(parser, args)
    cp_orient = False

    if out is None:
        prediction = '%s/%s_T1acq_nu_HfB_pred.nii.gz' % (subj_dir, subj) \
            # if bias is True else '%s/%s_T1acq_HfB_pred.nii.gz' % (subj_dir, subj)
        prediction_std_orient = '%s/%s_T1acq_nu_HfB_pred_std_orient.nii.gz' % (subj_dir, subj)
    else:
        prediction = out
        prediction_std_orient = "%s/%s_std_orient.nii.gz" % (subj_dir, os.path.basename(out).split('.')[0])

    if os.path.exists(prediction) and force is False:
        print("\n %s already exists" % prediction)
    else:
        start_time = datetime.now()

        hfb = os.path.realpath(__file__)
        hyper_dir = Path(hfb).parents[2]

        if fl is None and t2 is None:
            test_seqs = [t1]
            training_mods = ["t1"]
            model_name = 'hfb_t1only_mcdp_multi'
            model_name_woc = 'hfb_t1'
            print("\n found only t1-w, using the %s model" % model_name)

        elif t2 is None and fl:
            test_seqs = [t1, fl]
            training_mods = ["t1", "flair"]
            model_name = 'hfb_t1fl_mcdp_multi'
            model_name_woc = 'hfb_t1fl'
            print("\n found t1 and fl sequences, using the %s model" % model_name)

        elif fl is None and t2:
            test_seqs = [t1, t2]
            training_mods = ["t1", "t2"]
            model_name = 'hfb_t1t2_mcdp_multi'
            model_name_woc = 'hfb_t1t2'
            print("\n found t1 and t2 sequences, using the %s model" % model_name)

        else:
            test_seqs = [t1, fl, t2]
            training_mods = ["t1", "flair", "t2"]
            model_name = 'hfb_multi_mcdp_contrast'
            model_name_woc = 'hfb_t1flt2_mcdp_contrast'
            print("\n found all 3 sequences, using the full %s model" % model_name)

        model_json = '%s/models/%s_model.json' % (hyper_dir, model_name)
        model_weights = '%s/models/%s_model_weights.h5' % (hyper_dir, model_name)

        assert os.path.exists(model_json), "%s does not exist ... please download and rerun script" % model_json
        assert os.path.exists(model_weights), "%s does not exist ... please download and rerun script" % model_weights

        # pred preprocess dir
        print(colored("\n pre-processing %s..." % os.path.abspath(subj_dir), 'green'))
        pred_dir = "%s/pred_process_hfb" % os.path.abspath(subj_dir)
        if not os.path.exists(pred_dir):
            os.mkdir(pred_dir)

        # pred_dir_mcdp = "%s/pred_process_mcdp" % os.path.abspath(subj_dir)
        # if not os.path.exists(pred_dir_mcdp):
        #     os.mkdir(pred_dir_mcdp)

        #############
        if bias is True:
            # t1_bias = os.path.join(subj_dir, "%s_T1_nu.nii.gz" % os.path.basename(t1).split('.')[0])
            t1_bias = os.path.join(subj_dir, "%s_T1_nu.nii.gz" % subj)
            biascorr.main(["-i", "%s" % t1, "-o", "%s" % t1_bias])
            in_ort = t1_bias
        else:
            in_ort = os.path.join(subj_dir, "%s.nii.gz" % os.path.basename(t1).split('.')[0])
            in_ort = in_ort if os.path.exists(in_ort) else convert(t1, in_ort)
            # in_ort = t1


        # std orientations
        r_orient = 'RPI'
        l_orient = 'LPI'
        # check orientation
        t1_ort = "%s/%s_std_orient.nii.gz" % (subj_dir, os.path.basename(t1).split('.')[0])
        if ign_ort is False:
            cp_orient = check_orient(in_ort, r_orient, l_orient, t1_ort)

        # loading t1
        in_t1 = t1_ort if os.path.exists(t1_ort) else in_ort
        t1_img = nib.load(in_t1)

        ###########
        c3 = C3d()
        pred_shape = [160, 160, 160]
        test_data = np.zeros((1, len(training_mods), pred_shape[0], pred_shape[1], pred_shape[2]), dtype=t1_img.get_data_dtype())

        for s, seq in enumerate(test_seqs):
            print(colored("\n pre-processing %s" % os.path.basename(seq).split('.')[0], 'green'))


            seq_ort = "%s/%s_std_orient.nii.gz" % (subj_dir, os.path.basename(seq).split('.')[0])
            if training_mods[s] != 't1':
                if training_mods[s] == 'flair':
                    seq_bias = os.path.join(subj_dir, "%s_T1acq_nu_FL.nii.gz" % subj)
                else:
                    seq_bias = os.path.join(subj_dir, "%s_T1acq_nu_T2.nii.gz" % subj)

                if bias is True:
                    biascorr.main(["-i", "%s" % seq, "-o", "%s" % seq_bias])
                seq = seq_bias if os.path.exists(seq_bias) else seq
                # check orientation
                if ign_ort is False:
                    cp_orient_seq = check_orient(seq, r_orient, l_orient, seq_ort)
            in_seq = seq_ort if os.path.exists(seq_ort) else seq

            # cropping
            if training_mods[s] == 't1':
                crop_file = '%s/%s_cropped.nii.gz' % (pred_dir, os.path.basename(seq).split('.')[0])
                trim(in_seq, crop_file, voxels=1)
            else:
                crop_file = '%s/%s_cropped.nii.gz' % (pred_dir, os.path.basename(seq).split('.')[0])
                ref_file = '%s/%s_cropped.nii.gz' % (pred_dir, os.path.basename(t1).split('.')[0])
                trim_like(in_seq, ref_file, crop_file, interp=1)

            # thresholding, standardize intensity and resampling  for data
            thresh_file = '%s/%s_cropped_thresholded.nii.gz' % (pred_dir, os.path.basename(seq).split('.')[0])
            cutoff_percents = 5.0
            cutoff_img(crop_file, cutoff_percents, thresh_file)

            std_file = '%s/%s_cropped_thresholded_standardized.nii.gz' % (pred_dir, os.path.basename(seq).split('.')[0])
            normalize_sample_wise_img(thresh_file, std_file)

            res_file = '%s/%s_resampled.nii.gz' % (pred_dir, os.path.basename(seq).split('.')[0])
            resample(std_file, pred_shape[0], pred_shape[1], pred_shape[2], res_file, interp=1)

            if not os.path.exists(res_file):
                print("\n pre-processing %s" % training_mods[s])
                c3.run()
            res_data = nib.load(res_file)
            test_data[0, s, :, :, :] = res_data.get_data()

        print(colored("\n predicting hfb segmentation using MC Dropout with %s samples" % num_mc, 'green'))

        res_t1_file = '%s/%s_resampled.nii.gz' % (pred_dir, os.path.basename(t1).split('.')[0])
        res = nib.load(res_t1_file)

        pred_s = np.zeros((num_mc, pred_shape[0], pred_shape[1], pred_shape[2]), dtype=res.get_data_dtype())

        for sample_id in range(num_mc):
            print("MC sample # %s" % sample_id)
            pred = run_test_case(test_data=test_data, model_json=model_json, model_weights=model_weights,
                                 affine=res.affine, output_label_map=True, labels=1)
            pred_s[sample_id, :, :, :] = pred.get_data()
            #nib.save(pred, os.path.join(pred_dir_mcdp, "hfb_pred_%s.nii.gz" % sample_id))

        # computing mean
        pred_mean = pred_s.mean(axis=0)
        pred = nib.Nifti1Image(pred_mean, res.affine)

        pred_prob = os.path.join(pred_dir, "hfb_prob.nii.gz")
        nib.save(pred, pred_prob)

        pred_th_name = os.path.join(pred_dir, "hfb_pred.nii.gz")
        pred_th = math_img('img > %s' % thresh, img=pred)
        nib.save(pred_th, pred_th_name)

        # resample back
        pred_res = resample_to_img(pred_prob, t1_img, interpolation="linear")
        pred_prob_name = os.path.join(pred_dir, "%s_%s_pred_prob.nii.gz" % (subj, model_name))
        nib.save(pred_res, pred_prob_name)

        # sm
        pred_sm = smooth_img(pred_res, fwhm=3)
        pred_res_th = math_img('img > %s' % thresh, img=pred_sm)
        # conn comp
        pred_comp = largest_connected_component_img(pred_res_th)
        pred_name = os.path.join(pred_dir, "%s_%s_pred.nii.gz" % (subj, model_name))
        nib.save(pred_comp, pred_name)

        # copy original orientation to final prediction
        print(cp_orient)
        if ign_ort is False and cp_orient:
            nib.save(pred_comp, prediction_std_orient)
            fill_holes(prediction_std_orient, prediction_std_orient)

            copy_orient(pred_name, in_ort, prediction)
            fill_holes(prediction, prediction)

        else:
            nib.save(pred_comp, prediction)
            fill_holes(prediction, prediction)

        # mask
        t1_masked_name = '%s/%s_T1_nu_masked.nii.gz' % (subj_dir, subj) \
            if bias is True else '%s/%s_masked.nii.gz' % (subj_dir, os.path.basename(t1).split('.')[0])
        masked_t1 = math_img("img1 * img2", img1=nib.load(in_ort), img2=nib.load(prediction))
        nib.save(masked_t1, t1_masked_name)

        if ign_ort is False and cp_orient:
            t1_masked_name_std = '%s/%s_T1_nu_masked_std_orient.nii.gz' % (subj_dir, subj) \
                if bias is True else '%s/%s_masked_std_orient.nii.gz' % (subj_dir, os.path.basename(t1).split('.')[0])
            masked_t1_std = math_img("img1 * img2", img1=t1_img, img2=nib.load(prediction_std_orient))
            nib.save(masked_t1_std, t1_masked_name_std)

        # predict cerebellum
        if woc == 1:
            print("\n predicting approximate cerebellar mask")

            cereb_prediction = '%s/%s_T1acq_nu_cerebellum_pred.nii.gz' % (subj_dir, subj) \
                if bias is True else '%s/%s_T1acq_cerebellum_pred.nii.gz' % (subj_dir, subj)
            model_json_woc = '%s/models/%s_model.json' % (hyper_dir, model_name_woc)
            cereb_weights = '%s/models/cereb_model_weights.h5' % hyper_dir

            cereb_pred = run_test_case(test_data=test_data, model_json=model_json_woc, model_weights=cereb_weights,
                                       affine=res.affine, output_label_map=True, labels=1)

            # resample back
            cereb_pred_res = resample_to_img(cereb_pred, t1_img)
            cereb_pred_name = os.path.join("%s/%s_hfb_cereb_pred_prob.nii.gz" % (pred_dir, subj))
            nib.save(cereb_pred_res, cereb_pred_name)
            cereb_sm = smooth_img(cereb_pred_res, fwhm=2)
            cereb_th = math_img('img > 0.25', img=cereb_sm)
            nib.save(cereb_th, cereb_prediction)

            # remove cerebellum
            woc_img = pred_comp.get_data() - cereb_th.get_data()
            woc_nii = nib.Nifti1Image(woc_img, t1_img.affine)
            # conn comp
            woc_th = math_img('img > 0', img=woc_nii)
            woc_comp = largest_connected_component_img(woc_th)
            woc_name = os.path.join(pred_dir, "%s_%s_woc_pred.nii.gz" % (subj, model_name))
            nib.save(woc_comp, woc_name)

            woc_pred = '%s/%s_T1acq_nu_HfB_woc_pred.nii.gz' % (subj_dir, subj) \
                if bias is True else '%s/%s_T1acq_HfB_woc_pred.nii.gz' % (subj_dir, subj)
            woc_pred_std_orient = '%s/%s_T1acq_nu_HfB_woc_pred_std_orient.nii.gz' % (subj_dir, subj)


            if ign_ort is False and cp_orient:
                nib.save(woc_comp, woc_pred_std_orient)
                fill_holes(woc_pred_std_orient, woc_pred_std_orient)

                copy_orient(woc_name, in_ort, woc_pred)
                fill_holes(woc_pred, woc_pred)

            else:
                nib.save(woc_comp, woc_pred)
                fill_holes(woc_pred, woc_pred)

            # mask
            t1_woc_name = '%s/%s_T1_nu_masked_woc.nii.gz' % (subj_dir, subj) \
                if bias is True else '%s/%s_masked_woc.nii.gz' % (subj_dir, os.path.basename(t1).split('.')[0])
            woc_t1 = math_img("img1 * img2", img1=nib.load(in_ort), img2=nib.load(woc_pred))
            nib.save(woc_t1, t1_woc_name)

            if ign_ort is False and cp_orient:
                t1_woc_name = '%s/%s_T1_nu_masked_woc_std_orient.nii.gz' % (subj_dir, subj) \
                    if bias is True else '%s/%s_masked_woc_std_orient.nii.gz' % (subj_dir, os.path.basename(t1).split('.')[0])
                woc_t1 = math_img("img1 * img2", img1=t1_img, img2=nib.load(woc_pred_std_orient))
                nib.save(woc_t1, t1_woc_name)

        print("\n generating mosaic image for qc")

        seg_qc.main(["-i", "%s" % t1, "-s", "%s" % prediction, "-g", "5", "-m", "75"])

        endstatement.main('Brain extraction and mosaic generation', '%s' % (datetime.now() - start_time))


if __name__ == "__main__":
    main(sys.argv[1:])
