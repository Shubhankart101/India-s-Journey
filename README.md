# PolityPolicy Daily Update Dashboard

A daily public-data monitor for [India, in Numbers](https://politypolicy.com/). This project inventories publicly accessible stories, Pulse trackers, collections, sister sites, and visible tracker headlines. It does not collect GitHub-account metrics.

## Daily Site Dashboard

<!-- METRICS:START -->

> Last refreshed: **2026-08-21T14:28:05+00:00**

> Collection status: **partial_or_blocked**
> Collector notes: HTTP 403: Forbidden; HTTP 403: Forbidden

| Public site signal | Count |
| --- | ---: |
| Pulse trackers | 0 |
| Interactive/latest story pages | 0 |
| Collections/categories | 0 |
| Sister sites | 0 |

### Pulse Tracker Headlines

| Tracker | HTTP status | Visible headline snippet |
| --- | ---: | --- |
| No trackers detected | - | - |

### Latest Public Story Links

| Page |
| --- |
| No story links detected |

[Latest raw snapshot](data/latest.json) and [Historical snapshots](data/history)

<!-- METRICS:END -->

## Weekly Polity and Policy Articles

Published articles from the public [Polity and Policy by Tushar Gupta](https://politypolicy.substack.com/) RSS feed.

<!-- SUBSTACK:START -->

> Last refreshed: **2026-08-21T14:31:57+00:00**
> Feed build date: **Fri, 21 Aug 2026 14:30:00 GMT**

| Article | Published | Summary |
| --- | --- | --- |
| [India's Fiscal Nightmare: The Strait of Hormuz](https://politypolicy.substack.com/p/indias-fiscal-nightmare-the-strait) | 2026-07-15 | How the war in the Persian Gulf costs you and the country at large |
| [What if International Crude Prices Dictated Petrol Pump Prices?](https://politypolicy.substack.com/p/what-if-international-crude-prices) | 2026-07-10 | Be careful what you wish for. |
| [Petrol And Pizza, Crude and Capsicum](https://politypolicy.substack.com/p/petrol-and-pizza-crude-and-capsicum) | 2026-07-09 | The economics and environmentalism around ethanol bashing don’t add up. |
| [Why Is The Prime Minister Travelling To Indonesia and Australia](https://politypolicy.substack.com/p/why-is-the-prime-minister-travelling) | 2026-07-08 | Another chapter unfolds in our pursuit of chip diplomacy |
| [The Markets Are Sending Us A Message About Ethanol](https://politypolicy.substack.com/p/the-markets-are-sending-us-a-message) | 2026-07-07 | Beyond the social media rhetoric, what is the invisible hand of the free market hinting at? |
| [Welcome to PolityPolicy.Com](https://politypolicy.substack.com/p/announcement-welcome-to-politypolicycom) | 2026-07-07 | A New Beginning |
| [India's Worst Balance Sheet](https://politypolicy.substack.com/p/indias-worst-balance-sheet) | 2026-07-03 | When subsidies are confused for good economics, the fiscal fundamentals crumble |
| [The Monk Who Runs State Finances Like a Ferrari](https://politypolicy.substack.com/p/the-monk-who-runs-state-finances) | 2026-07-01 | Chief Minister Yogi Adityanath's Fiscal Report Card After A Decade In Power |
| [The Brutal Reality About 'The Gujarat Model'](https://politypolicy.substack.com/p/the-brutal-reality-about-the-gujarat) | 2026-06-29 | When we compared Gujarat's fiscal with that of every other state in India. |
| [State Governments Are Borrowing, Not to Build, But to Breathe](https://politypolicy.substack.com/p/state-governments-are-borrowing-not) | 2026-06-26 | Fiscally, many state governments are on a ventilator, making ends meet through borrowings |
| [Why Should Politicians and Bureaucrats Have All the Fun?](https://politypolicy.substack.com/p/why-should-politicians-and-bureaucrats) | 2026-06-25 | Time for a new law for the declaration of real estate and stock market holdings? |
| [Why State Governments Have No Money For Asset Creation?](https://politypolicy.substack.com/p/why-state-governments-cash-transfers) | 2026-06-24 | Strip away the cash-transfer noise, and four heads quietly run India's state budgets |

[Latest article snapshot](data/substack-latest.json) and [Weekly article history](data/substack-history)

<!-- SUBSTACK:END -->

## What Is Collected

- Public Pulse tracker pages and their current visible headline snippets
- Latest and interactive-story links visible from the homepage
- Public category and collection links
- Sister-site links visible from the homepage
- Page title, source URL, HTTP status, and collection timestamp for each tracker
- Recent public article metadata from the Polity and Policy Substack RSS feed
- A dated JSON snapshot in [data/history](data/history)

## Refresh Schedule

The dashboard refreshes daily at 02:30 UTC and can also be run manually from the [Actions tab](../../actions/workflows/daily-politypolicy-update.yml). Historical snapshots are retained rather than overwritten.

Substack articles refresh weekly on Friday at 03:00 UTC through the [Weekly Substack Article Update](../../actions/workflows/weekly-substack-articles.yml) workflow.

## Scope and Data Ethics

The monitor only reads public HTML exposed by `politypolicy.com` and records a compact index of visible site metadata and headline text. It does not bypass access controls, copy complete underlying datasets, or present itself as an official source. Use the links in each snapshot to reach the original PolityPolicy visualization and its cited official source.

## Repository Layout

```text
.github/workflows/daily-politypolicy-update.yml  Daily public-site collection
.github/workflows/weekly-substack-articles.yml   Weekly Substack RSS collection
data/latest.json                                  Most recent site snapshot
data/history/YYYY-MM-DD.json                      Preserved dated snapshots
```
