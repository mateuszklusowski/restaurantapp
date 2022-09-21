from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(**params):
    return get_user_model().objects.create_user(**params)


def sample_cuisine(cuisine_name):
    return models.Cuisine.objects.create(name=cuisine_name)


def sample_restaurant(**params):
    return models.Restaurant.objects.create(**params)


def sample_tag(tag_name):
    return models.Tag.objects.create(name=tag_name)


def sample_ingredient(ingredient_name):
    return models.Ingredient.objects.create(name=ingredient_name)


def sample_meal(**params):
    return models.Meal.objects.create(**params)


def sample_drink(**params):
    return models.Drink.objects.create(**params)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        params = {
            'email': 'test@test.com',
            'name': 'testusername',
            'password': 'testpassword'
        }

        user = sample_user(**params)

        for key in params.keys():
            if key == 'password':
                self.assertTrue(user.check_password(params[key]))
                continue
            self.assertEqual(params[key], getattr(user, key))

    def test_normalized_email(self):
        params = {
            'email': 'test@TEST.com',
            'name': 'testusername',
            'password': 'testpassword'
        }

        user = sample_user(**params)

        self.assertEqual(user.email, params['email'].lower())

    def test_invalid_email(self):
        with self.assertRaises(ValueError):
            sample_user(email=None, password='testpassword')

    def test_create_superuser(self):
        super_user = get_user_model().objects.create_superuser(
            email='test@admin.com',
            password='testAdminPassword'
        )

        self.assertTrue(super_user.is_staff)
        self.assertTrue(super_user.is_superuser)

    def test_cuisine_model(self):
        name = 'testcuisine'

        cuisine = sample_cuisine(name)

        self.assertEqual(str(cuisine), name.title())

    def test_restaurant_model(self):
        params = {
            'name': 'testname',
            'city': 'Warsaw',
            'address': 'testaddress',
            'post_code': '01-111',
            'phone': 'testphone',
            'cuisine': sample_cuisine('testcuisine'),
            'delivery_price': 7.50
        }

        restaurant = sample_restaurant(**params)

        for key in params.keys():
            self.assertEqual(params[key], getattr(restaurant, key))

    def test_tag_model(self):
        name = 'tagname'

        tag = sample_tag(name)

        self.assertEqual(str(tag), name.title())

    def test_ingerdient_model(self):
        name = 'testingredient'

        ingredient = sample_ingredient(name)

        self.assertEqual(str(ingredient), name.title())

    def test_meal_model(self):
        params = {
            'name': 'testname',
            'price': 20.00,
            'tag': sample_tag('tagname')
        }

        ingredients = [sample_ingredient(f'ingredient{i}') for i in range(3)]

        meal = sample_meal(**params)
        meal.ingredients.set(ingredients)

        for key in params.keys():
            self.assertEqual(params[key], getattr(meal, key))

        for ingredient in ingredients:
            self.assertIn(ingredient, meal.ingredients.all())

    def test_drink_model(self):
        params = {
            'name': 'testname',
            'price': 1.11,
            'tag': sample_tag('tagname')
        }

        drink = sample_drink(**params)

        for key in params.keys():
            self.assertEqual(params[key], getattr(drink, key))

    def test_menu_model(self):
        restaurant_params = {
            'name': 'testname',
            'city': 'Warsaw',
            'address': 'testaddress',
            'post_code': '01-111',
            'phone': 'testphone',
            'cuisine': sample_cuisine('testcuisine'),
            'delivery_price': 7.50
        }

        ingredients = [sample_ingredient(f'ingredient{i}') for i in range(3)]

        meals = []
        for i in range(5):
            meal = sample_meal(
                name=f'testname_{i}',
                price=20.00,
                tag=sample_tag('tagname'))

            meal.ingredients.set(ingredients)
            meals.append(meal)

        drinks = [
            sample_drink(
                name=f'testname{i}',
                price=1.11,
                tag=sample_tag('tagname'))
            for i in range(5)
        ]

        menu = models.Menu.objects.create(
            restaurant=sample_restaurant(**restaurant_params))
        menu.meals.set(meals)
        menu.drinks.set(drinks)

        self.assertEqual(str(menu), f'{menu.restaurant.name} menu')

        for meal in meals:
            self.assertIn(meal, menu.meals.all())

        for drink in drinks:
            self.assertIn(drink, menu.drinks.all())
