# Tourism and World Heritage indicators

The **Tourism & Heritage** group has two independent subgroups: **International Visitor Trends** and **World Heritage Sites**. It places official source records beside their limits rather than treating visitors, receipts and inscription counts as one continuous measure.

## International Visitor Trends

Three World Bank annual indicators are collected for India:

| Indicator | World Bank code | Unit | Interpretation |
| --- | --- | --- | --- |
| International tourist arrivals | `ST.INT.ARVL` | Arrivals | International inbound tourism, as reported in the WDI source |
| International tourist departures | `ST.INT.DPRT` | Departures | International outbound tourism |
| International tourism receipts | `ST.INT.RCPT.CD` | Current US dollars | Nominal receipts; not inflation-adjusted |

Source pages: [arrivals](https://data.worldbank.org/indicator/ST.INT.ARVL?locations=IN), [departures](https://data.worldbank.org/indicator/ST.INT.DPRT?locations=IN), and [receipts](https://data.worldbank.org/indicator/ST.INT.RCPT.CD?locations=IN).

These are national annual observations, not a daily travel feed, domestic-tourism count, State-wise visitor series, monument attendance count, or measure of resident welfare. The World Bank series may be revised and the latest published year can differ by indicator.

## World Heritage Sites

The daily public-chart pipeline reads India-listed properties from the [official UNESCO World Heritage List](https://whc.unesco.org/en/list/), opens each property's official page, and reads its published inscription date and current category. The checked-in snapshot contains 45 currently listed properties (37 cultural, 7 natural and 1 mixed), and produces:

- an annual count of properties by inscription year;
- a cumulative count reconstructed from those inscription years; and
- current counts by cultural, natural and mixed category.

These are derived from today's list, not a frozen historical snapshot from every past year. The cumulative series can therefore change if UNESCO revises a property's date, boundary, name or classification. A site's inscription year does not establish the date it became a monument, the number of tourists it receives, or the economic impact of tourism.

No official machine-readable national dataset of annual visits to each monument or State-level tourist arrivals was verified for this collection. The project does not fill those gaps with unofficial travel websites or generated estimates.

## Refresh and reproducibility

Tourism observations are refreshed by `scripts/generate_public_charts.py` during the daily chart workflow. UNESCO collection uses public HTML pages, the Python standard library, and a short delay between property requests. A failed refresh reuses the last cached UNESCO values where available; it does not invent new observations.

See [pipeline documentation](PIPELINES.md) and the [source and limitation register](SOURCES-AND-LIMITATIONS.md).
