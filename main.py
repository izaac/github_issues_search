from lib import github_authenticate
from lib.dates import set_start_date
from lib.gh import create_data_for_spreadsheet
from lib.gh import get_filtered_repos
from lib.gh import get_users_by_ids
from lib.gh import get_all_users_issues
from lib.xlsx import create_worksheet
from lib.xlsx import get_workbook_and_formats
from lib.xlsx import write_gh_data_to_worksheet
import confuse
import argparse

template = {
    'users_ids': confuse.StrSeq(),
    'repos': confuse.StrSeq(),
    'milestone': confuse.StrSeq()
}


def main(users_ids, repos, milestone):
    github_authenticate(args.token)
    set_start_date(args.date)
    repos = get_filtered_repos(repos)
    users = get_users_by_ids(users_ids)
    all_issues = get_all_users_issues(repos, users, milestone)

    worksheet_data = create_data_for_spreadsheet(all_issues, users)
    workbook, workbook_formats = get_workbook_and_formats()
    worksheet = create_worksheet(workbook, workbook_formats)
    write_gh_data_to_worksheet(worksheet, worksheet_data, workbook_formats)
    workbook.close()


if __name__ == '__main__':
    config = confuse.Configuration('issues_finder', __name__)
    parser = argparse.ArgumentParser(description='get github issues')
    parser.add_argument('--token', '-t', dest='token', metavar='GHTOKEN',
                        help='github token')
    parser.add_argument('--date', '-d', dest='date',
                        help='start date to start search for issues format: %Y-%m-%d 2021-03-20')

    args = parser.parse_args()
    config.set_file('./config_default.yaml')
    config.set_args(args, dots=True)

    # print('configuration directory is', config.config_dir())
    valid = config.get(template)
    main(valid.users_ids, valid.repos, valid.milestone)
