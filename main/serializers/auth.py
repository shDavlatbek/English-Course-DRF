from rest_framework import serializers
from main import models
from django.contrib.auth import authenticate



class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ["first_name", "last_name", "email", "password"]
        extra_kwargs = {
            "email": {
                "error_messages": {
                    "unique": "already_registered",
                    "required": "missing_required_field",
                }
            },
            "password": {
                "error_messages": {
                    "required": "missing_required_field",
                }
            },
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = models.User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password')
        user = super().update(instance, validated_data)
        user.set_password(password)
        user.save()
        return user



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, error_messages={"required": "missing_required_field"})
    password = serializers.CharField(write_only=True, required=True, error_messages={"required": "missing_required_field"})

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        if email and password:
            user = authenticate(request=self.context.get("request"), email=email, password=password)
            if not user:
                raise serializers.ValidationError(
                    {"auth": "invalid_credentials"}
                )
        data["user"] = user
        return data