from celery import shared_task

from apps.asset.services import update_all_asset_health


@shared_task
def update_all_asset_health_task():
    update_all_asset_health()
