from rest_framework import serializers

from django.utils.translation import gettext_lazy as _

from decimal import Decimal

from core.models import Order, OrderMeal, OrderDrink, Menu


def calculate(meal=None, drink=None, restaurant=None):
    """counting the number of the same object"""
    if meal:
        data_name = 'meal'
        counted_object = meal
    if drink:
        data_name = 'drink'
        counted_object = drink

    calculated_object = []

    """Raise error for wrong meal and counting the number of the same object"""
    for data in counted_object:
        params = {
            'restaurant': restaurant,
            f'{data_name}s': data[data_name].id
        }

        if not Menu.objects.filter(**params).exists():
            msg = _(f"Some {data_name} doesn't come from restaurant menu")
            raise serializers.ValidationError(
                {f'wrong {data_name}': msg},
                code=data_name)

        if not calculated_object:
            calculated_object.append(
                {data_name: data[data_name], 'quantity': data['quantity']})
            continue

        for calculated_data in calculated_object:
            if data[data_name].id == calculated_data[data_name].id:
                calculated_data['quantity'] += data['quantity']
                break
            else:
                calculated_object.append(
                    {data_name: data[data_name], 'quantity': data['quantity']})
                break

    return calculated_object


class OrderMealSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        source='get_total_meal_price',
        read_only=True)
    price = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        source='meal.price',
        read_only=True)

    class Meta:
        model = OrderMeal
        exclude = ('order', 'id')


class OrderDetailMealSerializer(OrderMealSerializer):
    meal = serializers.StringRelatedField()


class OrderDrinkSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        source='get_total_drink_price',
        read_only=True)
    price = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        source='drink.price',
        read_only=True)

    class Meta:
        model = OrderDrink
        exclude = ('order', 'id')


class OrderDetailDrinkSerializer(OrderDrinkSerializer):
    drink = serializers.StringRelatedField()


class OrderSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00)
    restaurant = serializers.StringRelatedField()
    order_time = serializers.DateTimeField(format='%Y-%m-%d %H:%m')

    class Meta:
        model = Order
        exclude = ('user',)


class OrderDetailSerializer(OrderSerializer):
    meals = serializers.SerializerMethodField()
    drinks = serializers.SerializerMethodField()

    def get_meals(self, obj):
        meals = OrderMeal.objects.filter(order=obj)
        return OrderDetailMealSerializer(meals, many=True).data

    def get_drinks(self, obj):
        drinks = OrderDrink.objects.filter(order=obj)
        return OrderDetailDrinkSerializer(drinks, many=True).data


class OrderCreateSerializer(serializers.ModelSerializer):
    meals = OrderMealSerializer(many=True, write_only=True)
    drinks = OrderDrinkSerializer(many=True, write_only=True)
    order_time = serializers.DateTimeField(
        format='%Y-%m-%d %H:%m',
        read_only=True)

    class Meta:
        model = Order
        exclude = ('user',)
        read_only_fields = ('average_delivery_time', 'total_price')

    def validate(self, attr):
        restaurant = attr.get('restaurant')
        meals = attr.get('meals')
        drinks = attr.get('drinks')
        city = attr.get('delivery_city')
        post_code = attr.get('delivery_post_code')

        """Order can be delivered only within Warsaw"""
        if city.title() != 'Warsaw':
            msg = _("Orders are only available within Warsaw")
            raise serializers.ValidationError(
                {'delivery_city': msg}, code='city')

        """Check post code contain Warsaw district"""
        if post_code.split('-')[0][0] != '0':
            msg = _("Post code doesnt contain Warsaw district")
            raise serializers.ValidationError(
                {'post_code': msg}, code='post_code')

        """Raise error for empty order"""
        if not meals:
            msg = _("Cannot order nothing")
            raise serializers.ValidationError(
                {'meal': msg}, code='nothing')

        """Validate that meals and drinks come
           from right restaurant and calculate them"""
        attr['meals'] = calculate(meal=meals, restaurant=restaurant)
        attr['drinks'] = calculate(drink=drinks, restaurant=restaurant)

        return attr

    def create(self, validated_data):
        meals = validated_data.pop('meals')
        drinks = validated_data.pop('drinks')
        order = Order.objects.create(**validated_data)
        total = Decimal(0)

        """Create meals and drink models for order"""
        for meal_data in meals:
            OrderMeal.objects.create(order=order, **meal_data)

        for drink_data in drinks:
            OrderDrink.objects.create(order=order, **drink_data)

        meals = OrderMeal.objects.filter(order=order)
        drinks = OrderDrink.objects.filter(order=order)

        total += Decimal(
            sum([meal.get_total_meal_price for meal in meals]))
        total += Decimal(
            sum([drink.get_total_drink_price for drink in drinks]))

        order.total_price = total
        order.save()

        return order
