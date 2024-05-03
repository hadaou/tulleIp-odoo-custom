from odoo import api, fields, models

import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _is_notification_scheduled(self, scheduled_date):
        # Check if the 'sale.order' object has a method named '_is_notification_scheduled'
        if hasattr(super(SaleOrder, self), '_is_notification_scheduled'):
            # If it does, call it with 'scheduled_date' as a keyword argument
            return super(SaleOrder, self)._is_notification_scheduled(scheduled_date)
        else:
            # If it does not, return False
            return False