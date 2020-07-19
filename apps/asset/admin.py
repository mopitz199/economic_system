from django.contrib import admin

from apps.asset.models import Asset, AssetDetail


class AssetAdmin(admin.ModelAdmin):
    search_fields = ['symbol', 'name']


admin.site.register(Asset, AssetAdmin)


class AssetDetailAdmin(admin.ModelAdmin):
    search_fields = ['name']


admin.site.register(AssetDetail, AssetDetailAdmin)
