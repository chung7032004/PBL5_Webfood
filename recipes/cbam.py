from tensorflow.keras.layers import Layer, Dense, Conv2D, GlobalAveragePooling2D, GlobalMaxPooling2D, Reshape, Activation, Add, Multiply, Concatenate
from tensorflow.keras import backend as K


# Convolutional Block Attention Module (CBAM) DenseNet121
# class CBAM(Layer):
#     def __init__(self, filters, reduction_ratio=16, **kwargs):
#         super(CBAM, self).__init__(**kwargs)
#         self.filters = filters
#         self.reduction_ratio = reduction_ratio

#     def build(self, input_shape):
#         self.shared_dense_one = Dense(self.filters // self.reduction_ratio, activation='relu', use_bias=True)
#         self.shared_dense_two = Dense(self.filters, use_bias=True)
#         self.conv_spatial = Conv2D(1, kernel_size=7, strides=1, padding='same', activation='sigmoid', use_bias=False)

#     def call(self, input_tensor):
#         avg_pool = GlobalAveragePooling2D()(input_tensor)
#         max_pool = GlobalMaxPooling2D()(input_tensor)

#         avg_pool = Reshape((1, 1, self.filters))(avg_pool)
#         max_pool = Reshape((1, 1, self.filters))(max_pool)

#         mlp_avg = self.shared_dense_two(self.shared_dense_one(avg_pool))
#         mlp_max = self.shared_dense_two(self.shared_dense_one(max_pool))

#         channel_attention = Activation('sigmoid')(Add()([mlp_avg, mlp_max]))
#         channel_refined = Multiply()([input_tensor, channel_attention])

#         avg_pool_spatial = K.mean(channel_refined, axis=-1, keepdims=True)
#         max_pool_spatial = K.max(channel_refined, axis=-1, keepdims=True)

#         concat = Concatenate(axis=-1)([avg_pool_spatial, max_pool_spatial])
#         spatial_attention = self.conv_spatial(concat)
#         refined_feature = Multiply()([channel_refined, spatial_attention])
#         return refined_feature

# --- CBAM Module ---
class CBAM(Layer):
    def __init__(self, filters, reduction_ratio=16,  **kwargs):
        super(CBAM, self).__init__()
        self.filters = filters
        self.reduction_ratio = reduction_ratio

    def build(self, input_shape):
        self.shared_dense_one = Dense(self.filters // self.reduction_ratio, activation='relu', use_bias=True)
        self.shared_dense_two = Dense(self.filters, use_bias=True)
        self.conv_spatial = Conv2D(1, kernel_size=7, strides=1, padding='same', activation='sigmoid', use_bias=False)

    def call(self, input_tensor):
        # Tính trung bình và max theo kênh → vector dạng (batch, C)
        avg_pool = GlobalAveragePooling2D()(input_tensor)
        max_pool = GlobalMaxPooling2D()(input_tensor)

        # Đưa về dạng (batch, 1, 1, C) để phù hợp với Dense layers
        avg_pool = Reshape((1,1,self.filters))(avg_pool)
        max_pool = Reshape((1,1,self.filters))(max_pool)

        # Qua shared MLP: giảm → tăng chiều
        mlp_avg = self.shared_dense_two(self.shared_dense_one(avg_pool))
        mlp_max = self.shared_dense_two(self.shared_dense_one(max_pool))

        # Cộng lại và qua sigmoid → attention vector theo từng channel
        channel_attention = Activation('sigmoid')(Add()([mlp_avg, mlp_max]))
        # Nhân attention với đầu vào → tăng cường kênh quan trọng
        channel_refined = Multiply()([input_tensor, channel_attention])

        # Tính trung bình và max theo chiều kênh → còn lại mỗi pixel 1 giá trị
        avg_pool_spatial = K.mean(channel_refined, axis=-1, keepdims=True)
        max_pool_spatial = K.max(channel_refined, axis=-1, keepdims=True)

        concat = Concatenate(axis=-1)([avg_pool_spatial, max_pool_spatial]) # Ghép 2 ảnh trung bình và max lại theo kênh → shape (H, W, 2)
        spatial_attention = self.conv_spatial(concat)# Áp dụng conv 7x7 + sigmoid → spatial attention map (H, W, 1)
        refined_feature = Multiply()([channel_refined, spatial_attention])# Nhân attention map với feature map đầu vào → tăng cường vùng quan trọng
        return refined_feature

