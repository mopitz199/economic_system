from celery import shared_task

from apps.chart.services import (
    update_not_ending_asset_milestones_prices,
)


@shared_task
def update_not_ending_asset_milestones_prices_task():
    update_not_ending_asset_milestones_prices()
