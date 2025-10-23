# user/serializers.py
from django.db import transaction
from rest_framework import serializers
from advertisement.models import Advertisement, Carousel
from rest_framework.pagination import PageNumberPagination

from middleware.base_views import BaseViewSet
from middleware.utils import ApiResponse


def validate_type(value):
    """验证 type 字段"""
    if not value or value.strip() == '':
        raise serializers.ValidationError("广告类型(type)字段不能为空")
    return value.strip()


class CarouselSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carousel
        fields = '__all__'
        read_only_fields = ['id', 'create_time', 'update_time']

class AdvertisementSerializer(serializers.ModelSerializer):
    type = serializers.CharField(required=True, allow_blank=False, max_length=255)
    game_tags = serializers.SerializerMethodField()
    is_purchase = serializers.SerializerMethodField()
    banner_game_url = serializers.SerializerMethodField()

    def get_banner_game_url(self, obj):
        """
        从关联的轮播图中提取 image_url，拼接为逗号分隔的字符串返回
        与前端提交的格式保持一致
        """
        try:
            # 获取广告关联的所有轮播图，按 sort_order 排序（保证顺序与创建时一致）
            banners = obj.banners.all().order_by('sort_order')
            # 提取所有 image_url，过滤空值
            image_urls = [banner.image_url for banner in banners if banner.image_url]
            # 拼接为逗号分隔的字符串（无轮播图时返回空字符串）
            return ','.join(image_urls)
        except Exception:
            return ''

    def get_is_purchase(self, obj):
        """
        获取当前用户是否购买了该广告
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        try:
            from user.models import UserPurchase
            return UserPurchase.objects.filter(
                user_id=request.user.id,
                content_type='advertise',
                object_id=obj.id
            ).exists()
        except Exception:
            return False

    def get_game_tags(self, obj):
        """获取广告关联的标签名称列表"""
        try:
            return [
                {
                    'id': tag.id,
                    'name': tag.name,
                    'description': tag.description
                }
                for tag in obj.game_tags.all()
            ]
        except Exception:
            return []

    def to_internal_value(self, data):
        """
        重写该方法，手动提取前端传入的 banner_game_url 并添加到验证数据中
        解决 SerializerMethodField 无法接收输入的问题
        """
        # 调用父类方法获取基础验证数据
        internal_data = super().to_internal_value(data)
        # 手动提取前端传入的 banner_game_url（即使字段是 SerializerMethodField）
        # data 是前端原始输入数据（dict类型）
        game_tags = data.get('game_tags', '')
        banner_game_url = data.get('banner_game_url', '').strip()
        # 将提取的值添加到验证数据中，供 create/update 方法使用
        internal_data['game_tags'] = game_tags
        internal_data['banner_game_url'] = banner_game_url
        return internal_data

    @transaction.atomic  # 事务保护：广告和轮播图创建失败时回滚
    def create(self, validated_data):

        banner_urls_str = validated_data.pop('banner_game_url', '').strip()
        game_tags = validated_data.pop('game_tags', None)  # 提取游戏标签
        advertisement = Advertisement.objects.create(**validated_data)
        if game_tags is not None and isinstance(game_tags, list):
            from tags.models import Tag
            # 过滤有效标签ID（确保是整数且存在于数据库）
            tag_ids = [id for id in game_tags if isinstance(id, int)]
            valid_tags = Tag.objects.filter(id__in=tag_ids)
            advertisement.game_tags.set(valid_tags)
        if banner_urls_str:
            banner_urls = [url.strip() for url in banner_urls_str.split(',') if url.strip()]
            carousel_list = []
            for index, url in enumerate(banner_urls):
                # 自动生成轮播图名称（格式：广告名_轮播图_序号），sort_order 按 URL 顺序设置
                carousel = Carousel(
                    advertisement=advertisement,  # 自动关联当前广告
                    image_url=url,
                    name=f"{advertisement.name or '未命名广告'}_banner_{index + 1}",
                    sort_order=index,  # 保证轮播图顺序与 URL 顺序一致
                    type="advertise_banner"  # 可自定义轮播图类型，便于筛选
                )
                carousel_list.append(carousel)
            Carousel.objects.bulk_create(carousel_list)
        return advertisement

    @transaction.atomic
    def update(self, instance, validated_data):
        # 提取并删除 banner_game_url（同create逻辑）
        banner_urls_str = validated_data.pop('banner_game_url', '').strip()
        game_tags = validated_data.pop('game_tags', '')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 处理游戏标签关联
        if game_tags is not None:  # 明确传入了标签参数（包括空数组）
            from tags.models import Tag
            # 过滤有效标签ID（确保是整数且存在于数据库）
            # 先校验是否为列表且元素为整数
            if isinstance(game_tags, list):
                # 提取列表中的有效整数ID
                tag_ids = [id for id in game_tags if isinstance(id, int)]
                # 关联有效标签（空列表会清空关联）
                valid_tags = Tag.objects.filter(id__in=tag_ids)
                instance.game_tags.set(valid_tags)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        # 处理轮播图更新：先删除原有轮播图，再创建新的
        if banner_urls_str:
            # 删除当前广告关联的所有轮播图
            instance.banners.all().delete()
            # 批量创建新轮播图（同create逻辑）
            banner_urls = [url.strip() for url in banner_urls_str.split(',') if url.strip()]
            carousel_list = []
            for index, url in enumerate(banner_urls):
                carousel = Carousel(
                    advertisement=instance,
                    image_url=url,
                    name=f"{instance.name or '未命名广告'}_banner_{index + 1}",
                    sort_order=index,
                    type="advertise_banner"
                )
                carousel_list.append(carousel)
            Carousel.objects.bulk_create(carousel_list)
        elif banner_urls_str == '':
            # 若明确传空字符串，删除所有轮播图
            instance.banners.all().delete()
        return instance

    class Meta:
        model = Advertisement
        fields = [
            'id', 'name', 'title', 'description', 'type',
            'image_url', 'click_url', 'alt_text', 'target_type','is_purchase',
            'is_active', 'sort_order', 'is_vip','price','create_time', 'update_time','game_tags','banner_game_url'
        ]
        read_only_fields = ['id', 'create_time', 'update_time']  # 只读字段


