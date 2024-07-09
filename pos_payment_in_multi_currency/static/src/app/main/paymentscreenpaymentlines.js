/** @odoo-module */

/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

import { PaymentScreenPaymentLines } from "@point_of_sale/app/screens/payment_screen/payment_lines/payment_lines";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreenPaymentLines.prototype, {
    setup() {
        this.pos = usePos();
        super.setup();
    },
    formatLineAmount(paymentline) {
        var self = this;
        var current_order = self.pos.get_order();
        if (this.pos.config.enable_multi_currency && current_order.use_multi_currency && paymentline.is_multi_currency_payment) {
            var amt = current_order.get_other_currency_amount(paymentline);
            current_order.is_multi_currency_payment = paymentline.is_multi_currency_payment;
            return amt
        } else {
            return self.env.utils.formatCurrency(paymentline.get_amount());
        }
    }
});
