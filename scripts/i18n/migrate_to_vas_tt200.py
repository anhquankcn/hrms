#!/usr/bin/env python3
"""
Migrate an existing Company's Chart of Accounts to Vietnam TT200/VAS structure.

Pre-conditions: Company must have 0 transactions (GL Entry, Journal Entry, etc.)
Run inside Frappe container.

Args:
  COMPANY=<name>   (default: "Hồng Ngọc Hà Travel")
  --dry-run        preview only
"""
import sys
import os

DRY_RUN = "--dry-run" in sys.argv
COMPANY = os.environ.get("COMPANY", "Hồng Ngọc Hà Travel")
TEMPLATE_NAME = "Vietnam - Hệ thống tài khoản kế toán doanh nghiệp (TT200/2014)"

# Map of Company default field -> target VAS account number
DEFAULT_MAP = {
    "default_cash_account": "1111",
    "default_receivable_account": "131",
    "default_payable_account": "331",
    "round_off_account": "5118",
    "exchange_gain_loss_account": "635",
    "default_expense_account": "632",
    "default_income_account": "5111",
    "stock_received_but_not_billed": "151",
    "asset_received_but_not_billed": "151",
    "default_inventory_account": "156",
    "stock_adjustment_account": "632",
    "write_off_account": "6428",
    "default_employee_advance_account": "141",
    "default_payroll_payable_account": "3341",
    "accumulated_depreciation_account": "2141",
    "depreciation_expense_account": "6274",
    "expenses_included_in_asset_valuation": "6428",
    "disposal_account": "811",
    "capital_work_in_progress_account": "241",
    "expenses_included_in_valuation": "6428",
}


def main():
    import frappe
    from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts import create_charts

    frappe.init(site=os.environ.get("SITE", "frontend"))
    frappe.connect()

    print(f"Company: {COMPANY}")
    print(f"Template: {TEMPLATE_NAME}")
    print(f"Dry-run: {DRY_RUN}\n")

    if not frappe.db.exists("Company", COMPANY):
        print(f"ERROR: Company '{COMPANY}' not found")
        return

    txn_count = sum([
        frappe.db.count("GL Entry", {"company": COMPANY}),
        frappe.db.count("Journal Entry", {"company": COMPANY}),
        frappe.db.count("Sales Invoice", {"company": COMPANY}),
        frappe.db.count("Purchase Invoice", {"company": COMPANY}),
        frappe.db.count("Payment Entry", {"company": COMPANY}),
        frappe.db.count("Stock Entry", {"company": COMPANY}),
    ])
    if txn_count > 0:
        print(f"ABORT: Company has {txn_count} transactions. Migration unsafe.")
        return

    old_count = frappe.db.count("Account", {"company": COMPANY})
    print(f"Current accounts: {old_count}")

    if DRY_RUN:
        print("Dry-run complete.")
        frappe.destroy()
        return

    company = frappe.get_doc("Company", COMPANY)

    print("\n[1/4] Clearing Company default account fields...")
    for field in DEFAULT_MAP.keys():
        if company.get(field):
            company.set(field, None)
    company.save(ignore_permissions=True)
    frappe.db.commit()

    print("[2/4] Deleting existing accounts...")
    accounts = frappe.db.get_all("Account", filters={"company": COMPANY}, fields=["name"], order_by="lft desc")
    deleted = 0
    for acc in accounts:
        try:
            frappe.delete_doc("Account", acc["name"], ignore_permissions=True, force=True, delete_permanently=True)
            deleted += 1
        except Exception as e:
            try:
                frappe.db.sql("DELETE FROM `tabAccount` WHERE name = %s", acc["name"])
                deleted += 1
            except Exception as e2:
                print(f"  WARN delete failed: {acc['name']} ({e2})")
    frappe.db.commit()
    remaining = frappe.db.count("Account", {"company": COMPANY})
    print(f"  Deleted: {deleted}, remaining: {remaining}")

    print("[3/4] Creating accounts from VN TT200 template...")
    company.reload()
    company.chart_of_accounts = TEMPLATE_NAME
    company.save(ignore_permissions=True)
    create_charts(COMPANY, chart_template=TEMPLATE_NAME)
    frappe.db.commit()
    new_count = frappe.db.count("Account", {"company": COMPANY})
    print(f"  Accounts created: {new_count}")

    print("[4/4] Remapping Company default accounts...")
    company.reload()
    for field, account_number in DEFAULT_MAP.items():
        match = frappe.db.get_value(
            "Account",
            {"company": COMPANY, "account_number": account_number, "is_group": 0},
            "name",
        )
        if match:
            company.set(field, match)
            print(f"  {field} -> {match}")
        else:
            print(f"  {field}: no match for account_number={account_number}")
    company.save(ignore_permissions=True)
    frappe.db.commit()
    frappe.clear_cache()

    print(f"\nDone. {old_count} -> {new_count} accounts.")
    frappe.destroy()


if __name__ == "__main__":
    main()
