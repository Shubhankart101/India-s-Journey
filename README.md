# GitHub Metrics Dashboard

A daily, data-first view of the public GitHub footprint for [Shubhankar Thapliyal](https://github.com/Shubhankart101). Metrics are collected from the GitHub REST API, stored as dated snapshots, and rendered below by GitHub Actions.

## Daily Dashboard

<!-- METRICS:START -->

> Last refreshed: **2026-08-21T14:21:24+00:00**

| Metric | Value |
| --- | ---: |
| Public repositories | 28 |
| Followers | 0 |
| Following | 0 |
| Public gists | 0 |
| Total stars | 0 |
| Total forks | 0 |
| Open issues | 0 |
| Repository size | 196,155 KB |
| Repositories updated in 30 days | 18 |
| Recent public events | 100 |
| Recent push events | 96 |

**Primary language mix:** Python: 5 | C#: 3 | HCL: 2 | Shell: 2 | Go Template: 1 | PowerShell: 1 | CSS: 1 | JavaScript: 1

### Recently Updated Public Repositories

| Repository | Last updated (UTC) | Stars |
| --- | --- | ---: |
| TerraformRepoForNotes | 2026-08-21 | 0 |
| PythonScriptingForDevOpsRepoForNotes | 2026-08-21 | 0 |
| Kubernetes-DockerForDevOpsRepoForNotes | 2026-08-21 | 0 |
| PolityPolicyUpdate | 2026-08-21 | 0 |
| GitlabForDevOpsRepoForNotes | 2026-08-21 | 0 |
| AnsibleForDevOpsRepoForNotes | 2026-08-21 | 0 |
| PowershellScriptingForDevOpsRepoForNotes | 2026-08-21 | 0 |
| ShellScriptingForDevOpsRepoForNotes | 2026-08-21 | 0 |
[Latest raw snapshot](data/latest.json) and [Historical snapshots](data/history)
[Latest raw snapshot](data/latest.json) ?? [Historical snapshots](data/history)

<!-- METRICS:END -->

## Live Account Signals

<p>
	<a href="https://github.com/Shubhankart101?tab=repositories"><img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.github.com%2Fusers%2FShubhankart101&query=%24.public_repos&label=Public%20repositories&color=2088FF&style=for-the-badge&logo=github" alt="Public repositories"></a>
	<a href="https://github.com/Shubhankart101?tab=followers"><img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.github.com%2Fusers%2FShubhankart101&query=%24.followers&label=Followers&color=2ea44f&style=for-the-badge&logo=github" alt="Followers"></a>
	<a href="https://github.com/Shubhankart101?tab=overview"><img src="https://img.shields.io/badge/GitHub%20profile-Open-181717?style=for-the-badge&logo=github&logoColor=white" alt="Open GitHub profile"></a>
</p>

## What Is Collected

- Public repositories, followers, following, and public gists
- Aggregate public stars, forks, open issues, and repository size
- Repositories updated in the previous 30 days
- Language mix by repository primary language
- Recent public GitHub event count and recent push-event count
- A dated JSON snapshot in [data/history](data/history)

## Refresh Schedule

The dashboard refreshes daily at 02:30 UTC and can also be run manually from the [Actions tab](../../actions/workflows/daily-github-metrics.yml). Historical snapshots are retained rather than overwritten.

## Data Sources and Limits

This project uses only public GitHub REST API endpoints. Private repositories, private contributions, and private organization activity are intentionally excluded. Public-event data is a recent activity signal, not a lifetime contribution count.

## Repository Layout

```text
.github/workflows/daily-github-metrics.yml  Daily collection and README rendering
data/latest.json                             Most recent daily snapshot
data/history/YYYY-MM-DD.json                 Preserved dated snapshots
```