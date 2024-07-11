from __future__ import unicode_literals
import frappe

def delete_item():
    all_item = frappe.db.get_list("Item", pluck='name')
    print('---------------------------')
    for item in all_item:
        print(str(item))
        doc = frappe.get_doc("Item", item)

        if frappe.db.exists("Price List Generator Item", { "item_code": item }):
            print('Price List Generator')
            print('---------------------------')
            for plg in frappe.db.sql_list(""" Select DISTINCT parent from `tabPrice List Generator Item` where item_code = '{}' ORDER BY parent DESC """.format(item)):
                print(str(plg))
                doc_plg = frappe.get_doc("Price List Generator", plg)
                if doc_plg.docstatus == 1:
                    doc_plg.cancel()
                doc_plg.delete()

        if frappe.db.exists("Request Retur Items", { "item_code": item }):
            print('Request Retur')
            print('---------------------------')
            for rr in frappe.db.sql_list(""" Select DISTINCT parent from `tabRequest Retur Items` where item_code = '{}' ORDER BY parent DESC""".format(item)):
                print(str(rr))
                doc_rr = frappe.get_doc("Request Retur", rr)
                if doc_rr.docstatus == 1:
                    doc_rr.cancel()
                doc_rr.delete()

        doc.delete()
        frappe.db.commit()
        print('---------------------------')
