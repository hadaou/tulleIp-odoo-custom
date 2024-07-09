/** @odoo-module */

/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
import { PaymentScreenStatus } from "@point_of_sale/app/screens/payment_screen/payment_status/payment_status";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { patch } from "@web/core/utils/patch";  
import { formatFloat, roundDecimals as round_di } from "@web/core/utils/numbers";
patch(PaymentScreenStatus.prototype, {
    setup() {
      this.pos = usePos();
      super.setup();
    },
    
    get changeTextmc() {
      if (this.pos.config.enable_multi_currency && this.props.order.use_multi_currency) {
        var amt = this.pos.format_currency_n_symbol(this.props.order.get_change_mc(this.props.order.get_change(), this.props.order.selected_paymentline), 0.0001);
        var currency_id = this.props.order.selected_paymentline.other_currency_id;
        return this.pos.formating(amt, currency_id)
      }
      else {
        return this.env.utils.formatCurrency(this.props.order.get_change());
      }
    },
    get totalDueTextmc() {
      if (this.pos.config.enable_multi_currency && this.props.order.use_multi_currency) {
        var currency_id = this.props.order.selected_paymentline.other_currency_id;
        var due = this.props.order.get_change_mc(this.props.order.get_total_with_tax() + this.props.order.get_rounding_applied(), this.props.order.selected_paymentline)
        var amt = this.pos.format_currency_n_symbol(
          due > 0 ? due : 0, 0.0001);
        return this.pos.formating(amt, currency_id)
      }
      else {
        return this.env.utils.formatCurrency(
          this.props.order.get_total_with_tax() + this.props.order.get_rounding_applied()
        );
      }
    },
    get remainingTextmc() {
      if (this.pos.config.enable_multi_currency && this.props.order.use_multi_currency) {
        var currency_id = this.props.order.selected_paymentline.other_currency_id;
        var rem = this.props.order.get_change_mc(this.props.order.get_due(), this.props.order.selected_paymentline)
        var amt = this.pos.format_currency_n_symbol(
          rem > 0 ? rem : 0, 0.0001)
        return this.pos.formating(amt, currency_id)
      }
      else {
        return this.env.utils.formatCurrency(
          this.props.order.get_due() > 0 ? this.props.order.get_due() : 0
        );
      }
    },
    get convamount() {
      return this.env.utils.formatCurrency(this.props.order.selected_paymentline.get_amount());
    }
});
