/** @odoo-module */
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { formatFloat, roundDecimals as round_di } from "@web/core/utils/numbers";
import { onMounted } from "@odoo/owl";
patch(PaymentScreen.prototype, {
  setup() {
    this.pos = usePos();
    this.popup = useService("popup");
    super.setup();
  },
  updateSelectedPaymentline(amount = false) {
    if (this.paymentLines.every((line) => line.paid)) {
      this.currentOrder.add_paymentline(this.pos.payment_methods[0]);
    }
    if (!this.selectedPaymentLine) return; // do nothing if no selected payment line
    // disable changing amount on paymentlines with running or done payments on a payment terminal
    if (
      this.payment_interface &&
      !['pending', 'retry'].includes(this.selectedPaymentLine.get_payment_status())
    ) {
      return;
    }
    if (this.numberBuffer.get() === null) {
      this.deletePaymentLine({ detail: { cid: this.selectedPaymentLine.cid } });
    } else {
      if (this.selectedPaymentLine.is_multi_currency_payment) {
        var amt = (this.numberBuffer.getFloat() * this.pos.currency.rate) / this.selectedPaymentLine.other_currency_rate;
        this.selectedPaymentLine.otc_amount = amt;
        this.selectedPaymentLine.set_amount(amt);
      }
      else {
        this.selectedPaymentLine.set_amount(this.numberBuffer.getFloat());
      }
    }
  },
  clickmulticurrency() {
    var self = this;
    var order = self.pos.get_order();
    if (order && order.use_multi_currency) {
      order.use_multi_currency = false
      $('.wk-multi-currency').removeClass('highlight');
      if (order && order.get_paymentlines() && order.get_paymentlines().length) {
        order.get_paymentlines().forEach(function (paymentline) {
          paymentline.other_currency_id = false
          paymentline.other_currency_rate = 0
          paymentline.other_currency_amount = 0
          paymentline.is_multi_currency_payment = false
          if (self.pos.config.currency_id && self.pos.config.currency_id[0]) {
            paymentline.currency_id = self.pos.config.currency_id[0]

          }
        })
        // self.pos.change()
      }
    } else {
      order.use_multi_currency = true
      $('.wk-multi-currency').addClass('highlight');
    }
    order.export_as_JSON();
    order.save_to_db()
  },
  async addNewPaymentLine(paymentMethod) {
    var self = this;
    var current_order = self.pos.get_order();
    if (this.currentOrder.electronic_payment_in_progress()) {
      self.popup.add(ErrorPopup, {
        title: ('Error'),
        body: ('There is already an electronic payment in progress.'),
      });
      return false;
    } else {
      var currency_id = self.pos.config.currency_id[0];
      if (this.pos.config.enable_multi_currency && current_order.use_multi_currency) {
        var popup = await self.popup.add(MultiCurrencyPopup, { 'payment_id': paymentMethod })
        if (popup.confirmed) {
          currency_id = popup.payload
        }
      }
      var paymentline = this.currentOrder.add_paymentline(paymentMethod);
      if (current_order.selected_paymentline) {
        current_order.selected_paymentline.currency_id = parseInt(currency_id);
        if (self.pos.currency_by_id) {
          var currency_data = self.pos.currency_by_id[currency_id];
          current_order.selected_paymentline.other_currency_id = parseInt(currency_id);
          if (currency_data) {
            current_order.selected_paymentline.other_currency_rate = currency_data.rate
          }
          current_order.selected_paymentline.is_multi_currency_payment = true
          current_order.selected_paymentline.otc_amount = current_order.selected_paymentline.get_amount()
        }
      }
      this.numberBuffer.reset();
      this.payment_interface = paymentMethod.payment_terminal;
      if (this.payment_interface) {
        this.currentOrder.selected_paymentline.set_payment_status('pending');
      }
      return true;
    }
  }
});
export class MultiCurrencyPopup extends AbstractAwaitablePopup {
  static template = "pos_payment_in_multi_currency.MultiCurrencyPopup";
  static defaultProps = {
    confirmText: 'ADD',
    cancelText: 'Cancel',
    title: 'Select the Product',
    body: '',
    list: []
  };
  amountCheck() {
    var currency_id = $('.wk-selected-currency').val()
    if (currency_id) {
      var currency = this.pos.currency_by_id[currency_id]
      if (currency) {
        $(".wk-exchange-rate").html(currency.rate)
        var rate = (currency.rate * 1) / this.pos.currency_by_id[this.pos.config.currency_id[0]].rate
        rate = formatFloat(round_di(rate, 5), { digits: [69, 5] })
        $(".wk-currency-amount").html(rate)
        $(".wk-currency-name").html(currency.name + "(" + currency.symbol + ")")
      }
    }
  }
  setup() {
    this.pos = usePos();
    super.setup();
    onMounted(this.onMounted);
  }
  onMounted() {
    var self = this;
    self.amountCheck();
  }
  selected_currency() {
    var self = this;
    self.amountCheck();
  }
  getPayload() {
    var currency_id = $('.wk-selected-currency').val();
    return currency_id;
  }
};

