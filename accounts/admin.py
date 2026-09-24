from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import ProfilModel


class ProfilInline(admin.StackedInline):
    model               = ProfilModel
    can_delete          = False
    verbose_name_plural = 'Profil Bilgileri'
    fields              = ('telefon', 'sehir', 'avatar', 'biyografi', 'is_active')
    extra               = 0


class UserAdmin(BaseUserAdmin):
    inlines      = (ProfilInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter  = ('is_staff', 'is_active', 'groups')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(ProfilModel)
class ProfilAdmin(admin.ModelAdmin):
    list_display    = ('kullanici', 'email_goster', 'telefon', 'sehir', 'is_active', 'olusturuldu')
    list_filter     = ('is_active', 'sehir')
    search_fields   = ('kullanici__username', 'kullanici__email', 'telefon', 'sehir')
    readonly_fields = ('olusturuldu', 'guncellendi')

    def email_goster(self, obj):
        return obj.kullanici.email
    email_goster.short_description = 'E-posta'
