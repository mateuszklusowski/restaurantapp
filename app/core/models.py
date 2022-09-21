from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


class UserManager(BaseUserManager):
    """Modify creating a new user or superuser"""

    def create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError('User must have an email address')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):

        super_user = self.create_user(email, password)
        super_user.is_staff = True
        super_user.is_superuser = True
        super_user.save(using=self._db)

        return super_user


class User(AbstractBaseUser, PermissionsMixin):
    """Modify that email is used instead of username"""

    email = models.EmailField(max_length=255, unique=True, blank=False)
    name = models.CharField(max_length=20, unique=True, blank=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Cuisine(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name.capitalize()


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    city = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    post_code = models.CharField(max_length=7)
    phone = models.CharField(max_length=17)
    cuisine = models.ForeignKey(Cuisine, on_delete=models.CASCADE)
    delivery_price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name.capitalize()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name.capitalize()


class Ingredient(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name.capitalize()


class Meal(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.CharField(max_length=255)
    ingredients = models.ManyToManyField(Ingredient)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return self.name.capitalize()


class Drink(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return self.name.capitalize()


class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    meals = models.ManyToManyField(Meal)
    drinks = models.ManyToManyField(Drink)

    def __str__(self):
        return f'{self.restaurant.name} menu'
