import os
import frappe

os.chdir('/home/frappe/frappe-bench')
frappe.init('hrms.localhost', sites_path='sites')
frappe.connect()
frappe.db.set_value('System Settings', 'System Settings', 'time_zone', 'Asia/Kolkata')
frappe.db.commit()
print("SUCCESS: System Settings time_zone set to Asia/Kolkata")
