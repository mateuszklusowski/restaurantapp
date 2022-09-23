from rest_framework import generics, viewsets, mixins

from .serializers import (OrderSerializer,
                          OrderCreateSerializer,
                          OrderDetailSerializer)

from core.models import Order


class OrderViewSet(viewsets.GenericViewSet,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    lookup_field = 'id'

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return OrderDetailSerializer

        return self.serializer_class


class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer

    def perform_create(self, serializer):
        """Create order with authenticated user"""
        serializer.save(user=self.request.user)
