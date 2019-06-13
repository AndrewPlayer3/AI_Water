"""
masked.py contains the architecture for creating a
water mask within SAR imgaes.
"""

from keras import backend
from keras.layers import (
    Activation, BatchNormalization, Conv2D, Input, MaxPooling2D, UpSampling2D,
    concatenate
)
from keras.losses import binary_crossentropy
from keras.models import Model
from keras.optimizers import Adam


def down(filters, input_):
    conv_down = Conv2D(filters, (3, 3), padding='same')(input_)
    conv_down = BatchNormalization(epsilon=1e-4)(conv_down)
    conv_down = Activation('relu')(conv_down)
    conv_down = Conv2D(filters, (3, 3), padding='same')(conv_down)
    conv_down = BatchNormalization(epsilon=1e-4)(conv_down)
    conv_down_res = Activation('relu')(conv_down)
    conv_down_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv_down)
    return conv_down_pool, conv_down_res


def up(filters, input_, down):
    conv_up = UpSampling2D((2, 2))(input_)
    conv_up = concatenate([down, conv_up], axis=3)
    conv_up = Conv2D(filters, (3, 3), padding='same')(conv_up)
    conv_up = BatchNormalization(epsilon=1e-4)(conv_up)
    conv_up = Activation('relu')(conv_up)
    conv_up = Conv2D(filters, (3, 3), padding='same')(conv_up)
    conv_up = BatchNormalization(epsilon=1e-4)(conv_up)
    conv_up = Activation('relu')(conv_up)
    conv_up = Conv2D(filters, (3, 3), padding='same')(conv_up)
    conv_up = BatchNormalization(epsilon=1e-4)(conv_up)
    conv_up = Activation('relu')(conv_up)
    return conv_up


def create_model_masked(model_name: str) -> Model:

    inputs = Input(shape=(512, 512, 1))

    down_0a, down_0a_res = down(24, inputs)
    down_0, down_0_res = down(64, down_0a)
    down_1, down_1_res = down(128, down_0)
    down_2, down_2_res = down(256, down_1)
    down_3, down_3_res = down(512, down_2)
    down_4, down_4_res = down(768, down_3)

    center = Conv2D(768, (3, 3), padding='same')(down_4)
    center = BatchNormalization(epsilon=1e-4)(center)
    center = Activation('relu')(center)
    center = Conv2D(768, (3, 3), padding='same')(center)
    center = BatchNormalization(epsilon=1e-4)(center)
    center = Activation('relu')(center)

    up_4 = up(768, center, down_4_res)
    up_3 = up(512, up_4, down_3_res)
    up_2 = up(256, up_3, down_2_res)
    up_1 = up(128, up_2, down_1_res)
    up_0 = up(64, up_1, down_0_res)
    up_0a = up(24, up_0, down_0a_res)

    classify = Conv2D(1, (1, 1), activation='sigmoid',
                      name='last_layer')(up_0a)

    model = Model(inputs=inputs, outputs=classify)

    model.__asf_model_name = model_name
    print(model.layers[-1].output_shape)

    model.compile(loss=dice_loss, optimizer=Adam(), metrics=['accuracy'])

    return model


def coef(y_true, y_pred, smooth=1):
    y_true_f = backend.flatten(y_true)
    y_pred_f = backend.flatten(y_pred)

    intersection = backend.sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (backend.sum(y_true_f) +
                                           backend.sum(y_pred_f) + smooth)


def dice_coef_loss(y_true, y_pred):
    return 1-coef(y_true, y_pred)


def dice_loss(y_true, y_pred):
    return binary_crossentropy(y_true, y_pred) + dice_coef_loss(y_true, y_pred)
