from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

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


def sample_order(**params):
    return models.Order.objects.create(**params)


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

    def test_order_model(self):
        user_params = {
            'email': 'test@test.com',
            'name': 'test',
            'password': 'testpassword'
        }
        user = sample_user(**user_params)

        restaurant_params = {
            'name': 'testname',
            'city': 'Warsaw',
            'address': 'testaddress',
            'post_code': '01-111',
            'phone': 'testphone',
            'cuisine': sample_cuisine('testcuisine'),
            'delivery_price': 7.50
        }
        restaurant = sample_restaurant(**restaurant_params)

        order_params = {
            'user': user,
            'restaurant': restaurant,
            'delivery_address': 'test address',
            'delivery_city': 'Warsaw',
            'delivery_post_code': '00-000',
            'delivery_phone': '00000000000',
            'order_time': timezone.now()
        }

        order = sample_order(**order_params)

        for key in order_params.keys():
            if key == 'order_time':
                continue
            self.assertEqual(order_params[key], getattr(order, key))

        self.assertEqual(order.order_time.day,
                         order_params['order_time'].day)
        self.assertEqual(order.order_time.hour,
                         order_params['order_time'].hour)
        self.assertEqual(order.order_time.minute,
                         order_params['order_time'].minute)

    def test_ordermeal_model(self):
        user_params = {
            'email': 'test@test.com',
            'name': 'test',
            'password': 'testpassword'
        }
        user = sample_user(**user_params)

        restaurant_params = {
            'name': 'testname',
            'city': 'Warsaw',
            'address': 'testaddress',
            'post_code': '01-111',
            'phone': 'testphone',
            'cuisine': sample_cuisine('testcuisine'),
            'delivery_price': 7.50
        }
        restaurant = sample_restaurant(**restaurant_params)

        order_params = {
            'user': user,
            'restaurant': restaurant,
            'delivery_address': 'test address',
            'delivery_city': 'Warsaw',
            'delivery_post_code': '00-000',
            'delivery_phone': '00000000000',
            'order_time': timezone.now()
        }

        order = sample_order(**order_params)

        meal = sample_meal(name='testmeal', price=1.00, tag=sample_tag('tag'))
        order_meal = models.OrderMeal.objects.create(
            order=order,
            meal=meal,
            quantity=2
        )

        self.assertEqual(order_meal.order, order)
        self.assertEqual(order_meal.meal, meal)
        self.assertEqual(order_meal.quantity, 2)
        self.assertEqual(order_meal.get_total_meal_price, 2)

    def test_orderdrink_model(self):
        user_params = {
            'email': 'test@test.com',
            'name': 'test',
            'password': 'testpassword'
        }
        user = sample_user(**user_params)

        restaurant_params = {
            'name': 'testname',
            'city': 'Warsaw',
            'address': 'testaddress',
            'post_code': '01-111',
            'phone': 'testphone',
            'cuisine': sample_cuisine('testcuisine'),
            'delivery_price': 7.50
        }
        restaurant = sample_restaurant(**restaurant_params)

        order_params = {
            'user': user,
            'restaurant': restaurant,
            'delivery_address': 'test address',
            'delivery_city': 'Warsaw',
            'delivery_post_code': '00-000',
            'delivery_phone': '00000000000',
            'order_time': timezone.now()
        }

        order = sample_order(**order_params)

        drink = sample_drink(
            name='testdrink',
            price=1.00,
            tag=sample_tag('tag'))

        order_drink = models.OrderDrink.objects.create(
            order=order,
            drink=drink,
            quantity=2
        )

        self.assertEqual(order_drink.order, order)
        self.assertEqual(order_drink.drink, drink)
        self.assertEqual(order_drink.quantity, 2)
        self.assertEqual(order_drink.get_total_drink_price, 2)
