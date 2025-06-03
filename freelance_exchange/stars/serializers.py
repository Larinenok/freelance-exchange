from rest_framework import serializers

from .models import Star
from .utils import update_user_rating
from users.models import CustomUser

from ads.models import Ad


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'photo', 'slug')


class InputStarsSerializer(serializers.Serializer):
    target_username = serializers.CharField(max_length=150)


class AdShortInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ('id', 'title', 'orderNumber', 'status')


class ListStarInfo(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    target = CustomUserSerializer(read_only=True)
    ad = AdShortInfoSerializer(read_only=True)

    class Meta:
        model = Star
        fields = ('id', 'author', 'target', 'count', 'message', 'created_at', 'ad')


class ChangeStarSerializer(serializers.ModelSerializer):
    target_username = serializers.CharField(write_only=True)
    ad_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Star
        fields = ('count', 'message', 'target_username', 'ad_id')

    def validate(self, data):
        request = self.context.get('request')
        target_username = data.get('target_username')
        ad_id = data.get('ad_id')

        try:
            target = CustomUser.objects.get(username=target_username)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('Пользователь не найден.')

        try:
            ad = Ad.objects.get(id=ad_id)
        except Ad.DoesNotExist:
            raise serializers.ValidationError('Объявление не найдено.')

        if request.user == target:
            raise serializers.ValidationError('Нельзя оставить отзыв самому себе.')

        if ad.author != request.user:
            raise serializers.ValidationError('Вы не являетесь автором этого задания.')

        if ad.executor != target:
            raise serializers.ValidationError('Пользователь не является исполнителем этого задания.')

        if Star.objects.filter(author=request.user, target=target, ad=ad).exists():
            raise serializers.ValidationError('Вы уже оставили отзыв по этой задаче.')

        data['target'] = target
        data['ad'] = ad
        return data

    def create(self, validated_data):
        request = self.context['request']
        author = request.user
        target = validated_data.pop('target')
        ad = validated_data.pop('ad')

        star = Star.objects.create(
            author=author,
            target=target,
            ad=ad,
            count=validated_data['count'],
            message=validated_data.get('message', '')
        )
        update_user_rating(target)
        return star


class UserStatsSerializer(serializers.ModelSerializer):
    average_rating = serializers.FloatField()
    completed_ads_count = serializers.IntegerField()

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'slug', 'photo',
                  'average_rating', 'completed_ads_count')


class CompleteAdStarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Star
        fields = ('count', 'message')

    def validate(self, data):
        request = self.context.get('request')
        ad = self.context.get('ad')
        target = self.context.get('target')

        if not ad or not target:
            raise serializers.ValidationError('Отсутствует контекст выполнения.')

        if request.user == target:
            raise serializers.ValidationError('Нельзя оставить отзыв самому себе.')

        if ad.author != request.user:
            raise serializers.ValidationError('Вы не являетесь автором этого задания.')

        if ad.executor != target:
            raise serializers.ValidationError('Пользователь не является исполнителем этого задания.')

        if Star.objects.filter(author=request.user, target=target, ad=ad).exists():
            raise serializers.ValidationError('Вы уже оставили отзыв по этой задаче.')

        return data

    def create(self, validated_data):
        request = self.context['request']
        author = request.user
        ad = self.context['ad']
        target = self.context['target']

        star = Star.objects.create(
            author=author,
            target=target,
            ad=ad,
            count=validated_data['count'],
            message=validated_data.get('message', '')
        )
        update_user_rating(target)
        return star

