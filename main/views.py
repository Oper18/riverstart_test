# coding: utf-8

from rest_framework.generics import ListAPIView, DestroyAPIView, CreateAPIView, UpdateAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class ProductView(ListAPIView,
                  DestroyAPIView,
                  CreateAPIView,
                  UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request):
        if request.query_params.get('price_from'):
            self.queryset = self.queryset.filter(price__gte=float(request.query_params.get('price_from')))
        if request.query_params.get('price_to'):
            self.queryset = self.queryset.filter(price__lte=float(request.query_params.get('price_to')))
        if request.query_params.get('delete', None) and request.query_params.get('delete') == 1:
            self.queryset = self.queryset.filter(delete=True)
        else:
            self.queryset = self.queryset.filter(delete=False)
        return self.queryset
    
    def get_object(self, request=None):
        if request:
            return Product.objects.get(pk=request.data.get('id'))
        return super(ProductView, self).get_object()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset(request))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object(request)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
            instance.delete = True
            instance.save()

    def create(self, request, *args, **kwargs):
        request_data = request.data
        product = Product.objects.create(name=request_data.get('name'),
                                         price=request_data.get('price'),
                                         publish=request_data.get('publish', False))
        product.category.set(request_data.get('category'))
        product.save()
        return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object(request)
        request_data = request.data
        categories = request_data.pop('category', [])
        instance.category.set(Category.objects.filter(pk__in=categories))
        instance.save()
        serializer = self.get_serializer(instance, data=request_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class CategoryView(ListAPIView,
                   DestroyAPIView,
                   UpdateAPIView,
                   CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, request=None):
        if request:
            return Category.objects.get(pk=request.data.get('id'))
        else:
            return super(CategoryView, self).get_object()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object(request)
        if instance.products.all().exists():
            return Response(status=status.HTTP_409_CONFLICT)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object(request)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
