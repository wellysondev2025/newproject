from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserProfile


# Inline para editar o profile junto com o usuário
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

    list_display = ("email", "full_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email", "profile__full_name")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissões", {"fields": ("is_active", "is_staff", "is_superuser")}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "cpf", "birth_date", "user")
    search_fields = ("full_name", "cpf", "user__email")
