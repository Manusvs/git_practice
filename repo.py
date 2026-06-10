#!/usr/bin/env python3

import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter


def run_command(cmd, cwd=None):
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.strip()


def clone_repository(repo_url):
    temp_dir = tempfile.mkdtemp(prefix="repo_analysis_")

    print(f"Cloning repository...")
    subprocess.run(
        ["git", "clone", "--quiet", repo_url, temp_dir],
        check=True
    )

    return temp_dir


def get_commit_data(repo_path):
    output = run_command(
        ["git", "log", "--format=%aI|%an"],
        cwd=repo_path
    )

    commits = []

    for line in output.splitlines():
        if "|" not in line:
            continue

        date_str, author = line.split("|", 1)

        commit_date = datetime.fromisoformat(
            date_str.replace("Z", "+00:00")
        )

        commits.append((commit_date, author))

    return commits


def commits_per_month(commits):
    now = datetime.now().astimezone()

    monthly_counts = Counter()

    for commit_date, _ in commits:
        if commit_date >= now - timedelta(days=365):
            month_key = commit_date.strftime("%Y-%m")
            monthly_counts[month_key] += 1

    return monthly_counts


def top_contributors(commits):
    authors = [author for _, author in commits]
    return Counter(authors).most_common(5)


def average_commits_per_day(commits):
    if not commits:
        return 0

    dates = sorted([d for d, _ in commits])

    first_date = dates[0]
    last_date = dates[-1]

    total_days = max(
        (last_date - first_date).days,
        1
    )

    return len(commits) / total_days


def longest_gap(commits):
    if len(commits) < 2:
        return 0, None, None

    dates = sorted([d for d, _ in commits])

    max_gap = timedelta(0)
    start = end = None

    for i in range(1, len(dates)):
        gap = dates[i] - dates[i - 1]

        if gap > max_gap:
            max_gap = gap
            start = dates[i - 1]
            end = dates[i]

    return max_gap.days, start, end


def print_report(commits):
    print("\n" + "=" * 50)
    print("GIT REPOSITORY ANALYSIS REPORT")
    print("=" * 50)

    print(f"\nTotal commits: {len(commits)}")

    print("\nCommits Per Month (Last 12 Months)")
    print("-" * 35)

    monthly = commits_per_month(commits)

    for month in sorted(monthly.keys()):
        print(f"{month}: {monthly[month]}")

    print("\nTop 5 Contributors")
    print("-" * 20)

    for name, count in top_contributors(commits):
        print(f"{name}: {count}")

    avg = average_commits_per_day(commits)

    print("\nAverage Commits Per Day")
    print("-" * 25)
    print(f"{avg:.2f}")

    gap_days, start, end = longest_gap(commits)

    print("\nLongest Gap Between Commits")
    print("-" * 30)

    if start and end:
        print(f"{gap_days} days")
        print(f"From: {start}")
        print(f"To  : {end}")


def main():
    repo_url = input(
        "Enter GitHub repository URL: "
    ).strip()

    repo_path = clone_repository(repo_url)

    try:
        commits = get_commit_data(repo_path)
        print_report(commits)

    finally:
        shutil.rmtree(repo_path)


if __name__ == "__main__":
    main()
