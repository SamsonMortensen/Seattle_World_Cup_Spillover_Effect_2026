"""Download wsdot_freight_corridors.geojson from the WSDOT ArcGIS REST service.

The statewide FGTS truck-corridor layer is ~58 MB, so it is not committed to this
repository. `statistical_modeling.ipynb` will not run without it -- run this
script once, from the directory the notebook runs in, to fetch it.

    python code/fetch_wsdot_freight.py

Source
------
WSDOT Rail, Freight and Ports Division
"Freight and Goods Transportation System - Truck Corridors"
https://data.wsdot.wa.gov/arcgis/rest/services/Shared/FreightSystemData/MapServer/0

WSDOT republishes the FGTS every two years, so the feature count and the
PublishDate on each record will drift over time. The counts recorded under
EXPECTED below describe the vintage used for the committed results; a mismatch
is not an error, but it does mean the numbers in the notebook will not reproduce
exactly.
"""
import json
import sys
import time

import requests

LAYER = ("https://data.wsdot.wa.gov/arcgis/rest/services/"
         "Shared/FreightSystemData/MapServer/0")
OUT = "wsdot_freight_corridors.geojson"
PAGE = 1000  # the service's maxRecordCount

# Vintage backing the committed results (2021-12-31 PublishDate).
EXPECTED = {"features": 33550, "T-1": 334, "T-2": 720}


def fetch_all():
    session = requests.Session()
    features = []
    offset = 0
    while True:
        params = {
            "where": "1=1",
            "outFields": "*",
            "outSR": 4326,
            "f": "geojson",
            "resultOffset": offset,
            "resultRecordCount": PAGE,
        }
        r = session.get(LAYER + "/query", params=params, timeout=120)
        r.raise_for_status()
        page = r.json()
        if "error" in page:
            raise RuntimeError(page["error"])
        batch = page.get("features", [])
        if not batch:
            break
        features.extend(batch)
        offset += len(batch)
        print(f"  {offset:>6} features", flush=True)
        if not page.get("properties", {}).get("exceededTransferLimit") and len(batch) < PAGE:
            break
        time.sleep(0.2)
    return features


def main():
    print(f"Downloading FGTS truck corridors from {LAYER}")
    features = fetch_all()

    doc = {
        "type": "FeatureCollection",
        "name": "Freight_and_Goods_Transportation_System_-_Truck_Corridors",
        "crs": {"type": "name",
                "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": features,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh)

    classes = {}
    for f in features:
        c = (f.get("properties") or {}).get("FGTSClass")
        classes[c] = classes.get(c, 0) + 1

    print(f"\nWrote {OUT}: {len(features):,} features")
    print("FGTSClass breakdown:", dict(sorted(classes.items(), key=lambda kv: -kv[1])))
    print(f"Expected vintage:    {EXPECTED}")

    drift = [k for k, v in (("T-1", classes.get("T-1")), ("T-2", classes.get("T-2")))
             if v != EXPECTED[k]]
    if len(features) != EXPECTED["features"] or drift:
        print("\nNOTE: this is a different FGTS publication than the one behind the "
              "committed results. The notebook will run, but the freight flag -- and "
              "therefore the model output -- will differ.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
