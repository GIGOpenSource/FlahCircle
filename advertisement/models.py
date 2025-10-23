from django.db import models


class Advertisement(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.CharField(max_length=255, blank=True, null=True,verbose_name="封面")
    click_url = models.CharField(max_length=255, blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    target_type = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True, default=False)
    sort_order = models.IntegerField(blank=True, null=True, default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0.00)
    is_vip = models.BooleanField(default=False)
    game_tags = models.ManyToManyField('tags.Tag', related_name='ad', blank=True, verbose_name="兴趣标签")
    class Meta:
        db_table = 't_ad'
        ordering = ['create_time', 'name']

class Carousel(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.CharField(max_length=255, blank=True, null=True)
    sort_order = models.IntegerField(blank=True, null=True, default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    advertisement = models.ForeignKey(
        'Advertisement',  # 关联到广告模型
        related_name='banners',  # 反向查询：广告.advertisements 可获取所有关联的轮播图
        on_delete=models.CASCADE,  # 若广告被删除，关联的轮播图也删除（可按需修改）
        null=True,  # 允许轮播图不关联广告（可选，根据业务决定）
        blank=True,
        verbose_name="所属广告"
    )
    class Meta:
        db_table = 't_carousel'