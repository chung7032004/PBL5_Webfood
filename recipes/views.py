from django.shortcuts import render, get_object_or_404
from .models import *
from django.db.models import Q
import os
import uuid
import numpy as np
import unicodedata
import re
from PIL import Image
from django.conf import settings
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.densenet import preprocess_input
from .cbam import CBAM

# Load model (chỉ load một lần)
//model_path = os.path.join(settings.BASE_DIR, 'recipes/models/DenseNet121.h5')
model_path = os.path.join(settings.BASE_DIR, 'recipes/models/DenseNet169.h5')
model = load_model(model_path, custom_objects={'CBAM': CBAM})

# Danh sách lớp khớp thứ tự model
class_names = ['banh_beo', 'banh_bot_loc', 'banh_can', 'banh_canh', 'banh_cuon','banh_mi','banh_tet','banh_xeo','bun_bo_hue','bun_dau_mam_tom','bun_thit_nuong','chao_long','com_tam','goi_cuon','hu_tieu', 'mi_quang', 'nem_chua','pho','suon_xao','xoi_xeo']

# Hàm chuẩn hóa tên: bỏ dấu, viết thường, bỏ khoảng trắng thừa
def normalize_text(text):
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text

# Dự đoán ảnh
def predict_image(image_path):
    img = Image.open(image_path).convert('RGB').resize((224, 224))
    img = np.array(img)
    img = preprocess_input(img)
    img = np.expand_dims(img, axis=0)
    preds = model.predict(img)
    idx = np.argmax(preds)
    return class_names[idx]


# Trang chủ
def home(request):
    query = request.GET.get('q', '')
    if query:
        featured_dishes = Dish.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(ingredients__name__icontains=query)
        ).distinct()
    else:
        featured_dishes = Dish.objects.all()
    return render(request, 'recipes/home.html', {'featured_dishes': featured_dishes})

# Chi tiết món ăn
def dish_detail(request, pk):
    dish = get_object_or_404(Dish, pk=pk)
    return render(request, 'recipes/dish_detail.html', {'dish': dish})

# Dự đoán từ ảnh
def predict_view(request):
    prediction = None
    image_url = None
    dish_obj = None

    if request.method == 'POST' and 'image' in request.FILES:
        image = request.FILES['image']

        # Tạo thư mục media/predict nếu chưa có
        predict_dir = os.path.join(settings.MEDIA_ROOT, 'predict')
        if not os.path.exists(predict_dir):
            os.makedirs(predict_dir)

        # Tạo tên file ngẫu nhiên với đúng đuôi file gốc
        filename = str(uuid.uuid4()) + os.path.splitext(image.name)[1]
        file_path = os.path.join(predict_dir, filename)

        # Lưu file ảnh
        with open(file_path, 'wb+') as f:
            for chunk in image.chunks():
                f.write(chunk)

        # Dự đoán món ăn
        prediction = predict_image(file_path)
        normalized_prediction = prediction.replace('_', ' ').lower()

        # Tìm món ăn trong CSDL bằng cách chuẩn hóa tên trong CSDL
        for dish in Dish.objects.all():
            if normalize_text(dish.name) == normalized_prediction:
                dish_obj = dish
                break

        # Tạo URL để hiển thị ảnh trong template
        image_url = settings.MEDIA_URL + 'predict/' + filename

    return render(request, 'recipes/predict.html', {
        'prediction': prediction,
        'image_url': image_url,
        'dish_obj': dish_obj
    })
