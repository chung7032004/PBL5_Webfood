from django.db import models

class Dish(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='dishes/')
    cook_time = models.PositiveIntegerField()
    serving = models.PositiveIntegerField()
    video_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
    # Hàm lấy URL video nhúng từ URL YouTube
    def get_youtube_embed_url(self):
        if self.video_url and 'youtube.com/watch?v=' in self.video_url:
            return self.video_url.replace('watch?v=', 'embed/')
        return None

class Ingredient(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} {self.name}"

class Step(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='steps')
    description = models.TextField()
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"Bước {self.order}: {self.description[:30]}..."

    class Meta:
        ordering = ['order']
