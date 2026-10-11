import pandas as pd, json, sys
sys.path.insert(0,'../..')
# Source: Abgeordnetenhaus Berlin Drucksache 18/10900 (answer 25.04.2017), Q1 2017 monthly counts
q1 = {
 "Charlottenburg-Wilmersdorf": {"Internet":[174,217,365],"Mobile App":[331,387,424]},
 "Friedrichshain-Kreuzberg":   {"Internet":[754,894,852],"Mobile App":[319,524,573]},
 "Lichtenberg":                {"Internet":[142,203,290],"Mobile App":[326,328,437]},
 "Marzahn-Hellersdorf":        {"Internet":[97,99,128],  "Mobile App":[140,141,178]},
 "Mitte":                      {"Internet":[655,820,970],"Mobile App":[524,586,817]},
 "Neukölln":                   {"Internet":[543,513,673],"Mobile App":[743,933,1069]},
 "Pankow":                     {"Internet":[265,226,319],"Mobile App":[614,548,763]},
 "Reinickendorf":              {"Internet":[113,111,142],"Mobile App":[224,222,343]},
 "Spandau":                    {"Internet":[91,66,108],  "Mobile App":[236,202,229]},
 "Tempelhof-Schöneberg":       {"Internet":[381,392,436],"Mobile App":[237,274,439]},
 "Treptow-Köpenick":           {"Internet":[113,133,162],"Mobile App":[293,397,382]},
}
stated_totals={"Charlottenburg-Wilmersdorf":{"Internet":365}}
# Source: Drucksache 18/28582 Anlage 1, registered residents 31.12.2016
pop = {"Mitte":371407,"Friedrichshain-Kreuzberg":281323,"Pankow":397406,"Charlottenburg-Wilmersdorf":336249,
 "Spandau":239942,"Steglitz-Zehlendorf":304086,"Tempelhof-Schöneberg":346108,"Neukölln":327522,
 "Treptow-Köpenick":259524,"Marzahn-Hellersdorf":262015,"Lichtenberg":283121,"Reinickendorf":261919}
assert sum(pop.values())==3670622
rows=[];rid=0
for d,ch in q1.items():
  for c,months in ch.items():
    for m,n in enumerate(months,1):
      for _ in range(n):
        rows.append({"report_id":rid,"district":d,"channel":c,"reported_at":f"2017-{m:02d}-15T00:00:00"}); rid+=1
df=pd.DataFrame(rows); df.to_csv("berlin_ordnungsamt_q1_2017.csv",index=False)
ref={"district":{k:v/sum(pop.values()) for k,v in pop.items()}}
json.dump(ref,open("reference_population_2016.json","w"),ensure_ascii=False,indent=1)
json.dump({"title":"Berlin Ordnungsamt-Online reports by district, Q1 2017","description":"Record-level expansion of official monthly counts, Drucksache 18/10900","columns":{"district":"Bezirk","channel":"Internet or Mobile App","reported_at":"month of report"}},open("meta.json","w"))
from civicqa import CivicQAAuditor
for label,cfg in [("entropy",{}),("reference",{"reference_distribution":ref})]:
  r=CivicQAAuditor().audit(df,dataset_name="berlin_q1_2017",config={"protected_columns":["district"],**cfg})
  print("=== mode:",label); print(r.to_markdown())
sh=df.district.value_counts(normalize=True)
t=pd.DataFrame({"report_share":sh,"pop_share":pd.Series(ref["district"])}).fillna(0)
t["ratio"]=t.report_share/t.pop_share; print((t.sort_values("ratio")*1).round(3)); print("N",len(df))
