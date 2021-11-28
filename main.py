from tkinter.filedialog import askdirectory
import progressbar
import numpy as np
import sys, os
import cv2

print('select directory for input frames')
frames_dir = askdirectory()
outbasename = os.path.basename(frames_dir)

FPS = float(input('enter FPS for video: '))

print('select directory for output video')
outdir = askdirectory()


def defineROI(frame):
    box_s = cv2.selectROIs("Select perspective view ROI", frame, fromCenter=False)
    ((xmin, ymin, width, height),) = tuple(map(tuple, box_s))
    roi = {
        'xmin': xmin,
        'ymin': ymin,
        'width': width,
        'height': height,
    }

    return roi



def getROI(frame, roi):
    xmin = roi['xmin']
    ymin = roi['ymin']
    width = roi['width']
    height = roi['height']

    roi = frame[ymin:ymin + height, xmin:xmin + width]

    return roi


def hconcat_resize_max(im_list, interpolation=cv2.INTER_CUBIC):
    h_max = min([im.shape[0] for im in im_list])
    im_list_resized = [cv2.resize(im, (int(im.shape[1] * h_max / im.shape[0]), h_max), interpolation=interpolation) for
                       im in im_list]
    return cv2.hconcat(im_list_resized)


frames = {}
rois = {}

for view in ['top', 'side']:
    frames[view] = [f for f in sorted(os.listdir(frames_dir), key=lambda f: int(f.split('-')[-1][:-4])) if view in f]
    rois[view] = defineROI(cv2.imread(os.path.join(frames_dir, frames[view][0])))
cv2.destroyAllWindows()

frames_saved = 0
with progressbar.ProgressBar(max_value=len(frames['top'])) as pbar:
    for top, side in zip(frames['top'], frames['side']):

        top_section = getROI(cv2.cvtColor(cv2.imread(os.path.join(frames_dir, top)), cv2.COLOR_BGR2GRAY), rois['top'])
        side_section = getROI(cv2.cvtColor(cv2.imread(os.path.join(frames_dir, side)), cv2.COLOR_BGR2GRAY),
                              rois['side'])
        out_frame = hconcat_resize_max([top_section, side_section])
        # cv2.imshow("out",out_frame)
        # cv2.waitKey(500)

        if frames_saved == 0:
            out_h, out_w = out_frame.shape
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            writer = cv2.VideoWriter(os.path.join(outdir, '{}-merged.avi'.format(outbasename)), fourcc, FPS,
                                     (out_w, out_h), isColor=False)

        writer.write(out_frame)
        frames_saved += 1
        pbar.update(frames_saved)
    writer.release()