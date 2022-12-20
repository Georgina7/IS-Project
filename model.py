import numpy as np
import pandas as pd
import os
import cv2
import matplotlib.pyplot as plt
import tensorflow as tf
# import pickle
from keras import backend as K
# from dice_coef import *

# Loss Function - Dice Coefficient
def dice_coef(y_true, y_pred, smooth=1e-7):
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = K.sum(y_true_f * y_pred_f)
    dice = (2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth)
    return dice

def dice_coef_multilabel(y_true, y_pred, M=3):
    dice = 0
    dice += dice_coef_large(y_true, y_pred)
    dice += dice_coef_small(y_true, y_pred)
    dice += dice_coef_stomach(y_true, y_pred)
    return dice/M

def dice_coef_loss(y_true, y_pred):
    return 1 - dice_coef_multilabel(y_true, y_pred)

def dice_coef_large(y_true, y_pred):
    coef = dice_coef(y_true[:,:,:,0], y_pred[:,:,:,0])
    return coef

def dice_coef_small(y_true, y_pred):
    coef = dice_coef(y_true[:,:,:,1], y_pred[:,:,:,1])
    return coef

def dice_coef_stomach(y_true, y_pred):
    coef = dice_coef(y_true[:,:,:,2], y_pred[:,:,:,2])
    return coef

def dice_coef_background(y_true, y_pred):
    coef = dice_coef(y_true[:,:,:,3], y_pred[:,:,:,3])
    return coef

def create_mask(pred_mask):
    pred_mask = tf.math.argmax(pred_mask, axis=-1)
    pred_mask = pred_mask[..., tf.newaxis]
    return pred_mask[0].numpy()

def decode_to_rgb(mask):
    shape = 224 * 224
    pred_mask = np.reshape(mask, (shape, 1))
    classes = {0:[255, 0, 0], 1:[0, 255, 0], 2:[0, 0, 255], 3:[0, 0, 0]}
    rgb_mask = np.zeros((shape, 3), dtype=np.uint8)
    for i in range(shape):
        rgb_mask[i] = classes[pred_mask[i][0]]
    rgb_mask = np.reshape(rgb_mask, (224, 224, 3))/255
    return rgb_mask

def display(display_list):
    plt.figure(figsize=(15, 15))

    title = ['Input Image', 'Predicted Mask']

    for i in range(len(display_list)):
        plt.subplot(1, len(display_list), i+1)
        plt.title(title[i])
        if i == 0:
            plt.imshow(np.squeeze(display_list[i], axis=2))
        else:
            plt.imshow(display_list[i])
        plt.axis('off')
        plt.show()

def predict(path):
    # Loading saved model
    model = tf.keras.models.load_model('.\model\cp-0011-0.35.ckpt', custom_objects={'dice_coef_loss':dice_coef_loss, 'dice_coef_large':dice_coef_large, 'dice_coef_small':dice_coef_small, 'dice_coef_stomach':dice_coef_stomach})
    # Read scan from storage using opencv library
    image = cv2.imread(path, cv2.IMREAD_UNCHANGED).astype("float32")
    # Resize image to height and width of 224
    image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_NEAREST)
    # Normalize image
    image = image/255
    image = np.expand_dims(image, axis=2)

    # Pass image to model for prediction
    prediction = model.predict(np.expand_dims(image, axis=0))
    pred_mask = create_mask(prediction)
    # Plot image
    plt.imshow(np.squeeze(image, axis=2), cmap='gray')
    plt.savefig('.\static\images\mri_scan.png')
    plt.clf()
    
    # Plot mask overlay on image
    plt.imshow(np.squeeze(image, axis=2), cmap='gray')
    plt.imshow(decode_to_rgb(pred_mask), cmap='jet', alpha=0.5)
    plt.savefig('.\static\images\prediction.png')
    
    # return prediction
