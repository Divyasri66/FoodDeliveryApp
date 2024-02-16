# models.py
from django.db import models

class Organization(models.Model):
    name = models.CharField(max_length=100)

class Item(models.Model):
    TYPE_CHOICES = (
        ('perishable', 'Perishable'),
        ('non-perishable', 'Non-Perishable'),
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.CharField(max_length=255)

class Pricing(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    zone = models.CharField(max_length=100)
    base_distance_in_km = models.FloatField()
    km_price = models.DecimalField(max_digits=5, decimal_places=2)
    fix_price = models.DecimalField(max_digits=5, decimal_places=2)

# serializers.py
from rest_framework import serializers
from .models import Pricing

class PricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pricing
        fields = '_all_'

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Pricing
from .serializers import PricingSerializer

class CalculateDeliveryCost(APIView):
    def post(self, request):
        zone = request.data.get('zone')
        organization_id = request.data.get('organization_id')
        total_distance = request.data.get('total_distance')
        item_type = request.data.get('item_type')

        pricing = Pricing.objects.filter(organization_id=organization_id, zone=zone).first()
        if not pricing:
            return Response({'error': 'Pricing not found for the specified organization and zone'}, status=400)

        base_distance = pricing.base_distance_in_km
        km_price = pricing.km_price
        fix_price = pricing.fix_price

        if total_distance <= base_distance:
            total_price = fix_price
        else:
            total_price = fix_price + (total_distance - base_distance) * km_price

        response_data = {'total_price': total_price}
        return Response(response_data)

# price_calculation.py
class PriceCalculator:
    @staticmethod
    def calculate_delivery_cost(pricing, total_distance):
        base_distance = pricing.base_distance_in_km
        km_price = pricing.km_price
        fix_price = pricing.fix_price

        if total_distance <= base_distance:
            total_price = fix_price
        else:
            total_price = fix_price + (total_distance - base_distance) * km_price

        return total_price * 100  # Convert to cents

# urls.py
from django.urls import path
from .views import CalculateDeliveryCost

urlpatterns = [
    path('calculate_delivery_cost/', CalculateDeliveryCost.as_view(), name='calculate_delivery_cost'),
]