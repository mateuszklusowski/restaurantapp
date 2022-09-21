from rest_framework import serializers

from core.models import Restaurant, Menu, Meal, Drink, Ingredient


class DrinkSerializer(serializers.ModelSerializer):
    tag = serializers.StringRelatedField()

    class Meta:
        model = Drink
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class MealSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tag = serializers.StringRelatedField()

    class Meta:
        model = Meal
        fields = "__all__"

    def get_ingredients(self, obj):
        return obj.ingredients.values_list('name', flat=True)


class MenuSerializer(serializers.ModelSerializer):
    drinks = DrinkSerializer(many=True, read_only=True)
    meals = MealSerializer(many=True, read_only=True)

    class Meta:
        model = Menu
        fields = ('meals', 'drinks')


class RestaurantSerializer(serializers.ModelSerializer):
    cuisine = serializers.StringRelatedField()

    class Meta:
        model = Restaurant
        fields = "__all__"


class RestaurantDetailSerializer(RestaurantSerializer):
    menu = serializers.SerializerMethodField()

    class Meta(RestaurantSerializer.Meta):
        fields = '__all__'
        lookup_field = 'slug'

    def get_menu(self, obj):
        menu = Menu.objects.get(restaurant=obj)
        return MenuSerializer(menu, many=False).data
