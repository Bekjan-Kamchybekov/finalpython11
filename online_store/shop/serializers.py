from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'age', 'phone_number', 'status', 'date_registered')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self,validated_data):
        user = UserProfile.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user':{
                'username': instance.username,
                'email': instance.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Неверные учетные данные")

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user':{
                'username': instance.username,
                'email': instance.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),

        }


class UserProfile1Serializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class UserProfileSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'phone_number', 'status']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_name']

class ProductPhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPhotos
        fields = ['image']

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField('%d-%m-%Y %H:%M')
    class Meta:
        model = Review
        fields = '__all__'

class ProductListSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    date = serializers.DateField('%d-%m-%Y')

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'price', 'average_rating', 'date']

    def get_average_rating(self, obj):
        return obj.get_average_rating()

class ProductDetailSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    category = CategorySerializer()
    product = ProductPhotosSerializer(read_only=True, many=True)
    ratings = RatingSerializer(read_only=True, many=True)
    reviews = ReviewSerializer(read_only=True, many=True)
    date = serializers.DateField('%d-%m-%Y')
    owner = UserProfileSimpleSerializer()

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'category', 'description', 'product', 'product_video', 'average_rating', 'price', 'active', 'ratings', 'reviews', 'date', 'owner']


    def get_average_rating(self, obj):
        return obj.get_average_rating()

class CartItemSerializers(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, source='Product')

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'get_total_price']


class CartSerializers(serializers.ModelSerializer):
    items = CartItemSerializers(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price']

    def get_total_price(self,obj):
        return obj.get_total_price()