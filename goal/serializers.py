from rest_framework import serializers
from goal.models import User,Offer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from goal.utils import Util
from .models import User, Tour
from rest_framework.validators import UniqueValidator



class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type':'password'}, write_only=True)
    is_guide = serializers.BooleanField(default=False, write_only=True)
    profile = serializers.CharField(allow_blank=True, allow_null=True,required=False)
    username = serializers.CharField(max_length=200,validators=[UniqueValidator(queryset=User.objects.all())])
    citizenship = serializers.CharField(max_length=200, allow_blank=True, allow_null=True,required=False)
    languages = serializers.ListField(child=serializers.CharField(max_length=50), allow_null=True, allow_empty=True,required=False,default="['english']")
    phone_number = serializers.CharField(max_length=15, allow_blank=True, allow_null=True)
    hourly_rate = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True,required=False)
    location = serializers.CharField(max_length=15, allow_blank=True, allow_null=True,required=False)


    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'is_guide', 'profile', 'username', 'citizenship', 'languages', 'phone_number', 'hourly_rate','location']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        is_guide = validated_data.pop('is_guide', False)
        profile = validated_data.pop('profile', '')
        username = validated_data.pop('username', '')
        citizenship = validated_data.pop('citizenship', '')
        languages = validated_data.pop('languages', [])
        phone_number = validated_data.pop('phone_number', '')
        hourly_rate = validated_data.pop('hourly_rate', None)
        location=validated_data.pop('location',None)

        user = User.objects.create_user(**validated_data, is_guide=is_guide, profile=profile, username=username, citizenship=citizenship,location=location)
        user.languages = languages
        user.phone_number = phone_number
        user.hourly_rate = hourly_rate
        user.save()

        return user


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User  
        fields = ['email', 'password']

class UserProfileSerializer(serializers.ModelSerializer):
    languages = serializers.ListField(child=serializers.CharField(max_length=50), required=False, allow_null=True)
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'profile', 'username', 'citizenship','is_guide','phone_number','hourly_rate','ongoing_tour','languages','location']

class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        password = attrs.get('password')
        user = self.context.get('user')
        user.set_password(password)
        user.save()
        return attrs

class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = 'http://localhost:3000/api/user/reset/' + uid + '/' + token
            body = 'Click Following Link to Reset Your Password ' + link
            data = {
                'subject': 'Reset Your Password',
                'body': body,
                'to_email': user.email
            }
            # Util.send_email(data)
            return attrs
        else:
            raise serializers.ValidationError('You are not a Registered User')

class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            uid = self.context.get('uid')
            token = self.context.get('token')
            id = smart_str(urlsafe_base64_decode(uid))
            
            if not User.objects.filter(id=id).exists():
                raise serializers.ValidationError('User not found')

            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('Token is not Valid or Expired')

            user.set_password(password)
            user.save()
            return attrs
        except (DjangoUnicodeDecodeError, User.DoesNotExist):
            raise serializers.ValidationError('Token is not Valid or Expired')
        


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ['id', 'tour', 'guide', 'tourist', 'price', 'duration']

class TourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tour
        fields = '__all__'