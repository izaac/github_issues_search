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


def get_all_users_issues(repos, users, milestone):
    all_issues = []
    working_label = '[zube]: QA Working'
    done_label = '[zube]: Done'
    for repo in repos:
        if repo.name == 'dashboard':
            working_label = '[zube]: To Test'
        for user in users:
            o_milestone = None
            milestones = repo.get_milestones(state='open')
            o_milestone = [m for m in milestones if m.title == milestone[0]]
            if repo.name != 'rke':
                all_issues.extend(repo.get_issues(assignee=user,
                                                  state='open',
                                                  milestone=o_milestone[0],
                                                  labels=[working_label],
                                                  sort='updated')
                                  )
                all_issues.extend(repo.get_issues(assignee=user,
                                                  state='closed',
                                                  milestone=o_milestone[0],
                                                  labels=[done_label]
                                                  )
                                  )
            else:
                all_issues.extend(repo.get_issues(assignee=user,
                                                  state='open',
                                                  labels=[working_label],
                                                  sort='updated')
                                  )
                all_issues.extend(repo.get_issues(assignee=user,
                                                  state='closed',
                                                  labels=[done_label]
                                                  )
                                  )

    return all_issues


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
