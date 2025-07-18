import random
from django.contrib.auth.models import User
from posts.models import Post
from users.models import Profile
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image

def create_demo_users(num_users=10):
    users = []
    for i in range(num_users):
        username = f'demo_user_{i+1}'
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, password='password123')
            user.profile.bio = f'This is the bio for {username}.'
            user.profile.save()
            users.append(user)
        else:
            users.append(User.objects.get(username=username))
    return users

def create_placeholder_image():
    img = Image.new('RGB', (300, 300), color=(random.randint(100,255), random.randint(100,255), random.randint(100,255)))
    buf = BytesIO()
    img.save(buf, format='JPEG')
    return ContentFile(buf.getvalue(), 'demo.jpg')

def create_demo_posts(users, num_posts=50):
    sample_contents = [
        "Just enjoying a sunny day! ☀️",
        "Check out this awesome view!",
        "Feeling grateful for my friends.",
        "Anyone up for a coffee? ☕️",
        "#Django is awesome!",
        "Working on a new project.",
        "Life is beautiful!",
        "Throwback to last summer.",
        "Can't wait for the weekend!",
        "Reading a great book right now.",
    ]
    for i in range(num_posts):
        user = random.choice(users)
        content = random.choice(sample_contents)
        post = Post.objects.create(
            user=user,
            content=content,
        )
        # Add an image to every 3rd post
        if i % 3 == 0:
            post.image.save(f'demo_{i}.jpg', create_placeholder_image(), save=True)
        post.save()

def run():
    users = create_demo_users()
    create_demo_posts(users)
    print("Demo users and posts created!") 