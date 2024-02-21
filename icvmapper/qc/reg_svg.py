import os
import glob
import argparse
import argcomplete

import numpy as np
import nibabel as nib
import svgwrite
from nilearn.plotting import plot_roi
from nilearn.image import new_img_like
from PIL import Image

ORIENTATION_DICT = {'L' : 'x',
                    'R' : 'x',
                    'P' : 'y',
                    'A' : 'y',
                    'S' : 'z',
                    'I' : 'z',}

def parsefn():
    parser = argparse.ArgumentParser(usage='%(prog)s -i [ img ] \n\n'
                                           "Create tiled mosaic of segmentation overlaid on structural image")

    required = parser.add_argument_group('required arguments')

    required.add_argument('-f', '--fixed', type=str, metavar='', help="fixed image used in registration", required=True)
    required.add_argument('-r', '--reg', type=str, metavar='', help="registration output", required=True)

    optional = parser.add_argument_group('optional arguments')

    optional.add_argument('-s', '--seg', type=str, metavar='', help="segmentation mask")
    optional.add_argument('-sl', '--slices', type=int, metavar='', help="number of slices",
                          default=5)
    optional.add_argument('-o', '--out', type=str, metavar='', help="output image filename")

    return parser

def parse_inputs(parser, args):
    if isinstance(args, list):
        args = parser.parse_args(args)
    argcomplete.autocomplete(parser)

    fixed = args.fixed
    reg = args.reg
    seg = args.seg if args.seg else None
    slices = args.slices

    out_dir = None
    out_file = None
    if args.out:
        out_dir = os.path.dirname(args.out)
        out_file = args.out
    else:
        out_file = 'reg_comparison.svg'
        out_dir = os.getcwd()
    
    prefix = os.path.splitext(os.path.basename(out_file))[0]

    return fixed, reg, seg, slices, out_dir, out_file, prefix


def get_orient(image):
    return nib.aff2axcodes(image.affine)

def generate_pngs(fixed_file, reg_file, prefix, seg_file=None, output_dir=None, slices=5):
    fixed_img = nib.load(fixed_file)
    reg_img = nib.load(reg_file)
    seg_img = nib.load(seg_file) if seg_file else None

    if get_orient(fixed_img) != get_orient(reg_img):
        raise Exception("Both the registration and the fixed image have different orientations")
    
    if fixed_img.shape != reg_img.shape:
        raise Exception("Both the registration and the fixed image have different voxel dimensions ({}, and {})".format(reg_img.shape, fixed_img.shape))

    # check segmentation image
    if seg_img and get_orient(seg_img) != get_orient(reg_img):
        raise Exception("The segmentation mask's orientation is different than the others")

    # generate blank image
    if seg_file:
        mask_img = seg_file
    else:
        mask_img = new_img_like(fixed_img, np.zeros(fixed_img.shape))

    # create output dir for intermediate images
    preprocdir = os.path.join(output_dir, 'svg_process')
    os.makedirs(preprocdir, exist_ok=True)

    # set slice indices
    slice_pos = [-30, -15, 0, 15, 30]

    # generate 6 images
    for img_type, img in [('fixed', fixed_img), ('reg', reg_img)]:
        for direction in get_orient(fixed_img):
            axis = ORIENTATION_DICT[direction]
            
            #output
            if output_dir is None:
                output_dir = os.getcwd()
            
            output_file = os.path.join(preprocdir, "{}_{}_{}.png".format(prefix, img_type, axis))

            title = img_type.capitalize() if axis == 'x' else None

            plot_roi(mask_img, img, display_mode=axis, cut_coords=(-30, -15, 0, 15, 30), title=title, output_file=output_file)


def combine_png(out_dir, prefix):
    """
    Combine the generate pngs to be used in the animation
    """

    # grab all fixed and reg images
    fixed_images = glob.glob(os.path.join(out_dir, 'svg_process', '{}_fixed_*.png'.format(prefix)))
    fixed_images.sort()
    reg_images = glob.glob(os.path.join(out_dir, 'svg_process', '{}_reg_*.png'.format(prefix)))
    reg_images.sort()

    if not fixed_images or not reg_images:
        raise Exception("Intermediate files are missing. You may be missing either a registration file or the fixed image")

    # extract images
    fixed_pngs = [Image.open(x) for x in fixed_images]
    reg_pngs = [Image.open(x) for x in reg_images]

    width = fixed_pngs[0].width
    height = sum([svg.height for svg in fixed_pngs])

    # create larger fixed and reg images before saving
    fixed_image = Image.new('RGB', (width, height))
    for i, png in enumerate(fixed_pngs):
        fixed_image.paste(png, (0, i * png.height))
    fixed_image.save(os.path.join(out_dir, 'svg_process', '{}_combined_fixed_image.png'.format(prefix)))

    reg_image = Image.new('RGB', (width, height))
    for j, png in enumerate(reg_pngs):
        reg_image.paste(png, (0, j * png.height))
    reg_image.save(os.path.join(out_dir, 'svg_process', '{}_combined_reg_image.png'.format(prefix)))

    # remove intermediate images
    for image in fixed_images:
        os.remove(image)
    for image in reg_images:
        os.remove(image)


def compile_svg(out_dir, out_file, prefix):
    """
    Combine the fixed image and the registration image into an SVG animation.
    """
    fixed_png = glob.glob(os.path.join(out_dir, '**/{}_combined_fixed_image.png'.format(prefix)))
    reg_png = glob.glob(os.path.join(out_dir, '**/{}_combined_reg_image.png'.format(prefix)))

    if not fixed_png or not reg_png:
        raise Exception("Intermediate files are missing. You may be missing either a registration file or the fixed image")

    fixed_png = fixed_png[0]
    reg_png = reg_png[0]

    # get relative paths for swg file
    fixed_relpath = os.path.relpath(fixed_png, out_dir)
    reg_relpath = os.path.relpath(reg_png, out_dir)

    dwg = svgwrite.Drawing(out_file)
    background = dwg.add(svgwrite.image.Image(reg_relpath))
    foreground = dwg.add(svgwrite.image.Image(fixed_relpath))
    
    foreground.add(dwg.animate("opacity", dur="5s", values="0;0;1;1;0", keyTimes="0;0.1;0.5;0.7;1", repeatCount="indefinite"))

    dwg.save()


def main(args):
    parser = parsefn()
    fixed, reg, seg, slices, out_dir, out_file, prefix = parse_inputs(parser, args)

    generate_pngs(fixed, reg, prefix, seg, out_dir, slices)
    combine_png(out_dir, prefix)
    compile_svg(out_dir, out_file, prefix)