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
        for user in users:
            o_milestone = None
            milestones = repo.get_milestones(state='open')
            o_milestone = [m for m in milestones if m.title == milestone[0]]
            if repo.name != 'rke':
                if repo.name == 'dashboard':
                    working_label = '[zube]: To Test'
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
                # set the working label back to QA Working if repo was dashboard
                if repo.name == 'dashboard':
                    working_label = '[zube]: QA Working'
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


def create_data_for_spreadsheet(issues, users):
    worksheet_data = []
    for issue in issues:
        for user in users:
            if user in issue.assignees:
                size_label = []
                if len(issue.labels) > 0:
                    size_label = [label.name for label in issue.labels if label.name in size_labels.keys()]
                dupes = [wd[2] for wd in worksheet_data
                         if f'{issue.number} {issue.title}' in wd[2] and user.name in wd[0]]
                if len(dupes) > 0:
                    continue
                if issue.state == 'closed':
                    diff = get_start_date() - issue.closed_at
                    if diff and diff.days > 0:
                        continue
                test_event_date = None
                for e in issue.get_events().reversed:
                    if issue.repository.name == 'dashboard':
                        if e.event == 'labeled' and e.label.name == '[zube]: To Test':
                            test_event_date = e.created_at
                            break
                    else:
                        if e.event == 'labeled' and e.label.name == '[zube]: QA Working':
                            test_event_date = e.created_at
                            break
                worksheet_data.append([
                    user.name,
                    issue.repository.name,
                    f'{issue.number} {issue.title}',
                    'Closed' if issue.state == 'closed' else 'Working',
                    '' if len(size_label) == 0 else size_label[0],
                    issue.html_url,
                    test_event_date if issue.state != 'closed' else issue.closed_at
                ])
    return worksheet_data


def create_to_test_data_for_spreadsheet(issues, users):
    worksheet_data = []
    for issue in issues:
        for user in users:
            if user in issue.assignees:
                dupes = [wd[2] for wd in worksheet_data
                         if f'{issue.number} {issue.title}' in wd[2] and user.name in wd[0]]
                if len(dupes) > 0:
                    continue
                to_test_event_date = None
                for e in issue.get_events():
                    if e.event == 'labeled' and e.label.name == '[zube]: To Test':
                        to_test_event_date = e.created_at
                        break
                if to_test_event_date is None:
                    # issue has no event [zube]: To Test -> drop it
                    continue
                worksheet_data.append([
                    user.name,
                    issue.repository.name,
                    f'{issue.number} {issue.title}',
                    'Closed' if issue.state == 'closed' else 'Working',
                    issue.html_url,
                    to_test_event_date
                ])
    return worksheet_data
