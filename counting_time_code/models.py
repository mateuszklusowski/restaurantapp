class Order(models.Model):
    """Order model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    delivery_address = models.CharField(max_length=255, blank=False)
    delivery_city = models.CharField(max_length=255, blank=False)
    delivery_post_code = models.CharField(max_length=7, blank=False)
    delivery_phone = models.CharField(max_length=255, blank=False)
    order_time = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal(0))

    def __str__(self):
        return f'Order: {self.user}-{self.id} from {self.restaurant}'

    def save(self, *args, **kwargs):
        self.total_price += Decimal(self.restaurant.delivery_price)

        """Get average delivery time"""
        origins_address = '{0}, {1} {2}, {3}'.format(
            self.restaurant.address,
            self.restaurant.city,
            self.restaurant.post_code,
            self.restaurant.country
        )
        order_address = '{0}, {1} {2}, {3}'.format(
            self.delivery_address,
            self.delivery_city,
            self.delivery_post_code,
            self.delivery_country
        )
        self.average_delivery_time = get_average_delivery_time.delay(
            origins_address, 
            order_address)
        super().save(*args, **kwargs)