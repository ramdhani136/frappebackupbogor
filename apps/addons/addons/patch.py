from __future__ import unicode_literals
import frappe
import pandas as pd


# patch sinv account n repair gl entries
@frappe.whitelist()
def sinv_account():
    col = ["Name", "Item", "Incoming_Account"]
    data = pd.read_excel (r'/home/frappe/frappe-bench/apps/addons/addons/sinv_account.xls') 
    df = pd.DataFrame(data, columns=col)
    
    for index, row in df.iterrows():
        #Sales Invoice
        doc_si = frappe.get_doc('Sales Invoice Item',{ 'parent':row['Name'], 'item_code': row['Item']})
        if not pd.isna(row['Incoming_Account']):
            doc_si.income_account = row['Incoming_Account']
        doc_si.db_update()
        print("Item {} pada doc {} berhasil di rubah".format(row['Item'], row['Name']))

        frappe.db.sql(""" DELETE FROM `tabGL Entry` WHERE voucher_no = "{}" """.format(row['Name']))
        docu = frappe.get_doc('Sales Invoice', row['Name'])	
        docu.make_gl_entries()
        docu.repost_future_sle_and_gle()

def cust_credit_limit():
    name = "BUDI. IKM"
    customer = frappe.get_doc("Customer", name)
    customer.append("credit_limits", {
        "company": "PT EKATUNGGAL TUNAS MANDIRI - SEMARANG",
        "credit_limit": 25000000,
        "bypass_credit_limit_check": 1,
    })

    customer.db_update_all()

@frappe.whitelist()
def repair_gl_entry(doctype,docname):
    from erpnext.stock.stock_ledger import update_entries_after
    docu = frappe.get_doc(doctype, docname)
    print(docu.name)

    delete_gl = frappe.db.sql(""" DELETE FROM `tabGL Entry` WHERE voucher_no = "{}" """.format(docname))

    docu.make_gl_entries()
    print("DONE")

def patch_sinv():
    doctype = 'Sales Invoice'
    docname = 'SJ-2024-01-00066'
    doc = frappe.get_doc(doctype, docname)
    print(doc.name)
    doc.set_against_income_account()
    doc.run_method("calculate_taxes_and_totals")
    doc.db_update()
    doc.update_children()
    print("Done")

def cen_del():
    doctype = "Payment Entry"
    data = frappe.db.sql(""" SELECT name,docstatus,posting_date,payment_type FROM `tabPayment Entry` 
        WHERE payment_type = 'Receive' AND posting_date BETWEEN '2024-01-01' AND '2024-01-31' """.format(doctype),as_dict=1)
    
    print(len(data))
    con = 1
    for i in data:
        print(con)
        print(i['name']," || ",i['posting_date']," || ",i['docstatus'], ' || ',i['payment_type'])
        doc = frappe.get_doc("Payment Entry",i['name'])
        doc.delete()
        print(doc.name," ~~ ",doc.docstatus)
        print("DONE")
        con += 1