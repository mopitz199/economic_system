from django.contrib import admin

from apps.chart.models import Chart, Candle, Point


class ChartAdmin(admin.ModelAdmin):
    search_fields = ['asset__symbol']


admin.site.register(Chart, ChartAdmin)


class CandleAdmin(admin.ModelAdmin):
    ordering = ['-candle_date']
    search_fields = ['chart__asset__symbol']


admin.site.register(Candle, CandleAdmin)


class PointAdmin(admin.ModelAdmin):
    ordering = ['-point_date']
    search_fields = ['chart__asset__symbol']


admin.site.register(Point, PointAdmin)
