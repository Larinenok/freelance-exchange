from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Star
from users.models import CustomUser


def update_user_rating(user):
    stars = Star.objects.filter(target=user)
    if stars.exists():
        user.stars = sum(s.count for s in stars) / stars.count()
    else:
        user.stars = None
    user.save()


@receiver(post_save, sender=Star)
def update_rating_on_save(sender, instance, **kwargs):
    update_user_rating(instance.target)


@receiver(post_delete, sender=Star)
def update_rating_on_delete(sender, instance, **kwargs):
    update_user_rating(instance.target)
