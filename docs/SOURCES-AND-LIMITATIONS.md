# Sources, cadence, and limitations

## Essential services and population

The dashboard includes World Bank annual national series for electricity access, basic drinking-water access, basic sanitation, clean cooking fuel access, fertility, crude birth and death rates, population, primary/secondary/tertiary enrollment, and other indicators. World Bank series are annual estimates and may be revised; they are not daily administrative counts. Clean cooking access is not a direct count of LPG connections or gas network coverage.

Some state comparisons use RBI publications, Jal Jeevan Mission reporting, and other cited portals. They are snapshots where the source publishes one comparable year, not annual histories. A state metric is not described as complete coverage unless its generated dataset contains every expected State observation.

State-wise birth and death counts and a comparable annual state TFR series are not included. SRS and Civil Registration System publications have different reference periods, availability, and definitions. A state series must be assembled from published tables before it can be plotted; national annual fertility estimates are not a substitute for state observations.

## Fuel prices and energy

The fuel-consumption series measures activity/volume, not retail prices. The Indian crude basket price is a distinct crude-price measure, not a petrol/diesel pump price. PPAC's retail selling price archive and oil-marketing-company pages did not yield a verified, openly downloadable daily retail-price table for automated collection. No daily Indian retail prices are estimated or copied from unofficial aggregators.

## Elections

See [Election data coverage](ELECTIONS.md) for ECI provisional status, the partial historical workbook archive, SSR/SIR gaps, the U.S. Electoral College measure, and House coverage limitations.

The ECI archive currently supplies candidate-level workbook observations for selected State Assembly elections. It does not establish complete historic coverage, and unsupported PDF layouts remain absent. The dataset and explorer expose only parsed observations and their original report links.

## Tourism and World Heritage

International tourism arrival, departure, and receipt series use World Bank indicators (`ST.INT.ARVL`, `ST.INT.DPRT`, `ST.INT.RCPT.CD`). Coverage is annual and latest years differ; receipts are nominal current US dollars. These series do not describe domestic travel or visits to specific destinations.

UNESCO property counts are reconstructed from current World Heritage List pages and inscription dates, not from archived snapshots of the list. The result is a count of currently listed properties by inscription year, not visitor attendance or tourism revenue. State-wise tourism and monument-level annual visitation are not presented without a comparable source.

## Interpreting frequency

Refresh schedules describe how often a pipeline checks a source, not how often the source publishes new observations. A three-hourly election-page check may return unchanged counts; annual estimates remain annual even if an API is queried daily.

Interpret each chart alongside its displayed source, unit, frequency, note, and observation period. Missing or inaccessible source values are not interpolated or represented as zero.
