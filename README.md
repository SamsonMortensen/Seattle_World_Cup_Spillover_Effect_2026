# Seattle World Cup Spillover Effect
This project involves developing a thorough data pipeline and conducting detailed statistical analysis to understand how rerouting heavy freight during the Seattle World Cup can impact the economy. It's an exciting effort to uncover valuable insights and inform future decisions.

![Executive Dashboard](visuals/dashboard.png)

## Project Overview
In the summer of 2026, Seattle will host the FIFA World Cup, bringing an unprecedented surge in tourism to the city's infrastructure. This project analyzes a critical logistical vulnerability:

**What is the economic impact on residential neighborhoods if major freight highways fail during this mega-event?**

When primary supply chain routes break down, navigation algorithms (like Google Maps and Waze) automatically reroute heavy commercial trucks through residential areas—a phenomenon known as **algorithmic spillover**. This creates severe acoustic pollution, spikes municipal dispatch volumes, and impacts property values through a hypothesized **"Shadow Tax."**

This project quantifies that localized impact and deploys a predictive valuation model to help municipal authorities make data-driven logistics and infrastructure decisions.

---

## Architecture & Tech Stack
This end-to-end data pipeline integrates disparate government datasets into a cloud-ready predictive engine.

* **Data Engineering (ETL):** Python (requests, pandas, geopandas). Extracted recent 911 dispatch logs from the Seattle Open Data API, merged with King County Assessor records, WSDOT freight corridors, and FEMA climate risk scores.

* **Geospatial Processing:** Engineered a universal 10-digit Parcel Identification Number (PIN) and utilized R-Tree spatial intersections to map properties to active Heavy Freight buffers.

* **Statistical Modeling & ML:** Python (scipy, statsmodels, scikit-learn). Utilized a Welch's Two-Sample T-Test, Ordinary Least Squares (OLS) Hedonic Pricing Regression, and optimized tree-based machine learning models (Gradient Boosting, Random Forest).

* **Cloud Deployment:** Data batches were programmatically ingested into a **Supabase (PostgreSQL)** cloud database.
* **Business Intelligence:** Interactive dashboards and presentation storyboards designed in **Tableau**.

---

## Key Findings

### 1. Diagnosing Omitted Variable Bias (OVB)
Initial descriptive modeling aimed to isolate an acoustic "Shadow Tax" penalty. However, the Ordinary Least Squares (OLS) regression and subsequent scatter plot analyses revealed a classic case of **Omitted Variable Bias (OVB)**. The anticipated penalty from algorithmic spillover was mathematically offset by the premium buyers pay to live in dense, amenity-rich urban centers.

![Shadow Tax Scatter Plot](visuals/scatter_plot.png)

### 2. Geospatial Impact & Municipal Waste

While home prices were shielded by the density premium, the spatial intersection proved a massive drain on municipal resources. Rerouted commercial traffic triggered significant spikes in non-emergency dispatches across specific logistical chokepoints.

![Acoustic Urbanism Heatmap](visuals/spatial_map.png)

### 3. Predictive Machine Learning

A machine learning pipeline was constructed to forecast home values using strictly structural and environmental features. The **Gradient Boosting Regressor** outperformed other models (with 300 estimators and a max depth of 5 to handle right-skewed pricing distributions), demonstrating that environmental profiles alone have significant predictive power for baseline property equity.

---

## Interactive Deliverables

**1. The Tableau Dashboard**

For a deep dive into the data, an interactive Tableau Packaged Workbook is included in this repository.

* Download `RoaSCC_v2025.3.twbx` from the repository files.

* Open it using the free [Tableau Reader](https://www.tableau.com/products/reader) to explore the spatial heatmaps and statistical distributions locally.

**2. The Python Pipeline**

* **`code/data_engineering.ipynb`**: Contains the API extractions, string manipulation for a universal PIN generation, and GeoPandas spatial joins.

* **`code/statistical_modeling.ipynb`**: Contains the baseline variance testing, OLS regression, OVB diagnosis, and the Gradient Boosting machine learning architecture.


## References
The academic research, spatial econometrics methodologies, and municipal data sources used to formulate the analytical approach and baseline features can be found in the [Project References](docs/references.pdf) document.

## Data Sources

The raw inputs total roughly 1.9 GB, so they are not committed here. Both notebooks
read and write **relative to their working directory** — put every file listed below
in the directory you launch Jupyter from, then run `code/data_engineering.ipynb`
first and `code/statistical_modeling.ipynb` second.

| File | Source | Notes |
| --- | --- | --- |
| `rp_sale.csv` | [King County Assessor — Data Download](https://info.kingcounty.gov/assessor/DataDownload/default.aspx), table `EXTR_RPSale` | Columns used: `Major`, `Minor`, `SalePrice`, `DocumentDate`. Read with `encoding='latin1'`. |
| `residential.csv` | King County Assessor, table `EXTR_ResBldg` | Columns used: `Major`, `Minor`, `SqFtTotLiving`, `NbrLivingUnits`, `YrBuilt`. |
| `parcel.csv` | King County Assessor, table `EXTR_Parcel` | Columns used: `Major`, `Minor`, `CurrentZoning`. |
| `coords.csv` | [King County GIS Open Data — Address Points](https://gis-kingcounty.opendata.arcgis.com/) | E911 site-address points. Columns used: `PIN`, `LAT`, `LON`, `x`, `y`. Coordinates are King County State Plane (EPSG:2285); the notebooks reproject to EPSG:4326. |
| `seattle_police_beats.geojson` | [Seattle GeoData — SPD Beats](https://data.seattle.gov/) | Polygon boundaries. Join key `beat`. |
| Seattle 911 dispatch log | [Seattle Open Data, dataset `33kz-ixgy`](https://data.seattle.gov/resource/33kz-ixgy.json) | Pulled live by `data_engineering.ipynb`. **See the reproducibility note below.** |
| `wsdot.csv` | Attribute export of the WSDOT FGTS truck-corridor layer | Used only by the statewide Welch's t-test. Columns used: `FGTSClass`, `CountyName`. |
| `wsdot_freight_corridors.geojson` | [WSDOT FGTS — Truck Corridors (ArcGIS REST)](https://data.wsdot.wa.gov/arcgis/rest/services/Shared/FreightSystemData/MapServer/0) | Geometry for the freight spatial join. Run `python code/fetch_wsdot_freight.py` to download it. |
| `nri.csv` | [FEMA National Risk Index — Data Resources](https://hazards.fema.gov/nri/data-resources) | County-level NRI table. Columns used: `STATE`, `COUNTY`, `RISK_SCORE`. |

### `wsdot_freight_corridors.geojson`

This file defines `Heavy_Freight_Zone`, the model's only infrastructural control, and
its absence is what caused commit `b33fa92` to substitute a hardcoded list of police
beats. Fetch it with:

```bash
python code/fetch_wsdot_freight.py
```

Expected schema: a `FeatureCollection` of `LineString` features in CRS84, with the
FGTS attributes on each feature. The notebook uses `FGTSClass` only, filtering to the
heavy-freight classes `T-1` and `T-2`, reprojecting to EPSG:2285 so distances are in
feet, and buffering 1,000 ft.

The committed results were produced against the FGTS publication dated `2021-12-31`
(33,550 features; 334 `T-1` and 720 `T-2` segments). WSDOT republishes the FGTS every
two years, and the current publication reclassifies considerably more mileage as heavy
freight (612 `T-1`, 1,508 `T-2`). In practice this barely moves the analysis — both
vintages flag 25.9% of the modeled parcels and leave the freight coefficient
insignificant — but the fetch script prints a warning when the layer it downloads does
not match the vintage behind the committed numbers.

### Reproducibility note: the 911 pull is a moving window

`data_engineering.ipynb` requests the 50,000 most recent dispatch records
(`$order=cad_event_original_time_queued DESC`), so **it returns different data every
time it runs** and `total_noise_dispatches` is not stable across runs. This is the
mechanism behind the drift this repository has already experienced once.

The snapshot backing the committed CSVs and figures is checked in under
`data/Seattle_Noise_Dispatch_Log.csv` and `data/Seattle_Beat_Financial_Waste.csv`. To
reproduce the committed numbers exactly, copy those two files into your working
directory and skip the API cell; to refresh the analysis, run the API cell and accept
that every downstream figure will move.
