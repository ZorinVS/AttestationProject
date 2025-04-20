from rest_framework import serializers

from electronics_network.models import ContactInfo, Product, SupplyChainMember


class ContactInfoSerializer(serializers.ModelSerializer):
    """ Сериализатор модели `ContactInfo` """

    class Meta:
        model = ContactInfo
        exclude = ('network_member',)


class ProductSerializer(serializers.ModelSerializer):
    """ Сериализатор модели `Product` """

    class Meta:
        model = Product
        fields = '__all__'


class SupplyChainMemberSerializer(serializers.ModelSerializer):
    """ Сериализатор модели `SupplyChainMember` """

    products = ProductSerializer(many=True, read_only=True)
    contact = ContactInfoSerializer()

    class Meta:
        model = SupplyChainMember
        fields = '__all__'
        read_only_fields = ('created_at', 'user',)

    def validate(self, data):
        """ Валидация ссылки на поставщика """
        supplier = data.get('supplier')
        instance_type = data.get('type', getattr(self.instance, 'type', None))

        if instance_type == 'factory' and supplier is not None:
            raise serializers.ValidationError({
                'supplier': 'Завод не может иметь поставщика.',
            })
        if instance_type == 'retail':
            if supplier is None:
                raise serializers.ValidationError({
                    'supplier': 'Розничная сеть должна иметь поставщика.',
                })
            if supplier.type == 'entrepreneur':
                raise serializers.ValidationError({
                    'supplier': 'Поставщиком для розничной сети не может быть индивидуальный предприниматель.',
                })
        if instance_type == 'entrepreneur' and supplier is None:
            raise serializers.ValidationError({
                'supplier': 'Индивидуальный предприниматель должен иметь поставщика.',
            })
        return data

    def create(self, validated_data):
        """ Создание объекта с созданием контактных данных """
        contact_data = validated_data.pop('contact')
        instance = SupplyChainMember.objects.create(**validated_data)
        ContactInfo.objects.create(network_member=instance, **contact_data)
        return instance

    def update(self, instance, validated_data):
        """ Обновление объекта с возможностью обновления контактных данных """
        contact_data = validated_data.pop('contact', None)
        if contact_data:
            contact = getattr(instance, 'contact', None)
            if contact:
                for attr, value in contact_data.items():
                    setattr(contact, attr, value)
                contact.save()
            else:
                ContactInfo.objects.create(member=instance, **contact_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
