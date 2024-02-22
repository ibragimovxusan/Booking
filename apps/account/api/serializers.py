from rest_framework import serializers

from apps.account.models import User, Company


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'avatar'
        ]


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'avatar',
            'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'read_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data['phone_number'],
            role='user',
            avatar=validated_data['avatar'],
            password=validated_data['password']
        )
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.set_password(validated_data.get('password', instance.password))
        instance.save()
        return instance


class BarberUserSerializer(serializers.ModelSerializer):
    company = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'avatar',
            'start',
            'end',
            'break_start',
            'break_end',
            'company'
        ]


class BarberUserCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'avatar',
            'start',
            'end',
            'break_start',
            'break_end',
            'company',
            'password',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'read_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data['phone_number'],
            role='barber',
            avatar=validated_data['avatar'],
            start=validated_data['start'],
            end=validated_data['end'],
            break_start=validated_data['break_start'],
            break_end=validated_data['break_end'],
            company=validated_data['company'],
            password=validated_data['password']
        )
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.start = validated_data.get('start', instance.start)
        instance.end = validated_data.get('end', instance.end)
        instance.break_start = validated_data.get('break_start', instance.break_start)
        instance.break_end = validated_data.get('break_end', instance.break_end)
        instance.company = validated_data.get('company', instance.company)
        instance.set_password(validated_data.get('password', instance.password))
        instance.save()
        return instance


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'address',
            'is_active',
            'employees',
        ]


class CompanyCreateSerializer(serializers.ModelSerializer):
    employees = BarberUserSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'address',
            'is_active',
            'employees',
        ]
        extra_kwargs = {
            'employees': {'read_only': True}
        }
