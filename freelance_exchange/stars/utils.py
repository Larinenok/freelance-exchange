from users.models import CustomUser


def update_user_rating(user: CustomUser):
    stars = user.received_ratings.all()
    if stars.exists():
        avg = round(sum([s.count for s in stars]) / stars.count(), 2)
        user.stars = avg
    else:
        user.stars = None
    user.save()