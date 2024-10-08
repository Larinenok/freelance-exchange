from rest_framework import serializers

from .models import *
from users.models import CustomUser


class ListStarInfo(serializers.ModelSerializer):
    class Meta:
        model = Star
        fields = ['count', 'username', 'author', 'message']

    
class GetStarInfo(serializers.ModelSerializer):
    class Meta:
        model = Star
        fields = ['count', 'username']
    
    def validate(self, data):
        if not CustomUser.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "Такого пользователя не существует"})

        return data


class InputStarsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Star
        fields = ['username']

    def validate(self, data):
        if not CustomUser.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "Такого пользователя не существует"})

        return data


class ChangeStarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Star
        fields = ['count', 'username', 'message']

    def validate(self, data):
        if 0 > data['count'] or data['count'] > 5:
            raise serializers.ValidationError({'count': 'Рейтинг должен быть от 0 до 5'})

        if self.context['request'].user.username == data['username']:
            raise serializers.ValidationError({"username": "Нельзя оставить отзыв самому себе"})

        if not CustomUser.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "Такого пользователя не существует"})

        return data

    def create(self, validated_data):
        star = Star.objects.filter(username=validated_data.get('username'), author=self.context['request'].user)
        validated_data['author'] = self.context['request'].user.username
        if star.exists():
            return super().update(star[0], validated_data)
        return super().create(validated_data)

    def delete(self, validated_data):
        star = Star.objects.filter(username=validated_data.get('username'), author=self.context['request'].user)
        if star.exists():
            star[0].delete()
            return []
        raise serializers.ValidationError({"star": "Такого отзыва не существует"})
