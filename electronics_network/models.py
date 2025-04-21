from django.conf import settings
from django.db import models

from electronics_network.services import get_supply_chain_level_by_supplier


class SupplyChainMember(models.Model):
    """ Модель участника цепочки поставки """

    FACTORY = 'factory'
    RETAIL = 'retail'
    ENTREPRENEUR = 'entrepreneur'

    TYPE_CHOICES = [
        (FACTORY, 'Завод'),
        (RETAIL, 'Розничная сеть'),
        (ENTREPRENEUR, 'Индивидуальный предприниматель'),
    ]

    name = models.CharField(max_length=254, unique=True, verbose_name='Название участника сети продаж')
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, verbose_name='Тип участника')
    supplier = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='supply_chain_members',
        verbose_name='Поставщик'
    )
    debt = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name='Задолженность'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='supply_chain_members',
        verbose_name='Создатель',
    )

    @property
    def level(self):
        """ Вычисление уровня участника в иерархии поставок """
        return get_supply_chain_level_by_supplier(self.supplier)

    def __str__(self):
        return f'{self.name} (уровень {self.level} – {self.get_type_display()})'

    class Meta:
        verbose_name = 'участник цепочки поставок'
        verbose_name_plural = 'участники цепочки поставок'
        ordering = ('id',)


class ContactInfo(models.Model):
    """ Модель контактных данных """

    network_member = models.OneToOneField(
        'SupplyChainMember',
        on_delete=models.CASCADE,
        related_name='contact',
        verbose_name='Участник',
    )
    email = models.EmailField(verbose_name='Email')
    country = models.CharField(max_length=99, verbose_name='Страна')
    city = models.CharField(max_length=99, verbose_name='Город')
    street = models.CharField(max_length=99, verbose_name='Улица')
    house_number = models.CharField(max_length=9, verbose_name='Номер дома')

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'контактные данные'
        verbose_name_plural = 'контактные данные'
        ordering = ('id',)


class Product(models.Model):
    """ Модель продукта """

    name = models.CharField(max_length=254, verbose_name='Название')
    model = models.CharField(max_length=254, blank=True, null=True, verbose_name='Модель')
    release_date = models.DateField(verbose_name='Дата выхода на рынок')
    members = models.ManyToManyField(
        'SupplyChainMember',
        related_name='products',
        verbose_name='Участники сети'
    )

    def __str__(self):
        return f'{self.name} {self.model}'

    class Meta:
        verbose_name = 'продукт'
        verbose_name_plural = 'продукты'
        ordering = ('id',)
