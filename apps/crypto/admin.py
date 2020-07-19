from django.contrib import admin

from apps.crypto.models import Ranking


class RankingAdmin(admin.ModelAdmin):
    search_fields = ['asset__symbol']


admin.site.register(Ranking, RankingAdmin)
