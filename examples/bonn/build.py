"""Case study C — Bonn Mängelmelder archive (anliegen.bonn.de), Jan 2018 – Feb 2020.
Reproduces the Stadtbezirk representativeness analysis end to end.

Inputs (all open data, CC0, Stadt Bonn):
  anliegen-bonn_de-2018-export.csv     Mängelmelder archive (opendata.bonn.de)
  stadtbezirke_bonn.geojson            Flächen der Stadtbezirke (opendata.bonn.de)
  reference_stadtbezirk_2018.json      Residents per Stadtbezirk, 31.12.2018
                                              (Statistikstelle Bonn, Statistik aktuell Feb 2021, Tab. 8)
Usage:  cd examples/bonn && python build.py   (requires pandas, shapely; run from repo root with PYTHONPATH=.)
"""
import json
import pandas as pd
from shapely.geometry import shape, Point
from civicqa import CivicQAAuditor

df = pd.read_csv('anliegen-bonn_de-2018-export.csv', sep=';', encoding='latin-1')
df.columns = ['uuid', 'date_raw', 'category_raw', 'location_raw']
m = df['location_raw'].str.extract(r'Geolocation is\s*([-\d\.]+)\s*,\s*([-\d\.]+)')
df['lat'] = pd.to_numeric(m[0])
df['lon'] = pd.to_numeric(m[1])
df['reported_at'] = pd.to_datetime(df['date_raw'].str.replace(' - ', ' '), format='%d.%m.%Y %H:%M')
n_raw = len(df)
df = df.drop_duplicates(subset=['uuid', 'date_raw', 'category_raw', 'location_raw']).copy()
n_dedup = len(df)

g = json.load(open('stadtbezirke_bonn.geojson', encoding='utf-8', errors='replace'))
polys = {f['properties']['bezirk_bez']: shape(f['geometry']) for f in g['features']}


def assign(r):
    p = Point(r.lon, r.lat)
    for k, v in polys.items():
        if v.contains(p) or v.touches(p):
            return k
    return 'UNASSIGNED'


df['stadtbezirk'] = df.apply(assign, axis=1)
n_unassigned = int((df.stadtbezirk == 'UNASSIGNED').sum())
df = df[df.stadtbezirk != 'UNASSIGNED']

ref = json.load(open('reference_stadtbezirk_2018.json'))['reference_distribution']
data = df[['uuid', 'reported_at', 'category_raw', 'lat', 'lon', 'stadtbezirk']]
meta = {'title': 'Bonn Mängelmelder archive 2018–Feb 2020',
        'description': 'anliegen.bonn.de citizen reports, open data CC0',
        'columns': {c: c for c in data.columns}}

ent = CivicQAAuditor().audit(data, dataset_name='bonn_maengelmelder',
                             config={'metadata': meta, 'protected_columns': ['stadtbezirk']})
par = CivicQAAuditor().audit(data, dataset_name='bonn_maengelmelder',
                             config={'metadata': meta, 'protected_columns': ['stadtbezirk'],
                                     'reference_distribution': ref, 'flag_ratio': 0.8})
ent.to_json('audit_bonn_entropy.json')
par.to_json('audit_bonn_reference.json')
open('audit_bonn_entropy.md', 'w').write(ent.to_markdown())
open('audit_bonn_reference.md', 'w').write(par.to_markdown())

obs = df.stadtbezirk.value_counts()
N = int(obs.sum())
rows = [(k, int(obs.get(k, 0)), round(100 * obs.get(k, 0) / N, 1),
         round(100 * ref['stadtbezirk'][k], 1),
         round((obs.get(k, 0) / N) / ref['stadtbezirk'][k], 2)) for k in ref['stadtbezirk']]
t = pd.DataFrame(rows, columns=['stadtbezirk', 'reports', 'observed_%', 'expected_%', 'obs_over_exp'])
t.to_csv('bonn_stadtbezirk_table.csv', index=False)

print(f'raw rows {n_raw} | after exact-duplicate removal {n_dedup} | '
      f'unassigned (outside all polygons) {n_unassigned} | analysed {N}')
print(t.to_string(index=False))
