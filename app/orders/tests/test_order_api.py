from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase
from rest_framework import status

from orders import serializers as order_serializers
from core import models


ORDERS_URL = reverse('orders:order-list')
ORDER_CREATE_URL = reverse('orders:order-create')


def detail_url(object_id):
    return reverse('orders:order-detail', args=[object_id])


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def sample_restaurant(restaurant_name):
    return models.Restaurant.objects.create(
        name=restaurant_name,
        city='Warsaw',
        address='testaddress',
        post_code='00-000',
        phone='00000000000',
        cuisine=models.Cuisine.objects.create(name='testcuisine'),
        delivery_price=12.00
    )


def sample_ingredient(ingredient_name):
    return models.Ingredient.objects.create(name=ingredient_name)


def sample_tag(tag_name):
    return models.Tag.objects.create(name=tag_name)


def sample_meal(**params):
    """Sample meal for testing"""
    default = {
        'price': 10.00,
        'tag': sample_tag('testtag'),
    }
    default.update(**params)
    meal = models.Meal.objects.create(**default)
    meal.ingredients.set([sample_ingredient('testingredient1'),
                          sample_ingredient('testingredient2')])
    return meal


def sample_drink(**params):
    """Sample drink for testing"""
    default = {'price': 2.50, 'tag': sample_tag('testtag')}
    default.update(**params)
    return models.Drink.objects.create(**default)


def sample_order(**params):
    """Sample order for testing"""
    default = {
        'restaurant': sample_restaurant('testrestaurant'),
        'order_time': timezone.now(),
        'delivery_address': 'testaddress',
        'delivery_city': 'Warsaw',
        'delivery_post_code': '01-100',
        'delivery_phone': 'testphone'
    }
    default.update(**params)

    return models.Order.objects.create(**default)


class PublicOrderAPITests(APITestCase):

    def test_login_required(self):
        res = self.client.get(ORDERS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderAPITests(APITestCase):

    def setUp(self):
        self.user = create_user(
            email='test@test.com',
            password='testpass',
            name='Test name'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_orders(self):
        sample_order(user=self.user)
        sample_order(user=self.user)

        res = self.client.get(ORDERS_URL)

        orders = models.Order.objects.all()
        serializer = order_serializers.OrderSerializer(orders, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_orders_limited_to_user(self):
        user2 = create_user(
            email='other@user.com',
            password='testpass',
            name='Other name'
        )
        sample_order(user=self.user)
        sample_order(user=user2)

        res = self.client.get(ORDERS_URL)

        orders = models.Order.objects.filter(user=self.user)
        serializer = order_serializers.OrderSerializer(orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_detail_order(self):
        order = sample_order(
            user=self.user, restaurant=sample_restaurant('rest2'))
        order2 = sample_order(user=self.user)

        url = detail_url(order.id)
        res = self.client.get(url)

        serializer1 = order_serializers.OrderDetailSerializer(order)
        serializer2 = order_serializers.OrderDetailSerializer(order2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer1.data)
        self.assertNotEqual(res.data, serializer2.data)

    def test_create_order(self):
        restaurant = sample_restaurant('restaurant1')
        meal1 = sample_meal(name="meal1")
        meal2 = sample_meal(name="meal2")
        drink1 = sample_drink(name="drink1")
        drink2 = sample_drink(name="drink2")

        menu = models.Menu.objects.create(restaurant=restaurant)
        menu.meals.set([meal1, meal2])
        menu.drinks.set([drink1, drink2])

        payload = {
            "restaurant": restaurant.id,
            "meals": [
                {"meal": meal1.id, "quantity": 10},
                {"meal": meal2.id, "quantity": 10}
            ],
            "drinks": [
                {"drink": drink1.id, "quantity": 10},
                {"drink": drink2.id, "quantity": 10}
            ],
            "delivery_city": "Warsaw",
            "delivery_address": "some address",
            "delivery_post_code": "01-223",
            "delivery_phone": "some phone"
        }

        res = self.client.post(ORDER_CREATE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        order = models.Order.objects.get(id=res.data['id'])

        bad_assertion_keys = [
            'restaurant', 'meals', 'drinks']

        for key in payload.keys():
            if key in bad_assertion_keys:
                continue
            self.assertEqual(payload[key], getattr(order, key))

        self.assertEqual(payload['restaurant'], order.restaurant.id)
        self.assertEqual(order.total_price, 262.00)

        counted_meals = models.OrderMeal.objects.filter(order=order).count()
        self.assertEqual(2, counted_meals)
        for meal in payload['meals']:
            order_meal = models.OrderMeal.objects.get(
                order=order, meal__id=meal['meal'])
            self.assertEqual(order_meal.meal_id, meal['meal'])

        counted_drinks = models.OrderDrink.objects.filter(order=order).count()
        self.assertEqual(2, counted_drinks)
        for drink in payload['drinks']:
            order_drink = models.OrderDrink.objects.get(
                order=order, drink__id=drink['drink'])
            self.assertEqual(order_drink.drink_id, drink['drink'])

    def test_create_order_with_empty_meal(self):
        payload = {
            "restaurant": sample_restaurant('test').id,
            "meals": [],
            "drinks": [],
            "delivery_city": "some city",
            "delivery_address": "some address",
            "delivery_post_code": "01-223",
            "delivery_phone": "some phone"
        }

        res = self.client.post(ORDER_CREATE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_wrong_meal(self):
        restaurant = sample_restaurant('restaurant1')
        meal1 = sample_meal(name="meal1")
        meal2 = sample_meal(name="meal2")
        drink1 = sample_drink(name="drink1")
        drink2 = sample_drink(name="drink2")

        menu = models.Menu.objects.create(restaurant=restaurant)
        menu.meals.set([meal1])
        menu.drinks.set([drink1, drink2])

        payload = {
            "restaurant": restaurant.id,
            "meals": [
                {"meal": meal1.id, "quantity": 10},
                {"meal": meal2.id, "quantity": 10}
            ],
            "drinks": [
                {"drink": drink1.id, "quantity": 10},
                {"drink": drink2.id, "quantity": 10}
            ],
            "delivery_city": "some city",
            "delivery_address": "some address",
            "delivery_post_code": "01-223",
            "delivery_phone": "some phone"
        }

        res = self.client.post(ORDER_CREATE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
