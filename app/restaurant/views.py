from rest_framework import viewsets, mixins, permissions

from .serializers import RestaurantDetailSerializer, RestaurantSerializer

from core.models import Restaurant


class RestaurantViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin):
    serializer_class = RestaurantSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Restaurant.objects.all()
    lookup_field = 'slug'

    def get_queryset(self):
        """Params filtering"""
        queryset = self.queryset
        cuisine = str(self.request.query_params.get('cuisine', '')).lower()
        city = str(self.request.query_params.get('city', '')).title()

        if city != '':
            queryset = queryset.filter(city=city)

        if cuisine != '':
            queryset = queryset.filter(cuisine__name=cuisine)

        return queryset

    def get_serializer_class(self):
        """Return appropraite serializer class"""
        if self.action == 'retrieve':
            return RestaurantDetailSerializer

        return self.serializer_class
