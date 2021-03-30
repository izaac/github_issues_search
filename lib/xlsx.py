from .dates import get_today
from .dates import get_start_date
from .dates import get_business_hours_rules
import xlsxwriter


today = get_today()
businesshrs = get_business_hours_rules()


def get_workbook_and_formats():
    workbook = xlsxwriter.Workbook(f'issues-{today.strftime("%m%d%Y-%H%M%S")}.xlsx')
    date_format_yellow = workbook.add_format({'num_format': 'dd/mm/yy hh:mm', 'bg_color': 'yellow'})
    bold = workbook.add_format({'bold': 1})
    date_format = workbook.add_format({'num_format': 'dd/mm/yy hh:mm'})
    bg_yellow = workbook.add_format({'bg_color': 'yellow'})

    workbook_formats = {'date_format_yellow': date_format_yellow,
                        'bold': bold,
                        'date_format': date_format,
                        'bg_yellow': bg_yellow
                        }
    return workbook, workbook_formats


def create_worksheet(workbook, formats):
    dt = get_start_date()
    bold = formats['bold']
    worksheet = workbook.add_worksheet('QAIssues')
    worksheet.set_column(0, 0, 25)
    worksheet.set_column(1, 1, 15)
    worksheet.set_column(2, 2, 50)
    worksheet.set_column(5, 5, 25)
    worksheet.write('A1', f'Since {dt.strftime("%b %d %Y %H:%M:%S")}', bold)
    worksheet.write('A2', 'Person', bold)
    worksheet.write('B2', 'Repo', bold)
    worksheet.write('C2', 'Issue', bold)
    worksheet.write('D2', 'Status', bold)
    worksheet.write('E2', 'Size', bold)
    worksheet.write('F2', 'Updated At', bold)
    return worksheet


def write_gh_data_to_worksheet(worksheet, worksheet_data, workbook_formats):
    worksheet_data.sort()
    row = 2
    col = 0

    for name, repo, issue, status, size, url, updated_or_closed_at in worksheet_data:
        bg_yellow = workbook_formats['bg_yellow']
        time_diff_hours = None
        print(status)
        if size:
            time_diff_hours = businesshrs.difference(updated_or_closed_at, today).timedelta.total_seconds() / 3600
        if (time_diff_hours and time_diff_hours > 0) and status != 'Closed':
            worksheet.write_string(row, col, name, cell_format=bg_yellow)
            worksheet.write_string(row, col + 1, repo, cell_format=bg_yellow)
            worksheet.write_url(row, col + 2, url, string=issue, cell_format=bg_yellow)
            worksheet.write_string(row, col + 3, status, cell_format=bg_yellow)
            worksheet.write_string(row, col + 4, size, cell_format=bg_yellow)
            worksheet.write_datetime(row, col + 5, updated_or_closed_at, workbook_formats['date_format_yellow'])
            row += 1
            continue

        worksheet.write_string(row, col, name)
        worksheet.write_string(row, col + 1, repo)
        worksheet.write_url(row, col + 2, url, string=issue)
        worksheet.write_string(row, col + 3, status)
        worksheet.write_string(row, col + 4, size)
        worksheet.write_datetime(row, col + 5, updated_or_closed_at, workbook_formats['date_format'])
        row += 1
