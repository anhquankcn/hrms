#!/usr/bin/env python3
"""
Translate Chart of Accounts names from English to Vietnamese.

Run inside Frappe container:
  docker compose exec -T backend bash -c "cd /home/frappe/frappe-bench/sites && \
    ../env/bin/python /home/frappe/frappe-bench/apps/hrms/scripts/i18n/translate_accounts.py"

Args: --dry-run to preview only.
"""
import sys
import os

# Account name translations: English -> Vietnamese (TT200/VAS aligned)
TRANSLATIONS = {
    "Application of Funds (Assets)": "Tài sản",
    "Source of Funds (Liabilities)": "Nguồn vốn (Nợ phải trả)",
    "Equity": "Vốn chủ sở hữu",
    "Income": "Doanh thu",
    "Expenses": "Chi phí",

    "Current Assets": "Tài sản ngắn hạn",
    "Cash In Hand": "Tiền mặt tại quỹ",
    "Cash": "Tiền mặt",
    "Bank Accounts": "Tiền gửi ngân hàng",
    "Accounts Receivable": "Phải thu khách hàng",
    "Debtors": "Phải thu khách hàng",
    "Loans and Advances (Assets)": "Cho vay và Tạm ứng",
    "Employee Advances": "Tạm ứng nhân viên",
    "Securities and Deposits": "Ký quỹ, ký cược",
    "Earnest Money": "Tiền đặt cọc",
    "Investments": "Đầu tư tài chính",
    "Stock Assets": "Hàng tồn kho",
    "Stock In Hand": "Hàng tồn kho tại quỹ",
    "Tax Assets": "Tài sản thuế",
    "Asset Received But Not Billed": "Tài sản đã nhận chưa có hóa đơn",

    "Fixed Assets": "Tài sản cố định",
    "Buildings": "Nhà cửa, vật kiến trúc",
    "Capital Equipments": "Thiết bị đầu tư",
    "Electronic Equipments": "Thiết bị điện tử",
    "Office Equipments": "Thiết bị văn phòng",
    "Plants and Machineries": "Máy móc thiết bị",
    "Furnitures and Fixtures": "Nội thất và đồ đạc",
    "Softwares": "Phần mềm",
    "CWIP Account": "Xây dựng cơ bản dở dang",
    "Accumulated Depreciation": "Hao mòn lũy kế",

    "Current Liabilities": "Nợ ngắn hạn",
    "Accounts Payable": "Phải trả người bán",
    "Creditors": "Phải trả người bán",
    "Stock Liabilities": "Nợ phải trả tồn kho",
    "Stock Received But Not Billed": "Hàng đã nhận chưa có hóa đơn",
    "Duties and Taxes": "Thuế và các khoản phải nộp",
    "VAT": "Thuế GTGT",
    "TDS Payable": "Thuế khấu trừ phải nộp",
    "Payroll Payable": "Tiền lương phải trả",
    "Loans (Liabilities)": "Vay nợ",
    "Secured Loans": "Vay có bảo đảm",
    "Unsecured Loans": "Vay không bảo đảm",
    "Bank Overdraft Account": "Tài khoản thấu chi ngân hàng",

    "Capital Stock": "Vốn cổ phần",
    "Dividends Paid": "Cổ tức đã chi trả",
    "Opening Balance Equity": "Vốn số dư đầu kỳ",
    "Retained Earnings": "Lợi nhuận chưa phân phối",

    "Direct Income": "Doanh thu trực tiếp",
    "Indirect Income": "Doanh thu gián tiếp",
    "Sales": "Doanh thu bán hàng",
    "Service": "Doanh thu dịch vụ",
    "Commission on Sales": "Hoa hồng bán hàng",
    "Exchange Gain/Loss": "Lãi/lỗ chênh lệch tỷ giá",
    "Gain/Loss on Asset Disposal": "Lãi/lỗ thanh lý tài sản",

    "Direct Expenses": "Chi phí trực tiếp",
    "Indirect Expenses": "Chi phí gián tiếp",
    "Cost of Goods Sold": "Giá vốn hàng bán",
    "Administrative Expenses": "Chi phí quản lý",
    "Marketing Expenses": "Chi phí marketing",
    "Sales Expenses": "Chi phí bán hàng",
    "Salary": "Tiền lương",
    "Office Rent": "Tiền thuê văn phòng",
    "Office Maintenance Expenses": "Chi phí bảo trì văn phòng",
    "Telephone Expenses": "Chi phí điện thoại",
    "Postal Expenses": "Chi phí bưu chính",
    "Travel Expenses": "Chi phí công tác",
    "Entertainment Expenses": "Chi phí tiếp khách",
    "Legal Expenses": "Chi phí pháp lý",
    "Print and Stationery": "Chi phí in ấn và văn phòng phẩm",
    "Utility Expenses": "Chi phí điện nước",
    "Freight and Forwarding Charges": "Chi phí vận chuyển",
    "Miscellaneous Expenses": "Chi phí khác",
    "Depreciation": "Chi phí khấu hao",
    "Expenses Included In Asset Valuation": "Chi phí tính vào giá trị tài sản",
    "Expenses Included In Valuation": "Chi phí tính vào giá trị hàng tồn kho",
    "Stock Adjustment": "Điều chỉnh tồn kho",
    "Stock Expenses": "Chi phí kho",

    "Round Off": "Làm tròn",
    "Write Off": "Xóa sổ",
    "Temporary Accounts": "Tài khoản tạm",
    "Temporary Opening": "Mở số dư tạm",
}

DRY_RUN = "--dry-run" in sys.argv


def main():
    import frappe

    site = os.environ.get("SITE", "frontend")
    frappe.init(site=site)
    frappe.connect()

    changed = 0
    skipped = 0
    not_found = 0

    accounts = frappe.db.get_all("Account", fields=["name", "account_name"])
    print(f"Found {len(accounts)} accounts. Dry-run: {DRY_RUN}\n")

    for acc in accounts:
        old_acc_name = acc["account_name"]
        if old_acc_name not in TRANSLATIONS:
            not_found += 1
            continue
        new_acc_name = TRANSLATIONS[old_acc_name]
        if old_acc_name == new_acc_name:
            skipped += 1
            continue

        old_name = acc["name"]
        new_name = old_name.replace(old_acc_name, new_acc_name, 1)

        print(f"  {old_acc_name} -> {new_acc_name}")
        print(f"    {old_name}")
        print(f"      -> {new_name}")

        if not DRY_RUN:
            try:
                frappe.rename_doc("Account", old_name, new_name, merge=False, force=True, show_alert=False)
                frappe.db.set_value("Account", new_name, "account_name", new_acc_name)
                changed += 1
            except Exception as e:
                print(f"    ERROR: {e}")

    if not DRY_RUN:
        frappe.db.commit()
        frappe.clear_cache()

    print(f"\nSummary: changed={changed} skipped(same)={skipped} not_in_map={not_found}")
    frappe.destroy()


if __name__ == "__main__":
    main()
