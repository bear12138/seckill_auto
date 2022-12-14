import os
import sys
import time
from io import BytesIO

import onnxruntime
import torch
import torchvision

import numpy as np

import cv2

# εΎεε€η
from PIL import Image


def padded_resize(im, new_shape=(640, 640), stride=32):
    try:
        shape = im.shape[:2]

        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]
        # dw, dh = np.mod(dw, stride), np.mod(dh, stride)
        dw /= 2
        dh /= 2
        if shape[::-1] != new_unpad:  # resize
            im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114))  # add border
        # Convert
        im = im.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
        im = np.ascontiguousarray(im)
        im = torch.from_numpy(im)
        im = im.float()
        im /= 255
        im = im[None]
        im = im.cpu().numpy()  # torch to numpy
        return im
    except:
        print("123")


def xywh2xyxy(x):
    # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
    y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
    y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
    y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
    y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
    y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y
    return y


def box_iou(box1, box2):
    """
    Return intersection-over-union (Jaccard index) of boxes.
    Both sets of boxes are expected to be in (x1, y1, x2, y2) format.
    Arguments:
        box1 (Tensor[N, 4])
        box2 (Tensor[M, 4])
    Returns:
        iou (Tensor[N, M]): the NxM matrix containing the pairwise
            IoU values for every element in boxes1 and boxes2
    """

    def box_area(box):
        # box = 4xn
        return (box[2] - box[0]) * (box[3] - box[1])

    area1 = box_area(box1.T)
    area2 = box_area(box2.T)

    # inter(N,M) = (rb(N,M,2) - lt(N,M,2)).clamp(0).prod(2)
    inter = (torch.min(box1[:, None, 2:], box2[:, 2:]) - torch.max(box1[:, None, :2], box2[:, :2])).clamp(0).prod(2)
    return inter / (area1[:, None] + area2 - inter)  # iou = inter / (area1 + area2 - inter)


def non_max_suppression(prediction, conf_thres=0.25, iou_thres=0.45, classes=None, agnostic=False, multi_label=False,
                        labels=(), max_det=300):
    """Runs Non-Maximum Suppression (NMS) on inference results

    Returns:
         list of detections, on (n,6) tensor per image [xyxy, conf, cls]
    """

    nc = prediction.shape[2] - 5  # number of classes
    xc = prediction[..., 4] > conf_thres  # candidates

    # Checks
    assert 0 <= conf_thres <= 1, f'Invalid Confidence threshold {conf_thres}, valid values are between 0.0 and 1.0'
    assert 0 <= iou_thres <= 1, f'Invalid IoU {iou_thres}, valid values are between 0.0 and 1.0'

    # Settings
    min_wh, max_wh = 2, 7680  # (pixels) minimum and maximum box width and height
    max_nms = 30000  # maximum number of boxes into torchvision.ops.nms()
    time_limit = 10.0  # seconds to quit after
    redundant = True  # require redundant detections
    multi_label &= nc > 1  # multiple labels per box (adds 0.5ms/img)
    merge = False  # use merge-NMS

    t = time.time()
    output = [torch.zeros((0, 6), device=prediction.device)] * prediction.shape[0]
    for xi, x in enumerate(prediction):  # image index, image inference
        # Apply constraints
        x[((x[..., 2:4] < min_wh) | (x[..., 2:4] > max_wh)).any(1), 4] = 0  # width-height
        x = x[xc[xi]]  # confidence

        # Cat apriori labels if autolabelling
        if labels and len(labels[xi]):
            lb = labels[xi]
            v = torch.zeros((len(lb), nc + 5), device=x.device)
            v[:, :4] = lb[:, 1:5]  # box
            v[:, 4] = 1.0  # conf
            v[range(len(lb)), lb[:, 0].long() + 5] = 1.0  # cls
            x = torch.cat((x, v), 0)

        # If none remain process next image
        if not x.shape[0]:
            continue

        # Compute conf
        x[:, 5:] *= x[:, 4:5]  # conf = obj_conf * cls_conf

        # Box (center x, center y, width, height) to (x1, y1, x2, y2)
        box = xywh2xyxy(x[:, :4])

        # Detections matrix nx6 (xyxy, conf, cls)
        if multi_label:
            i, j = (x[:, 5:] > conf_thres).nonzero(as_tuple=False).T
            x = torch.cat((box[i], x[i, j + 5, None], j[:, None].float()), 1)
        else:  # best class only
            conf, j = x[:, 5:].max(1, keepdim=True)
            x = torch.cat((box, conf, j.float()), 1)[conf.view(-1) > conf_thres]

        # Filter by class
        if classes is not None:
            x = x[(x[:, 5:6] == torch.tensor(classes, device=x.device)).any(1)]

        # Apply finite constraint
        # if not torch.isfinite(x).all():
        #     x = x[torch.isfinite(x).all(1)]

        # Check shape
        n = x.shape[0]  # number of boxes
        if not n:  # no boxes
            continue
        elif n > max_nms:  # excess boxes
            x = x[x[:, 4].argsort(descending=True)[:max_nms]]  # sort by confidence

        # Batched NMS
        c = x[:, 5:6] * (0 if agnostic else max_wh)  # classes
        boxes, scores = x[:, :4] + c, x[:, 4]  # boxes (offset by class), scores
        i = torchvision.ops.nms(boxes, scores, iou_thres)  # NMS
        if i.shape[0] > max_det:  # limit detections
            i = i[:max_det]
        if merge and (1 < n < 3E3):  # Merge NMS (boxes merged using weighted mean)
            # update boxes as boxes(i,4) = weights(i,n) * boxes(n,4)
            iou = box_iou(boxes[i], boxes) > iou_thres  # iou matrix
            weights = iou * scores[None]  # box weights
            x[i, :4] = torch.mm(weights, x[:, :4]).float() / weights.sum(1, keepdim=True)  # merged boxes
            if redundant:
                i = i[iou.sum(1) > 1]  # require redundancy

        output[xi] = x[i]
        if (time.time() - t) > time_limit:
            break  # time limit exceeded

    return output


def xyxy2xywh(x):
    # Convert nx4 boxes from [x1, y1, x2, y2] to [x, y, w, h] where xy1=top-left, xy2=bottom-right
    y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
    y[:, 0] = (x[:, 0] + x[:, 2]) / 2  # x center
    y[:, 1] = (x[:, 1] + x[:, 3]) / 2  # y center
    y[:, 2] = x[:, 2] - x[:, 0]  # width
    y[:, 3] = x[:, 3] - x[:, 1]  # height
    return y


def is_ascii(s=''):
    # Is string composed of all ASCII (no UTF) characters? (note str().isascii() introduced in python 3.7)
    s = str(s)  # convert list, tuple, None, etc. to str
    return len(s.encode().decode('ascii', 'ignore')) == len(s)


def box_label(self, box, label='', color=(128, 128, 128), txt_color=(255, 255, 255)):
    # Add one xyxy box to image with label
    if self.pil or not is_ascii(label):
        self.draw.rectangle(box, width=self.lw, outline=color)  # box
        if label:
            w, h = self.font.getsize(label)  # text width, height
            outside = box[1] - h >= 0  # label fits outside box
            self.draw.rectangle((box[0],
                                 box[1] - h if outside else box[1],
                                 box[0] + w + 1,
                                 box[1] + 1 if outside else box[1] + h + 1), fill=color)
            # self.draw.text((box[0], box[1]), label, fill=txt_color, font=self.font, anchor='ls')  # for PIL>8.0
            self.draw.text((box[0], box[1] - h if outside else box[1]), label, fill=txt_color, font=self.font)
    else:  # cv2
        p1, p2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
        cv2.rectangle(self.im, p1, p2, color, thickness=self.lw, lineType=cv2.LINE_AA)
        if label:
            tf = max(self.lw - 1, 1)  # font thickness
            w, h = cv2.getTextSize(label, 0, fontScale=self.lw / 3, thickness=tf)[0]  # text width, height
            outside = p1[1] - h - 3 >= 0  # label fits outside box
            p2 = p1[0] + w, p1[1] - h - 3 if outside else p1[1] + h + 3
            cv2.rectangle(self.im, p1, p2, color, -1, cv2.LINE_AA)  # filled
            cv2.putText(self.im, label, (p1[0], p1[1] - 2 if outside else p1[1] + h + 2), 0, self.lw / 3, txt_color,
                        thickness=tf, lineType=cv2.LINE_AA)


def return_coordinates(xyxy, conf):
    conf = float(conf.numpy())
    gain = 1.02
    pad = 10
    xyxy = torch.tensor(xyxy).view(-1, 4)
    b = xyxy2xywh(xyxy)  # boxes
    b[:, 2:] = b[:, 2:] * gain + pad  # box wh * gain + pad
    xyxy = xywh2xyxy(b).long()
    c1, c2 = (int(xyxy[0, 0]) + 6, int(xyxy[0, 1]) + 6), (int(xyxy[0, 2]) - 6, int(xyxy[0, 3]) - 6)
    # print(f"leftTop:{c1},rightBottom:{c2},Confidence:{conf*100}%")
    result_dict = {"leftTop": c1, "rightBottom": c2, "Confidence": conf}
    return result_dict


def clip_coords(boxes, shape):
    # Clip bounding xyxy bounding boxes to image shape (height, width)
    if isinstance(boxes, torch.Tensor):  # faster individually
        boxes[:, 0].clamp_(0, shape[1])  # x1
        boxes[:, 1].clamp_(0, shape[0])  # y1
        boxes[:, 2].clamp_(0, shape[1])  # x2
        boxes[:, 3].clamp_(0, shape[0])  # y2
    else:  # np.array (faster grouped)
        boxes[:, [0, 2]] = boxes[:, [0, 2]].clip(0, shape[1])  # x1, x2
        boxes[:, [1, 3]] = boxes[:, [1, 3]].clip(0, shape[0])  # y1, y2


def scale_coords(img1_shape, coords, img0_shape, ratio_pad=None):
    # Rescale coords (xyxy) from img1_shape to img0_shape
    if ratio_pad is None:  # calculate from img0_shape
        gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
        pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2  # wh padding
    else:
        gain = ratio_pad[0][0]
        pad = ratio_pad[1]

    coords[:, [0, 2]] -= pad[0]  # x padding
    coords[:, [1, 3]] -= pad[1]  # y padding
    coords[:, :4] /= gain
    clip_coords(coords, img0_shape)
    return coords


def onnx_model_main(path):
    # onnx
    session = onnxruntime.InferenceSession("file/last.onnx", providers=["CPUExecutionProvider"])
    start = time.time()
    image = open(path, "rb").read()
    img = np.array(Image.open(BytesIO(image)))
    # img = cv2.imread(path)
    # εΎεε€η
    img = img[:, :, :3]
    im = padded_resize(img)
    # ζ¨‘εθ°εΊ¦
    pred = session.run([session.get_outputs()[0].name], {session.get_inputs()[0].name: im})[0]
    pred = torch.tensor(pred)
    pred = non_max_suppression(pred, conf_thres=0.60, iou_thres=0.60, max_det=1000)  # ε€§δΊηΎεδΉε­εηη½?δΏ‘εΊ¦
    coordinate_list = []
    for i, det in enumerate(pred):
        det[:, :4] = scale_coords(im.shape[2:], det[:, :4], img.shape).round()
        for *xyxy, conf, cls in reversed(det):
            # θΏεεζ εη½?δΏ‘εΊ¦
            coordinates = return_coordinates(xyxy, conf)
            coordinate_list.append(coordinates)
    # εζ εθ‘¨
    coordinate = sorted(coordinate_list, key=lambda a: a["Confidence"])
    # η¨ζΆ
    duration = str((time.time() - start))
    if len(coordinate) == 0:
        data = {'message': 'error', 'time': duration}
    else:
        coordinate = coordinate[-1]
        x = coordinate.get('leftTop')[0]
        y = coordinate.get('leftTop')[1]
        w = coordinate.get('rightBottom')[0] - coordinate.get('leftTop')[0]
        h = coordinate.get('rightBottom')[1] - coordinate.get('leftTop')[1]
        point = f"{x}|{y}|{w}|{h}"
        data = {'message': 'success', 'time': duration, 'point': point}
        data.update(coordinate)
        # print(x)
        #εε₯ζ»εη§»ε¨ζ°ζ?,εη§»εδΈͺ
        slide=x+10
        slide=str(slide)
        with open('file/slide.txt', 'w') as data_file:
            data_file.write(''.join((slide)))

    return data




#ηζζ ζ³¨εΎη
# def drow_rectangle(coordinate, path):
#     img = cv2.imread(path)
#     # η»ζ‘
#     result = cv2.rectangle(img, coordinate.get("leftTop"), coordinate.get("rightBottom"), (0, 0, 255), 2)
#     cv2.imwrite("drow_rectangle.jpg", result)  # θΏεεδΈ­η©ε½’ηεΎη
#     print("θΏεεζ η©ε½’ζε")

    # def __getRadomPauseScondes(self):
    #     """
    #     :return:ιζΊηζε¨ζεζΆι΄
    #     """
    #     return random.uniform(0.6, 0.9)
    #
    # def simulateDragX(self, source, targetOffsetX):
    #     """
    #     ζ¨‘δ»ΏδΊΊηζζ½ε¨δ½οΌεΏ«ιζ²ΏηXθ½΄ζε¨οΌε­ε¨θ――ε·?οΌοΌεζεοΌηΆεδΏ?ζ­£θ――ε·?
    #     ι²ζ­’θ’«ζ£ζ΅δΈΊζΊε¨δΊΊοΌεΊη°βεΎηθ’«ζͺη©εζδΊβη­ιͺθ―ε€±θ΄₯ηζε΅
    #     :param source:θ¦ζζ½ηhtmlεη΄ 
    #     :param targetOffsetX: ζζ½η?ζ xθ½΄θ·η¦»
    #     :return: None
    #     """
    #     action_chains = webdriver.ActionChains(self.driver)
    #     # ηΉε»οΌεε€ζζ½
    #     action_chains.click_and_hold(source)
    #     # ζε¨ζ¬‘ζ°οΌδΊε°δΈζ¬‘
    #     dragCount = random.randint(2, 3)
    #     if dragCount == 2:
    #         # ζ»θ――ε·?εΌ
    #         sumOffsetx = random.randint(-15, 15)
    #         action_chains.move_by_offset(targetOffsetX + sumOffsetx, 0)
    #         # ζεδΈδΌ
    #         action_chains.pause(self.__getRadomPauseScondes())
    #         # δΏ?ζ­£θ――ε·?οΌι²ζ­’θ’«ζ£ζ΅δΈΊζΊε¨δΊΊοΌεΊη°εΎηθ’«ζͺη©εζδΊη­ιͺθ―ε€±θ΄₯ηζε΅
    #         action_chains.move_by_offset(-sumOffsetx, 0)
    #     elif dragCount == 3:
    #         # ζ»θ――ε·?εΌ
    #         sumOffsetx = random.randint(-15, 15)
    #         action_chains.move_by_offset(targetOffsetX + sumOffsetx, 0)
    #         # ζεδΈδΌ
    #         action_chains.pause(self.__getRadomPauseScondes())
    #
    #         # ε·²δΏ?ζ­£θ――ε·?ηε
    #         fixedOffsetX = 0
    #         # η¬¬δΈζ¬‘δΏ?ζ­£θ――ε·?
    #         if sumOffsetx < 0:
    #             offsetx = random.randint(sumOffsetx, 0)
    #         else:
    #             offsetx = random.randint(0, sumOffsetx)
    #
    #         fixedOffsetX = fixedOffsetX + offsetx
    #         action_chains.move_by_offset(-offsetx, 0)
    #         action_chains.pause(self.__getRadomPauseScondes())
    #
    #         # ζεδΈζ¬‘δΏ?ζ­£θ――ε·?
    #         action_chains.move_by_offset(-sumOffsetx + fixedOffsetX, 0)
    #         action_chains.pause(self.__getRadomPauseScondes())
    #
    #     else:
    #         raise Exception("θ«δΈζ―η³»η»εΊη°δΊι?ι’οΌ!")
    #
    #     # εθaction_chains.drag_and_drop_by_offset()
    #     action_chains.release()
    #     action_chains.perform()


# onnx_model_main("slide.png")

# if __name__ == '__main__':
#     coordinate_onnx = onnx_model_main("slide.png")
    # drow_rectangle(coordinate_onnx, "slide.png")#ζ ζ³¨εΎη


##ε€ζ¬‘ζ¨‘ζζ»ε¨οΌζδΈιθ¦οΌζζ
# def __getRadomPauseScondes():
#     """
#     :return:ιζΊηζε¨ζεζΆι΄
#     """
#     return random.uniform(0.2, 0.4)
#
# def simulateDragX(web, source, targetOffsetX):
#     """
#     ζ¨‘δ»ΏδΊΊηζζ½ε¨δ½οΌεΏ«ιζ²ΏηXθ½΄ζε¨οΌε­ε¨θ――ε·?οΌοΌεζεοΌηΆεδΏ?ζ­£θ――ε·?
#     ι²ζ­’θ’«ζ£ζ΅δΈΊζΊε¨δΊΊοΌεΊη°βεΎηθ’«ζͺη©εζδΊβη­ιͺθ―ε€±θ΄₯ηζε΅
#     :param source:θ¦ζζ½ηhtmlεη΄ 
#     :param targetOffsetX: ζζ½η?ζ xθ½΄θ·η¦»
#     :return: None
#     """
#     action_chains = webdriver.ActionChains(web)
#     # ηΉε»οΌεε€ζζ½
#     action_chains.click_and_hold(source)
#     # ζε¨ζ¬‘ζ°οΌδΊε°δΈζ¬‘
#     dragCount = random.randint(2, 3)
#     if dragCount == 2:
#         # ζ»θ――ε·?εΌ
#         sumOffsetx = random.randint(-15, 15)
#         action_chains.move_by_offset(targetOffsetX + sumOffsetx, 2)
#         # ζεδΈδΌ
#         action_chains.pause(__getRadomPauseScondes())
#         # δΏ?ζ­£θ――ε·?οΌι²ζ­’θ’«ζ£ζ΅δΈΊζΊε¨δΊΊοΌεΊη°εΎηθ’«ζͺη©εζδΊη­ιͺθ―ε€±θ΄₯ηζε΅
#         action_chains.move_by_offset(-sumOffsetx, 0)
#     else :
#         # ζ»θ――ε·?εΌ
#         sumOffsetx = random.randint(-15, 15)
#         action_chains.move_by_offset(targetOffsetX + sumOffsetx, 0)
#         # ζεδΈδΌ
#         action_chains.pause(__getRadomPauseScondes())
#
#         # ε·²δΏ?ζ­£θ――ε·?ηε
#         fixedOffsetX = 0
#         # η¬¬δΈζ¬‘δΏ?ζ­£θ――ε·?
#         if sumOffsetx < 0:
#             offsetx = random.randint(sumOffsetx, 0)
#         else:
#             offsetx = random.randint(0, sumOffsetx)
#
#         fixedOffsetX = fixedOffsetX + offsetx
#         action_chains.move_by_offset(-offsetx, 0)
#         action_chains.pause(__getRadomPauseScondes())
#
#         # ζεδΈζ¬‘δΏ?ζ­£θ――ε·?
#         action_chains.move_by_offset(-sumOffsetx + fixedOffsetX, 5)
#         action_chains.pause(__getRadomPauseScondes())
#
#
#
#     # εθaction_chains.drag_and_drop_by_offset()
#     action_chains.release()
#     action_chains.perform()