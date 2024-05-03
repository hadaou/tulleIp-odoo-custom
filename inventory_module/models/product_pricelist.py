from odoo import api, fields, models
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    def _compute_rent_rule(self, products, rental_duration=1, rental_unit='day', quantity=1, date=False, **kwargs):
        """
        Compute the rental rule applicable to the specified product.

        :param product: the product or product variant.
        :param quantity: Quantity of products requested.
        :param rental_duration: Numeric duration of the rental period.
        :param rental_unit: Unit of time for the rental duration ('hour', 'day', 'week', etc.).
        :param date: Date for price computation.
        :return: Dictionary with product ID as key and rental price as value.

        """
        if not products.exists():
            _logger.info('No products found for rental price computation.')
            return {}

        if not date:
            date = datetime.now()

        if not date:
            date = fields.Date.context_today(self)

        start_date = fields.Date.from_string(date)

        # Calculate the end_date based on the rental_duration and rental_unit
        if rental_unit == 'day':
            end_date = start_date + relativedelta(days=rental_duration)
        elif rental_unit == 'week':
            end_date = start_date + relativedelta(weeks=rental_duration)
        elif rental_unit == 'month':
            end_date = start_date + relativedelta(months=rental_duration)
        elif rental_unit == 'year':
            end_date = start_date + relativedelta(years=rental_duration)
        else:
            # Default to days if unit is not recognized
            _logger.info("Unrecognized rental_unit '%s', defaulting to days", rental_unit)
            end_date = start_date + relativedelta(days=rental_duration)

        try:

            price_rule = super()._compute_price_rule(
                products=products,
                quantity=quantity,
                date=date,
                start_date=start_date,
                end_date=end_date
            )
            return price_rule
        except Exception as e:
            _logger.error('Failed to compute rent rule: %s', e)
            return {}

    def _get_product_rental_price(self, product, *args, **kwargs):
        """
        Wrapper method to get the rental price for a product using _compute_rent_rule.

        :param product: Product record.
        :returns: Rental price for the product or None if not found.
        """
        if not product.exists():
            _logger.info('Product not found for rental price computation.')
            return None

        if not product.rent_ok:
            return None

        try:
            rent_check = super()._check_pricing_product_rental()
            rent_price_rule = self._compute_rent_rule(product, *args, **kwargs)
            # Attempt to retrieve the price rule tuple for the given product ID
            # If not found, return a default tuple of (None, None)
            price_rule_tuple = rent_price_rule.get(product.id, (None, None))
            # Extract the first element from the tuple, which is the rental price
            rental_price = price_rule_tuple[0]
            return rental_price
        except Exception as e:
            _logger.error('Failed to get product rental price: %s', e)
            return None