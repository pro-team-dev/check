from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from goal.models import User

class CustomUserModelAdmin(BaseUserAdmin):
    list_display = ('id', 'email', 'name', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        ('User Credentials', {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email', 'id')
    filter_horizontal = ()

# Register the CustomUser model with the common admin class
admin.site.register(User, CustomUserModelAdmin)
