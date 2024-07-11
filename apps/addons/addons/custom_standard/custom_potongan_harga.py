from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.accounts.utils import get_account_currency, get_fiscal_years, validate_fiscal_year
from erpnext.accounts.doctype.gl_entry.gl_entry import update_outstanding_amt
def generate_journal(doc,method):
	total_disc=0
	fiscal_years = get_fiscal_years(doc.date, company="PT EKATUNGGAL TUNAS MANDIRI - BOGOR")[0][0]
	for row in doc.sales_inv:
		gl = frappe.new_doc("GL Entry")
		gl.account="1130.001 - Piutang Opr - Usaha - ETM-BGR"
		gl.party_type="Customer"
		gl.posting_date=doc.date
		gl.party=doc.customer
		gl.cost_center="Main - ETM-BGR"
		gl.debit=0
		gl.debit_in_account_currency=0
		gl.account_currency="IDR"
		gl.credit=row.potongan_harga
		gl.credit_in_account_currency=row.potongan_harga
		gl.voucher_type="Form Potongan Harga"
		gl.voucher_no=doc.name
		gl.is_opening="No"
		gl.against_voucher_type="Sales Invoice"
		gl.against_voucher=row.sales_invoice
		gl.fiscal_year=fiscal_years
		gl.company="PT EKATUNGGAL TUNAS MANDIRI - BOGOR"
		gl.is_cancelled=0
		gl.insert(ignore_permissions=True)
		total_disc=row.potongan_harga+total_disc
		update_outstanding_amt(
					gl.account,
					"Customer",
					gl.party,
					"Sales Invoice",
					gl.against_voucher
					)
	gl = frappe.new_doc("GL Entry")
	gl.account="4200.001 - By. Discount Penjualan - ETM-BGR"
	gl.party_type="Customer"
	gl.posting_date=doc.date
	gl.party=doc.customer
	gl.cost_center="SLS - ETM BGR - ETM-BGR"
	gl.debit=total_disc
	gl.debit_in_account_currency=total_disc
	gl.account_currency="IDR"
	gl.credit=0
	gl.credit_in_account_currency=0
	gl.voucher_type="Form Potongan Harga"
	gl.voucher_no=doc.name
	gl.is_opening="No"
	gl.fiscal_year=fiscal_years
	gl.company="PT EKATUNGGAL TUNAS MANDIRI - BOGOR"
	gl.is_cancelled=0
	gl.insert(ignore_permissions=True)

def patch():
	data=frappe.db.sql("""select name from `tabForm Potongan Harga` where docstatus=2 """,as_list=1)
	for row in data:
		delete_journal(frappe.get_doc("Form Potongan Harga",row[0]),"cancel")
		# frappe.db.commit()

def delete_journal(doc,method):
	frappe.db.sql("""delete from `tabGL Entry` where voucher_no='{}' and voucher_type="Form Potongan Harga" """.format(doc.name))
	for row in doc.sales_inv:
		update_outstanding_amt(
			"1130.001 - Piutang Opr - Usaha - ETM-BGR",
			"Customer",
			doc.customer,
			"Sales Invoice",
			row.sales_invoice
		)
	frappe.db.commit()

def generate_journal_old(doc,method):
	accounts=[]
	total_disc=0
	for row in doc.sales_inv:
		accounts.append({
			"account": "1130.001 - Piutang Opr - Usaha - ETM-BGR",
			"party_type": "Customer",
			"party": doc.customer,
			"cost_center": "Main - ETM-BGR",
			"credit":row.potongan_harga,
			"debit":0,
			"reference_type":"Sales Invoice",
			"reference_name":row.sales_invoice
		})
		total_disc=row.potongan_harga+total_disc
	accounts.append({
		"account": "4200.001 - By. Discount Penjualan - ETM-BGR",
		"cost_center": "SLS - ETM BGR - ETM-BGR",
		"credit":0,
		"debit":total_disc
	})
	fiscal_years = get_fiscal_years(doc.date, company="PT EKATUNGGAL TUNAS MANDIRI - BOGOR")[0][0]
	jv = frappe.new_doc("Journal Entry")
	jv.workflow_state="Pending"
	jv.voucher_type="Journal Entry"
	jv.naming_series="CJ-.YYYY.-.MM.-.####"
	jv.posting_date=doc.date
	jv.fiscal_year=fiscal_years
	jv.company="PT EKATUNGGAL TUNAS MANDIRI - BOGOR"
#	jv.title=doc.name
#	jv.accounts=accounts
	jv.user_remark="Potongan Discount"
#	jv.insert(ignore_permissions=True,ignore_mandatory=True)
	jv.accounts=accounts
	jv.insert(ignore_permissions=True,ignore_mandatory=True)
#	jv.save(ignore_permissions=True, ignore_version=True)
	doc.jv=jv.name
	frappe.msgprint("Journal Created , Please Review and Do Submit , Voucher No {}".format(jv.name))

