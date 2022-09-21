from rest_framework.test import APITestCase
from rest_framework import status

from django.urls import reverse

from core.models import Restaurant, Menu, Cuisine

from restaurant.serializers import (RestaurantDetailSerializer,
                                    RestaurantSerializer)

RESTAURANTS_URL = reverse('restaurant:restaurant-list')


def sample_cuisine(cuisine_name):
    return Cuisine.objects.create(name=cuisine_name)


def detail_url(obj_slug):
    return reverse('restaurant:restaurant-detail', args=[obj_slug])


def sample_restaurant(**params):
    return Restaurant.objects.create(**params)


class RestaurantAPITests(APITestCase):

    def test_retrieve_restaurant_list(self):
        params = {
            'name': 'testname',
            'city': 'Warsaw',
            'address': 'testaddress',
            'post_code': '01-111',
            'phone': 'testphone',
            'cuisine': sample_cuisine('testcuisine'),
            'delivery_price': 7.50
        }
        sample_restaurant(**params)
        params['name'] = 'testname2'
        sample_restaurant(**params)

        res = self.client.get(RESTAURANTS_URL)
        restaurants = Restaurant.objects.all().order_by('id')
        serializer = RestaurantSerializer(restaurants, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_restaurant_detail(self):
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
        Menu.objects.create(restaurant=restaurant)

        url = detail_url(restaurant.slug)

        res = self.client.get(url)
        serializer = RestaurantDetailSerializer(restaurant)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_search_with_cuisine(self):
        params = {
            'name': 'testname',
            'city': 'Warsaw',
            'address': 'testaddress',
            'post_code': '01-111',
            'phone': 'testphone',
            'cuisine': sample_cuisine('testcuisine'),
            'delivery_price': 7.50
        }
        rest1 = sample_restaurant(**params)
        params['name'] = 'testname2'
        rest2 = sample_restaurant(**params)
        rest2.cuisine = sample_cuisine('testcuisine2')
        rest2.save()

        res = self.client.get(RESTAURANTS_URL, {'cuisine': 'testcuisine'})

        serial1 = RestaurantSerializer(rest1).data
        serial2 = RestaurantSerializer(rest2).data

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serial1, res.data)
        self.assertNotIn(serial2, res.data)

    def test_search_with_city(self):
        params = {
            'name': 'testname',
            'city': 'Warsaw',
            'address': 'testaddress',
            'post_code': '01-111',
            'phone': 'testphone',
            'cuisine': sample_cuisine('testcuisine'),
            'delivery_price': 7.50
        }
        rest1 = sample_restaurant(**params)
        params['name'] = 'testname2'
        params['city'] = 'Poznan'
        rest2 = sample_restaurant(**params)

        res = self.client.get(RESTAURANTS_URL, {'city': 'warsaw'})

        serial1 = RestaurantSerializer(rest1).data
        serial2 = RestaurantSerializer(rest2).data

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serial1, res.data)
        self.assertNotIn(serial2, res.data)
