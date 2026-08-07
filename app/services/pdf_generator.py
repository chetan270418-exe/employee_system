"""
PDF Generator — Creates salary slips using ReportLab
"""
import os
import calendar
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def generate_salary_slip(payroll, employee, slip_path):
    """Generate a PDF salary slip for an employee."""
    doc = SimpleDocTemplate(
        slip_path,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )

    styles = getSampleStyleSheet()
    elements = []

    # Color palette
    primary_color = colors.HexColor('#1a237e')
    accent_color = colors.HexColor('#0d47a1')
    light_bg = colors.HexColor('#e8eaf6')
    white = colors.white

    # Header
    header_style = ParagraphStyle('Header', fontName='Helvetica-Bold', fontSize=18,
                                   textColor=white, alignment=TA_CENTER, spaceAfter=2)
    sub_header_style = ParagraphStyle('SubHeader', fontName='Helvetica', fontSize=11,
                                       textColor=white, alignment=TA_CENTER)

    header_data = [
        [Paragraph('<b>SMART PAYROLL MANAGEMENT SYSTEM</b>', header_style)],
        [Paragraph('Employee Salary Slip', sub_header_style)],
    ]
    header_table = Table(header_data, colWidths=[180*mm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), primary_color),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('ROWHEIGHT', (0, 0), (0, 0), 28),
        ('ROWHEIGHT', (0, 1), (0, 1), 20),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8*mm))

    # Month/Year label
    month_name = calendar.month_name[payroll.month]
    slip_title = ParagraphStyle('SlipTitle', fontName='Helvetica-Bold', fontSize=13,
                                 textColor=accent_color, alignment=TA_CENTER)
    elements.append(Paragraph(f'Salary Slip for {month_name} {payroll.year}', slip_title))
    elements.append(Spacer(1, 5*mm))
    elements.append(HRFlowable(width='100%', thickness=1.5, color=primary_color))
    elements.append(Spacer(1, 5*mm))

    # Employee Info Grid
    info_style = ParagraphStyle('Info', fontName='Helvetica', fontSize=10)
    info_bold = ParagraphStyle('InfoBold', fontName='Helvetica-Bold', fontSize=10)
    dept_name = employee.department.name if employee.department else 'N/A'

    info_data = [
        [Paragraph('<b>Employee Name:</b>', info_bold), Paragraph(employee.name, info_style),
         Paragraph('<b>Employee ID:</b>', info_bold), Paragraph(employee.employee_id, info_style)],
        [Paragraph('<b>Designation:</b>', info_bold), Paragraph(employee.designation or 'N/A', info_style),
         Paragraph('<b>Department:</b>', info_bold), Paragraph(dept_name, info_style)],
        [Paragraph('<b>PAN Number:</b>', info_bold), Paragraph(employee.pan_number or 'N/A', info_style),
         Paragraph('<b>Bank Account:</b>', info_bold), Paragraph(employee.bank_account or 'N/A', info_style)],
        [Paragraph('<b>Date of Joining:</b>', info_bold), Paragraph(str(employee.join_date) if employee.join_date else 'N/A', info_style),
         Paragraph('<b>Generated On:</b>', info_bold), Paragraph(datetime.now().strftime('%d %b %Y'), info_style)],
    ]
    info_table = Table(info_data, colWidths=[45*mm, 50*mm, 45*mm, 40*mm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), light_bg),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, light_bg]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#c5cae9')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 5*mm))

    # Attendance Summary
    att_header = ParagraphStyle('AttHeader', fontName='Helvetica-Bold', fontSize=11,
                                  textColor=white, alignment=TA_CENTER)
    att_data = [
        [Paragraph('<b>Attendance Summary</b>', att_header), '', '', ''],
        [Paragraph('<b>Working Days</b>', info_bold), Paragraph(str(payroll.working_days), info_style),
         Paragraph('<b>Present Days</b>', info_bold), Paragraph(str(payroll.present_days), info_style)],
        [Paragraph('<b>Absent Days</b>', info_bold), Paragraph(str(payroll.absent_days), info_style),
         Paragraph('<b>Leave Days</b>', info_bold), Paragraph(str(payroll.leave_days), info_style)],
        [Paragraph('<b>Overtime Hours</b>', info_bold), Paragraph(f"{payroll.overtime_hours:.1f} hrs", info_style),
         Paragraph('', info_style), Paragraph('', info_style)],
    ]
    att_table = Table(att_data, colWidths=[45*mm, 50*mm, 45*mm, 40*mm])
    att_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (3, 0)),
        ('BACKGROUND', (0, 0), (3, 0), accent_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_bg]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#c5cae9')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(att_table)
    elements.append(Spacer(1, 5*mm))

    # Earnings & Deductions
    earn_style = ParagraphStyle('EarnHead', fontName='Helvetica-Bold', fontSize=11,
                                  textColor=white, alignment=TA_CENTER)

    def fmt(val):
        return f'₹ {float(val):,.2f}'

    sal_data = [
        [Paragraph('<b>Earnings</b>', earn_style), Paragraph('<b>Amount</b>', earn_style),
         Paragraph('<b>Deductions</b>', earn_style), Paragraph('<b>Amount</b>', earn_style)],
        ['Basic Salary', fmt(payroll.base_salary), 'Provident Fund (PF)', fmt(payroll.pf)],
        ['HRA (20%)', fmt(payroll.hra), 'ESI', fmt(payroll.esi)],
        ['DA (10%)', fmt(payroll.da), 'TDS', fmt(payroll.tds)],
        ['Travel Allowance', fmt(payroll.ta), 'Leave Deduction', fmt(payroll.leave_deduction)],
        ['Overtime', fmt(payroll.overtime_amount), 'Other Deductions', fmt(payroll.other_deductions)],
        ['Bonus', fmt(payroll.bonus), '', ''],
        [Paragraph('<b>Gross Salary</b>', info_bold), Paragraph(f'<b>{fmt(payroll.gross_salary)}</b>', info_bold),
         Paragraph('<b>Total Deductions</b>', info_bold), Paragraph(f'<b>{fmt(payroll.total_deductions)}</b>', info_bold)],
    ]
    sal_table = Table(sal_data, colWidths=[55*mm, 35*mm, 55*mm, 35*mm])
    sal_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#2e7d32')),
        ('BACKGROUND', (2, 0), (3, 0), colors.HexColor('#b71c1c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f1f8e9')]),
        ('BACKGROUND', (0, -1), (1, -1), colors.HexColor('#c8e6c9')),
        ('BACKGROUND', (2, -1), (3, -1), colors.HexColor('#ffcdd2')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ccc')),
        ('PADDING', (0, 0), (-1, -1), 7),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
    ]))
    elements.append(sal_table)
    elements.append(Spacer(1, 6*mm))

    # Net Salary Box
    net_style = ParagraphStyle('Net', fontName='Helvetica-Bold', fontSize=14,
                                 textColor=white, alignment=TA_CENTER)
    net_data = [[Paragraph(f'NET SALARY: ₹ {float(payroll.net_salary):,.2f}', net_style)]]
    net_table = Table(net_data, colWidths=[180*mm])
    net_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), primary_color),
        ('PADDING', (0, 0), (-1, -1), 14),
        ('ROWHEIGHT', (0, 0), (-1, -1), 30),
    ]))
    elements.append(net_table)
    elements.append(Spacer(1, 6*mm))

    # Footer
    footer_style = ParagraphStyle('Footer', fontName='Helvetica', fontSize=8,
                                   textColor=colors.grey, alignment=TA_CENTER)
    elements.append(HRFlowable(width='100%', thickness=0.5, color=colors.grey))
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph('This is a computer-generated salary slip and does not require a signature.', footer_style))
    elements.append(Paragraph(f'Generated on {datetime.now().strftime("%d %B %Y at %I:%M %p")}', footer_style))

    doc.build(elements)
    return slip_path
