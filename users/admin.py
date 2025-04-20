from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """ Админ-панель для модели пользователя """
    list_display = ('id', 'email', 'phone_number', 'city',)
    exclude = ('password',)
    sortable_by = ('email',)
    search_fields = ('email',)
