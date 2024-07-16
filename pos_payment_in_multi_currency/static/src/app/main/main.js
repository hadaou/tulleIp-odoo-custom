/** @odoo-module */
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { Payment } from "@point_of_sale/app/store/models";
import { formatFloat, roundDecimals as round_di } from "@web/core/utils/numbers";
patch(PosStore.prototype, {
    async _processData(loadedData) {
        await super._processData(...arguments);
        var self = this;
        const currencies = await self.orm.silent.call(
           'res.currency',
           'get_currency',
            [this.config.multi_currency_ids]
        )
        if (currencies) {     
            self.currencies = false
            if (self.config.enable_multi_currency && self.config.multi_currency_ids) {
                self.currencies = []
                self.currency_by_id = {}
                currencies.forEach(function (currencie) {
                    if (self.config.multi_currency_ids.includes(currencie.id)) {
                        if (self.config.currency_id[0] != currencie.id) {
                            self.currencies.push(currencie)
                            self.currency_by_id[currencie.id] = currencie
                        }
                    }
                    if (self.config.currency_id[0] == currencie.id) {
                        self.currencies.push(currencie)
                        self.currency_by_id[currencie.id] = currencie
                    }
                    if (currencie.rate == 1) {
                        self.base_currency = currencie
                    }
                });
            }
        }
    },
    formating(amount, currency_id) {
        if (currency_id) {
          var currency = this.currency_by_id[currency_id];
        }
        else {
          var currency = this.currency;
        }
        if (currency.position === 'after') {
          return amount + ' ' + (currency.symbol || '');
        } else {
          return (currency.symbol || '') + ' ' + amount;
        }
      },
      format_currency_n_symbol(amount, precisson) {
        if (typeof amount === 'number') {

          var decimals = 0; //Haitham remove decimals
          //var decimals = 4;
          amount = round_di(amount, decimals)
          amount = formatFloat(round_di(amount, decimals), {
            digits: [69, decimals],
          });
        }
        return amount;
  
      },
});
patch(Order.prototype, {
    setup(options) {
        super.setup(...arguments);
        var self = this;
        self.use_multi_currency = self.use_multi_currency || false;
        self.multi_payment_lines = self.multi_payment_lines || {};
        self.is_multi_currency_payment = self.is_multi_currency_payment || false;
    },
    init_from_JSON(json) {
        var self = this;
        super.init_from_JSON(...arguments);
        this.use_multi_currency = json.use_multi_currency || false;
        this.other_currency_amount = json.other_currency_amount || false;
        this.multi_payment_lines = json.multi_payment_lines || {};
        this.is_multi_currency_payment = json.is_multi_currency_payment || false;
        this.reprint = json.reprint || false;

    },
    export_as_JSON() {
        var self = this;
        var loaded = super.export_as_JSON();
        if (self.use_multi_currency)
            loaded.use_multi_currency = self.use_multi_currency;
            loaded.reprint = self.reprint;
        loaded.multi_payment_lines = self.multi_payment_lines;
        loaded.is_multi_currency_payment = self.is_multi_currency_payment;
        return loaded
    },
    export_for_printing() {
        var self = this;
        var receipt = super.export_for_printing();
        receipt.multi_payment_lines = self.get_paymentlines();
        // if (receipt.multi_payment_lines.length) {
        //     receipt.multi_payment_lines.forEach(function (line) {
        //         if (line.is_multi_currency_payment) {
        //             line.other_currency_amount=formatFloat(round_di(line.other_currency_amount, 4), { digits: [69, 4] });
        //         }
        //     });
        // }
        if(self.reprint){
            receipt.is_multi_currency_payment = self.is_multi_currency_payment;
            receipt.multi_payment_lines = self.multi_payment_lines;
            receipt.multi_payment_lines.forEach(function(line){
                if(line.is_change){
                    receipt.is_other_currency_change = true
                    receipt.change_other_currency_id = line.other_currency_id
                    receipt.change_other_currency_amount = line.other_currency_amount
                }
            })
        }
        receipt.is_multi_currency_payment = self.is_multi_currency_payment;
        return receipt;
    },
    get_other_currency_amount(line) {
        var self = this;
        if (line && line.currency_id) {
            var amt = (self.pos.currency_by_id[line.currency_id].rate * line.otc_amount) / self.pos.currency.rate
            line.other_currency_amount = (self.pos.currency_by_id[line.currency_id].rate * line.get_amount()) / self.pos.currency.rate;
            var res = formatFloat(round_di(amt, 0), { digits: [69, 0] }); //Haitham, remove decimals
            //var res = formatFloat(round_di(amt, 4), { digits: [69, 4] });
            return res;
        }
        else {
            line.other_currency_amount = 0.0;
            return 0.0;
        }
    },
    get_change_mc(change, paymentline) {
        if (this.use_multi_currency && paymentline && paymentline.other_currency_id) {
            var amt = (this.pos.currency_by_id[paymentline.currency_id].rate * change) / this.pos.currency.rate
            amt = parseFloat(round_di(amt, 4));
            return amt
        } else {
            return Math.max(0, change);
        }
    }
});
patch(Payment.prototype, {
    setup() {
        super.setup(...arguments);
        var self = this;
        // self.other_currency_id = false
        // self.other_currency_rate = false
        // self.other_currency_amount = 0.0
        // self.otc_amount = 0.0
        self.currency_id = self.currency_id || false;
        self.other_currency_id = self.currency_id || false;
        self.other_currency_rate = self.other_currency_rate || false;
        self.other_currency_amount = self.other_currency_amount || 0.0;
        self.is_multi_currency_payment = self.is_multi_currency_payment || false;
        self.otc_amount = self.otc_amount || 0;
    },
    init_from_JSON(json) {
        var self = this;
        super.init_from_JSON(...arguments);
        self.currency_id = json.currency_id || false;
        self.other_currency_id = self.currency_id || false;
        self.other_currency_rate = json.other_currency_rate || false;
        self.other_currency_amount = self.other_currency_amount || 0.0;
        self.is_multi_currency_payment = json.is_multi_currency_payment || false;
        self.otc_amount = json.otc_amount || 0.0;
    },
    export_as_JSON() {
        var self = this;
        var loaded = super.export_as_JSON();
        if (self.currency_id) {
            loaded.currency_id = self.currency_id;
        }
        if (self.other_currency_id) {
            loaded.other_currency_id = self.currency_id;
        }
        if (self.other_currency_rate) {
            loaded.other_currency_rate = self.other_currency_rate;
        }
        if (self.other_currency_amount) {
            loaded.other_currency_amount = self.other_currency_amount;
        }
        if (self.is_multi_currency_payment) {
            loaded.is_multi_currency_payment = self.is_multi_currency_payment
        }
        if (self.otc_amount) {
            loaded.otc_amount = self.otc_amount
        }
        return loaded;
    }
});
