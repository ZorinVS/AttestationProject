from django.contrib import admin
from django.utils.html import format_html

from electronics_network.models import ContactInfo, Product, SupplyChainMember


@admin.action(description='Очистить задолженность перед поставщиком у выбранных объектов')
def clear_debt(modeladmin, request, queryset):
    """ Очистка задолженности """
    count = queryset.update(debt=0)
    modeladmin.message_user(request, f'Количество объектов, у которых задолженность была очищена: {count}')


@admin.register(SupplyChainMember)
class SupplyChainMemberAdmin(admin.ModelAdmin):
    """ Админ-панель для модели участника цепочки поставок """

    list_display = (
        'id', 'name', 'type', 'level', 'contact', 'supplier_link', 'debt', 'created_at', 'user', 'product_list',
    )
    list_filter = ('contact__city',)
    actions = [clear_debt]
    readonly_fields = ('created_at', 'debt',)
    search_fields = ('name',)

    def supplier_link(self, instance):
        """ Получение ссылки на поставщика """
        if instance.supplier:
            return format_html(
                '<a href="/admin/electronics_network/supplychainmember/{}/change/">{}</a>',
                instance.supplier.id, instance.supplier.name
            )
        return '–'
    supplier_link.short_description = 'Ссылка на поставщика'

    def product_list(self, instance):
        """ Получение списка продуктов в виде строки (через запятую) """
        return ', '.join(f'{product.name} {product.model}' for product in instance.products.all())
    product_list.short_description = 'Продукты'


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    """ Админ-панель для модели контактных данных """

    list_display = ('id', 'network_member', 'email', 'country', 'city', 'street', 'house_number',)
    sortable_by = ('city',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """ Админ-панель для модели продукта """

    list_display = ('id', 'name', 'model', 'release_date',)
    sortable_by = ('release_date',)
