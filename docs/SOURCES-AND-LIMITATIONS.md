# Sources, cadence, and limitations

## Essential services and population

The dashboard includes World Bank annual national series for electricity access, basic drinking-water access, basic sanitation, clean cooking fuel access, fertility, crude birth and death rates, population, primary/secondary/tertiary enrollment, and other indicators. World Bank series are annual estimates and may be revised; they are not daily administrative counts. Clean cooking access is not a direct count of LPG connections or gas network coverage.

Some state comparisons use RBI publications, Jal Jeevan Mission reporting, and other cited portals. They are snapshots where the source publishes one comparable year, not annual histories. A state metric is not described as complete coverage unless its generated dataset contains every expected State observation.

State-wise birth and death counts and a comparable annual state TFR series are not included. SRS and Civil Registration System publications have different reference periods, availability, and definitions. A state series must be assembled from published tables before it can be plotted; national annual fertility estimates are not a substitute for state observations.

## Fuel prices and energy

The fuel-consumption series measures activity/volume, not retail prices. The Indian crude basket price is a distinct crude-price measure, not a petrol/diesel pump price. PPAC's retail selling price archive and oil-marketing-company pages did not yield a verified, openly downloadable daily retail-price table for automated collection. No daily Indian retail prices are estimated or copied from unofficial aggregators.

## Elections

See [Election data coverage](ELECTIONS.md) for ECI provisional status, the U.S. Electoral College measure, and historical / House coverage gaps.

## Interpreting frequency

Refresh schedules describe how often a pipeline checks a source, not how often the source publishes new observations. A three-hourly election-page check may return unchanged counts; annual estimates remain annual even if an API is queried daily.

Interpret each chart alongside its displayed source, unit, frequency, note, and observation period. Missing or inaccessible source values are not interpolated or represented as zero.
