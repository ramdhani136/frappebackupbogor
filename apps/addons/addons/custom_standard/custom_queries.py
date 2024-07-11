# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import erpnext
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe.utils import nowdate, getdate
from collections import defaultdict
from erpnext.stock.get_item_details import _get_item_tax_template
from frappe.utils import unique

@frappe.whitelist()
def get_delivery_notes_to_be_billed_custom(doctype, txt, searchfield, start, page_len, filters, as_dict):
	fields = get_fields("Delivery Note", ["name", "customer", "posting_date", "grand_total"])

	return frappe.db.sql("""
		select %(fields)s
		from `tabDelivery Note`
		where `tabDelivery Note`.`%(key)s` like %(txt)s and
			`tabDelivery Note`.docstatus = 1
			and status not in ("Stopped", "Closed") %(fcond)s
			and (
				(`tabDelivery Note`.is_return = 0 and `tabDelivery Note`.per_billed < 100)
				or `tabDelivery Note`.grand_total = 0
				or (
					`tabDelivery Note`.is_return = 1
					and return_against in (select name from `tabDelivery Note` where per_billed < 100)
				)
			)
			%(mcond)s order by `tabDelivery Note`.`%(key)s` asc limit %(start)s, %(page_len)s
	""" % {
		"fields": ", ".join(["`tabDelivery Note`.{0}".format(f) for f in fields]),
		"key": searchfield,
		"fcond": get_filters_cond(doctype, filters, []),
		"mcond": get_match_cond(doctype),
		"start": start,
		"page_len": page_len,
		"txt": "%(txt)s"
	}, {"txt": ("%%%s%%" % txt)}, as_dict=as_dict)

def get_fields(doctype, fields=[]):
	meta = frappe.get_meta(doctype)
	fields.extend(meta.get_search_fields())

	if meta.title_field and not meta.title_field.strip() in fields:
		fields.insert(1, meta.title_field.strip())

	return unique(fields)
