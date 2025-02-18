from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import OrderLineItem
import logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=OrderLineItem)
def update_on_save(sender, instance, created, **kwargs):
    logger.debug(f"Signal triggered: update_on_save for OrderLineItem {instance.id}")
    instance.order.update_total()

@receiver(post_delete, sender=OrderLineItem)
def update_on_delete(sender, instance, **kwargs):
    logger.debug(f"Signal triggered: update_on_delete for OrderLineItem {instance.id}")
    instance.order.update_total()