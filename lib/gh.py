from lib import process_github_data
from lib import get_github_session
from lib.dates import get_start_date

size_labels = {'QA/XS': 0.5, 'QA/S': 1, 'QA/M': 3, 'QA/L': 5, 'QA/XL': 10}


def get_filtered_repos(repos):
    reps = process_github_data()
    return [r for r in reps if r.full_name in repos]


def get_users_by_ids(users_ids):
    users = []
    for userx in users_ids:
        users.append(get_github_session().get_user(userx))
    return users


def get_all_users_issues(repos, users):
    all_issues = []
    dt = get_start_date()
    for repo in repos:
        for user in users:
            all_issues.extend(repo.get_issues(assignee=user,
                                              state='all',
                                              sort='updated',
                                              since=dt)
                              )
    return all_issues


def filter_issues(issues):
    filtered_list = []
    for issue in issues:
        if len(issue.labels) == 0:
            continue
        if issue.title in [i.title for i in filtered_list]:
            continue
        if issue.state == 'closed':
            filtered_list.append(issue)
        if '[zube]: QA Working' in [x.name for x in issue.labels]:
            filtered_list.append(issue)
        if issue.repository.name == 'dashboard':
            if '[zube]: To Test' in [x.name for x in issue.labels]:
                filtered_list.append(issue)
    return filtered_list


def create_date_for_spreadsheet(issues, users):
    worksheet_data = []
    for issue in issues:
        for user in users:
            if user in issue.assignees:
                size_label = []
                if len(issue.labels) > 0:
                    size_label = [label.name for label in issue.labels if label.name in size_labels.keys()]
                dupes = [wd[2] for wd in worksheet_data if f'{issue.number} {issue.title}' in wd[2]]
                if len(dupes) > 0:
                    continue
                if issue.state == 'closed':
                    diff = get_start_date() - issue.closed_at
                    if diff and diff.days > 0:
                        continue
                worksheet_data.append([
                    user.name,
                    issue.repository.name,
                    f'{issue.number} {issue.title}',
                    'Closed' if issue.state == 'closed' else 'Working',
                    '' if len(size_label) == 0 else size_label[0],
                    issue.html_url,
                    issue.updated_at if issue.state != 'closed' else issue.closed_at
                ])
    return worksheet_data
