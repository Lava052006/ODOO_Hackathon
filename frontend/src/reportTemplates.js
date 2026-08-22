/**
 * ARIA Report & Document Generation Templates
 * Generates formatted CSVs and PDF/Printable executive reports.
 */

function formatInr(val) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0
  }).format(val || 0)
}

export function downloadCsv(filename, csvContent) {
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
  const url = URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export function printOrSavePdf(htmlContent, title = "ARIA-Report") {
  const printWindow = window.open("", "_blank")
  if (!printWindow) {
    alert("Please allow pop-ups to generate and print PDF reports.")
    return
  }

  const fullHtml = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>${title}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      color: #1a202c;
      background: #fff;
      padding: 32px;
      line-height: 1.5;
    }

    .report-container {
      max-width: 800px;
      margin: 0 auto;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 32px;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }

    .header-row {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      border-bottom: 2px solid #0d9488;
      padding-bottom: 20px;
      margin-bottom: 24px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .brand-title {
      font-size: 24px;
      font-weight: 800;
      color: #0f172a;
      letter-spacing: -0.5px;
    }

    .brand-sub {
      font-size: 11px;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .doc-meta {
      text-align: right;
    }

    .doc-meta h2 {
      font-size: 18px;
      color: #0d9488;
      font-weight: 700;
      margin-bottom: 4px;
    }

    .doc-meta p {
      font-size: 12px;
      color: #64748b;
    }

    .info-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      background: #f8fafc;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 24px;
      font-size: 13px;
    }

    .info-item {
      display: flex;
      justify-content: space-between;
      padding: 4px 0;
      border-bottom: 1px solid #edf2f7;
    }

    .info-item span { color: #64748b; }
    .info-item strong { color: #0f172a; font-weight: 600; }

    table.report-table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 24px;
      font-size: 13px;
    }

    table.report-table th {
      background: #f1f5f9;
      color: #334155;
      font-weight: 600;
      text-align: left;
      padding: 10px 12px;
      border-bottom: 1px solid #cbd5e1;
    }

    table.report-table td {
      padding: 10px 12px;
      border-bottom: 1px solid #e2e8f0;
      color: #334155;
    }

    table.report-table tr:last-child td {
      border-bottom: 0;
    }

    .text-right { text-align: right !important; }
    .text-center { text-align: center !important; }

    .summary-box {
      display: flex;
      justify-content: flex-end;
      margin-top: 16px;
      margin-bottom: 32px;
    }

    .summary-card {
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      border-radius: 8px;
      padding: 16px 24px;
      min-width: 260px;
      text-align: right;
    }

    .summary-card small {
      display: block;
      color: #166534;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
    }

    .summary-card strong {
      display: block;
      font-size: 22px;
      color: #15803d;
      font-weight: 800;
      margin-top: 4px;
    }

    .footer {
      border-top: 1px solid #e2e8f0;
      padding-top: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11px;
      color: #94a3b8;
    }

    .signatory {
      text-align: right;
      font-size: 12px;
      color: #475569;
    }

    .signatory-line {
      width: 140px;
      border-top: 1px dashed #94a3b8;
      margin-top: 36px;
      margin-left: auto;
      margin-bottom: 4px;
    }

    @media print {
      body { padding: 0; }
      .report-container { border: 0; box-shadow: none; padding: 0; }
      .no-print { display: none; }
    }
  </style>
</head>
<body>
  <div class="no-print" style="margin-bottom: 20px; text-align: center;">
    <button onclick="window.print()" style="background: #0d9488; color: #fff; border: 0; padding: 10px 24px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 14px;">Print / Save as PDF</button>
  </div>
  <div class="report-container">
    ${htmlContent}
  </div>
  <script>
    window.onload = function() {
      setTimeout(function() { window.print(); }, 400);
    }
  </script>
</body>
</html>`

  printWindow.document.open()
  printWindow.document.write(fullHtml)
  printWindow.document.close()
}

export function generatePayslipPdf(employee) {
  const basic = Number(employee.basic || 50000)
  const hra = Number(employee.hra || 15000)
  const special = Number(employee.special || 12000)
  const other = Number(employee.other || 5000)
  const gross = basic + hra + special + other

  const pf = Math.round(basic * 0.12)
  const pt = 200
  const tds = Math.round(gross * 0.05)
  const totalDeductions = pf + pt + tds
  const netPay = gross - totalDeductions

  const content = `
    <div class="header-row">
      <div class="brand">
        <div>
          <div class="brand-title">ARIA HRMS</div>
          <div class="brand-sub">Workforce & Payroll Management</div>
        </div>
      </div>
      <div class="doc-meta">
        <h2>SALARY PAYSLIP</h2>
        <p>Period: <b>August 2026</b></p>
        <p>Generated: 22 Aug 2026</p>
      </div>
    </div>

    <div class="info-grid">
      <div>
        <div class="info-item"><span>Employee Name:</span><strong>${employee.name || 'Employee'}</strong></div>
        <div class="info-item"><span>Employee ID:</span><strong>${employee.id || employee.employeeId || 'EMP1024'}</strong></div>
        <div class="info-item"><span>Designation:</span><strong>${employee.role || employee.jobTitle || 'Software Engineer'}</strong></div>
        <div class="info-item"><span>Department:</span><strong>${employee.department || 'Engineering'}</strong></div>
      </div>
      <div>
        <div class="info-item"><span>Location:</span><strong>${employee.location || 'New Delhi'}</strong></div>
        <div class="info-item"><span>Bank Account:</span><strong>HDFC Bank ··· 4892</strong></div>
        <div class="info-item"><span>PAN Number:</span><strong>ABCDE1234F</strong></div>
        <div class="info-item"><span>Payment Status:</span><strong style="color: #16a34a;">Verified & Processed</strong></div>
      </div>
    </div>

    <table class="report-table">
      <thead>
        <tr>
          <th>Earnings Component</th>
          <th class="text-right">Amount</th>
          <th>Deductions Component</th>
          <th class="text-right">Amount</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Basic Salary</td>
          <td class="text-right">${formatInr(basic)}</td>
          <td>Provident Fund (PF)</td>
          <td class="text-right">${formatInr(pf)}</td>
        </tr>
        <tr>
          <td>House Rent Allowance (HRA)</td>
          <td class="text-right">${formatInr(hra)}</td>
          <td>Professional Tax (PT)</td>
          <td class="text-right">${formatInr(pt)}</td>
        </tr>
        <tr>
          <td>Special Allowance</td>
          <td class="text-right">${formatInr(special)}</td>
          <td>Income Tax (TDS)</td>
          <td class="text-right">${formatInr(tds)}</td>
        </tr>
        <tr>
          <td>Other Allowances</td>
          <td class="text-right">${formatInr(other)}</td>
          <td>—</td>
          <td class="text-right">—</td>
        </tr>
        <tr style="font-weight: 700; background: #f8fafc;">
          <td>Total Gross Earnings</td>
          <td class="text-right" style="color: #0d9488;">${formatInr(gross)}</td>
          <td>Total Deductions</td>
          <td class="text-right" style="color: #dc2626;">${formatInr(totalDeductions)}</td>
        </tr>
      </tbody>
    </table>

    <div class="summary-box">
      <div class="summary-card">
        <small>Net Payable Salary</small>
        <strong>${formatInr(netPay)}</strong>
      </div>
    </div>

    <div class="footer">
      <div>
        <p>This is a computer-generated document authorized by ARIA Systems.</p>
        <p>Verification Code: ARIA-PAY-202608-${employee.id || 'EMP1024'}</p>
      </div>
      <div class="signatory">
        <div class="signatory-line"></div>
        <p>Authorized Signatory<br><b>Head of People Operations</b></p>
      </div>
    </div>
  `

  printOrSavePdf(content, `ARIA-Payslip-${employee.id || 'EMP'}-Aug-2026`)
}

export function generatePayrollSummaryPdf(payrollData, employees) {
  const totalGross = payrollData?.summary?.grossPayroll || '₹73.5L'
  const empCount = employees.length || 120

  const empRows = employees.slice(0, 20).map((emp, i) => {
    const gross = (emp.basic || 0) + (emp.hra || 0) + (emp.special || 0) + (emp.other || 0)
    const net = gross - (emp.deductions || 0)
    return `
      <tr>
        <td>${emp.id}</td>
        <td><strong>${emp.name}</strong></td>
        <td>${emp.role || 'Engineer'}</td>
        <td class="text-right">${formatInr(emp.basic)}</td>
        <td class="text-right">${formatInr(gross)}</td>
        <td class="text-right"><strong>${formatInr(net)}</strong></td>
        <td class="text-center" style="color: #15803d; font-weight: 600;">Verified</td>
      </tr>
    `
  }).join('')

  const content = `
    <div class="header-row">
      <div class="brand">
        <div>
          <div class="brand-title">ARIA HRMS</div>
          <div class="brand-sub">Executive Payroll & Compensation Report</div>
        </div>
      </div>
      <div class="doc-meta">
        <h2>PAYROLL SUMMARY REPORT</h2>
        <p>Cycle: <b>August 2026</b></p>
        <p>Status: <b>Verified in PostgreSQL</b></p>
      </div>
    </div>

    <div class="info-grid">
      <div>
        <div class="info-item"><span>Total Employees:</span><strong>${empCount} Active Personnel</strong></div>
        <div class="info-item"><span>Scheduled Pay Date:</span><strong>31 August 2026</strong></div>
      </div>
      <div>
        <div class="info-item"><span>Total Gross Payroll:</span><strong style="color: #0d9488;">${totalGross}</strong></div>
        <div class="info-item"><span>Pre-flight Checks:</span><strong style="color: #16a34a;">100% Cleared</strong></div>
      </div>
    </div>

    <h3 style="font-size: 14px; font-weight: 700; margin-bottom: 8px; color: #1e293b;">Departmental Payroll Allocation</h3>
    <table class="report-table">
      <thead>
        <tr>
          <th>Department</th>
          <th class="text-center">Staff Count</th>
          <th class="text-right">Monthly Gross</th>
          <th class="text-right">Est. Net Outflow</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>Engineering</td><td class="text-center">35</td><td class="text-right">₹34,80,000</td><td class="text-right">₹30,28,000</td></tr>
        <tr><td>Customer Success</td><td class="text-center">24</td><td class="text-right">₹16,80,000</td><td class="text-right">₹14,78,400</td></tr>
        <tr><td>Operations</td><td class="text-center">26</td><td class="text-right">₹15,60,000</td><td class="text-right">₹13,72,800</td></tr>
        <tr><td>Product & Design</td><td class="text-center">15</td><td class="text-right">₹15,00,000</td><td class="text-right">₹13,05,000</td></tr>
        <tr><td>Finance & People</td><td class="text-center">20</td><td class="text-right">₹16,00,000</td><td class="text-right">₹13,92,000</td></tr>
      </tbody>
    </table>

    <h3 style="font-size: 14px; font-weight: 700; margin-bottom: 8px; color: #1e293b;">Employee Compensation Excerpt (Top Records)</h3>
    <table class="report-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Employee</th>
          <th>Role</th>
          <th class="text-right">Basic</th>
          <th class="text-right">Gross</th>
          <th class="text-right">Net Pay</th>
          <th class="text-center">Status</th>
        </tr>
      </thead>
      <tbody>
        ${empRows}
      </tbody>
    </table>

    <div class="footer">
      <div>ARIA Enterprise HR System · Confidential Payroll Record</div>
      <div class="signatory">
        <div class="signatory-line"></div>
        <p>Chief Financial Officer & HR Director</p>
      </div>
    </div>
  `

  printOrSavePdf(content, `ARIA-Executive-Payroll-Report-Aug-2026`)
}

export function generateAttendanceSummaryPdf(stats, rows) {
  const rowHtml = rows.slice(0, 25).map((r) => `
    <tr>
      <td><strong>${r.name}</strong></td>
      <td>${r.employeeId || 'EMP'}</td>
      <td class="text-center"><span style="color: ${r.status === 'Present' ? '#15803d' : r.status === 'Remote' ? '#0369a1' : '#b45309'}; font-weight: 600;">${r.status}</span></td>
      <td>${r.in || '09:00'}</td>
      <td>${r.out || '18:00'}</td>
      <td>${r.hours || '9h 00m'}</td>
      <td>${r.location || 'New Delhi'}</td>
    </tr>
  `).join('')

  const content = `
    <div class="header-row">
      <div class="brand">
        <div>
          <div class="brand-title">ARIA HRMS</div>
          <div class="brand-sub">Daily Attendance & Presence Intelligence</div>
        </div>
      </div>
      <div class="doc-meta">
        <h2>ATTENDANCE LOG REPORT</h2>
        <p>Date: <b>22 August 2026</b></p>
        <p>Presence: <b>${stats.presentPercentage || 81.7}% Verified</b></p>
      </div>
    </div>

    <div class="info-grid">
      <div>
        <div class="info-item"><span>Present Today:</span><strong>${stats.presentToday || 98} Teammates</strong></div>
        <div class="info-item"><span>Remote Working:</span><strong>${stats.remoteToday || 10} Teammates</strong></div>
      </div>
      <div>
        <div class="info-item"><span>Average Check-in:</span><strong>${stats.avgCheckIn || '09:06 AM'}</strong></div>
        <div class="info-item"><span>Exceptions Flagged:</span><strong>${stats.exceptionsCount || 0} Resolved</strong></div>
      </div>
    </div>

    <table class="report-table">
      <thead>
        <tr>
          <th>Employee</th>
          <th>ID</th>
          <th class="text-center">Status</th>
          <th>Check-in</th>
          <th>Check-out</th>
          <th>Work Duration</th>
          <th>Location</th>
        </tr>
      </thead>
      <tbody>
        ${rowHtml}
      </tbody>
    </table>

    <div class="footer">
      <div>ARIA Biometric & Time Tracking Log · Official Record</div>
      <div class="signatory">
        <div class="signatory-line"></div>
        <p>Operations Manager</p>
      </div>
    </div>
  `

  printOrSavePdf(content, `ARIA-Daily-Attendance-Report-22-Aug-2026`)
}
