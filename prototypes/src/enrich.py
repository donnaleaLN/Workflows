import csv, sys, json, re, collections, datetime as dt
src, out = sys.argv[1], sys.argv[2]
rows = list(csv.DictReader(open(src)))
TODAY = dt.date(2026, 11, 12)

THEMES = [  # (id, label, regex) – order = priority for primary theme
 ("nuclear","Nuclear", r"nuclear|uranium|enrichment|reactor|nuscale|loviisa|millstone|eddystone"),
 ("geothermal","Geothermal", r"geothermal|fervo|cape station"),
 ("lng","LNG & gas", r"\blng\b|natural gas|gas pipeline|gas supply|gas generation|gas cap|midstream|gas portfolio|gas transport|fuel cell|methanol"),
 ("oil","Oil & refining", r"crude|\boil\b|refin|diesel|petroleum|barrel|fuel price|oilfield|oil-field|shale|tanker|acres"),
 ("minerals","Critical minerals", r"lithium|spodumene|nickel|alumin|vanadium|gold refiner|alunorte|speewah|mine\b|minerals"),
 ("renew","Solar & wind", r"solar|wind|photovoltaic|renewable|clean energy|clean-energy|green energy|carbon removal|methane-reducing"),
 ("grid","Grid, storage & utilities", r"grid|battery|storage|transmission|base rates|utility|power plant|turbine|dispatch|interconnection|power infrastructure|power facility"),
]
AI = r"google|alphabet|amazon|microsoft|\bmeta\b|oracle|data cent|hyperscal|equinix|\bqts\b|nvidia|frontier ai|ai operations|super intelligence|salesforce|\bsap se\b"

REG_TYPES = {"Product Regulatory Action","M&A Regulatory Intervention","Sanctions Designation","Sanctions Breach / Enforcement","Abuse of Dominance","Cartel / Price-Fixing","Pollution / Environmental Violation"}
GEO_TYPES = {"Sanctions Exposure","Geographic Exit","Conflict Minerals / Sourcing Violation","Operational Disruption / Business Continuity Failure"}
GEO_PLACES = {"russia","iran","venezuela","middle east","cuba","falklands","falkland islands","ukraine","israel","red sea","strait of hormuz"}

DECISIONS = {
 "screen":"Counterparty & sanctions screening",
 "supply":"Supply & sourcing strategy",
 "offtake":"Power offtake & pricing",
 "capital":"Investment & capital allocation",
 "expand":"Market entry & expansion",
 "comply":"Regulatory & compliance planning",
 "watch":"Partner & competitor watch",
}
def decision(r, text):
    t, c = r["event_type"], r["event_category"]
    if c == "Financial Crime" or t.startswith("Sanctions") or "Conflict Minerals" in t: return "screen"
    if t in {"Product Regulatory Action","M&A Regulatory Intervention","Abuse of Dominance","Cartel / Price-Fixing","Pollution / Environmental Violation"}: return "comply"
    if t in {"Operational Disruption / Business Continuity Failure","Channel / GTM Strategy Shift","Geographic Exit"}: return "supply"
    if re.search(r"supply (agreement|partnership|deal)|offtake|sourcing|spodumene|lithium", text) and not re.search(r"power purchase|ppa", text): return "supply"
    if t in {"Major Customer Win","Exclusive Alliance","Pricing Strategy Change"} or re.search(r"power purchase|\bppa\b|vppa|power agreement|power supply", text): return "offtake"
    if t in {"Geographic Expansion","Market Entry (Vertical or Segment)","Upmarket Expansion","Strategic Repositioning","Standalone-to-Integration Shift"}: return "expand"
    if c in {"Financial Performance","M&A & Ownership Activity"} or t in {"CapEx Update","Divestiture","Joint Venture Formation / Dissolution","Capital Allocation Reorientation","R&D Spend Update","Cost Savings Program Announced"}: return "capital"
    return "watch"

THREADS = [
 ("russia","Russia sanctions fallout for refiners & LNG", r"nayara|rosneft|indian refiners|oil india|russian diesel|russian energy giant|arctic lng|mesabi|essar|novatek"),
 ("iran","Iran oil sanctions-evasion network", r"\biran"),
 ("crude","Middle East disruption reshapes crude sourcing", r"crude sourcing|crude imports|middle east crude|indian oil|iocl|\bioc\b|reliance|crude oil supply|mauritius"),
 ("venezuela","Venezuela reopens to Western energy", r"venezuela"),
 ("alunorte","Alunorte gas outage hits Norsk Hydro", r"alunorte|norsk hydro"),
 ("geo","Geothermal goes commercial with Big Tech", r"fervo|geothermal"),
 ("nuclearai","Hyperscalers lock in firm nuclear power", r"nuclear|uranium|enrichment|reactor"),
 ("pushback","Regulators push back on power & fuel pricing", r"base rates|commission denies|price cap|gas cap|price-fixing|emergency order|approves baker hughes|light and noise"),
 ("lng","LNG export capacity race", r"\blng\b|gas pipeline|natural gas transport"),
 ("metals","Battery-metal supply lock-ins", r"lithium|spodumene|nickel|speewah|vanadium|gold refiner"),
 ("ppa","Big Tech's clean-power buying spree", AI),
]
THREAD_BLURB = {
 "russia":"EU and US measures on Rosneft-linked assets are pushing service providers, refiners and LNG partners to cut ties, and courts are starting to push back.",
 "iran":"Enforcement keeps widening from Chinese teapot refiners to banks, payment rails and tanker servicers.",
 "crude":"Indian refiners are replacing Middle East barrels with spot cargoes from West Africa, Latin America and Europe.",
 "venezuela":"Licences are drawing US majors, oil-field services and commodity traders back into Venezuela.",
 "alunorte":"A gas supply failure at the Alunorte refinery has moved from an operating problem to a guidance cut.",
 "geo":"Fervo's Google deal has grown from one PPA to an expandable 1 GW programme in ten weeks.",
 "nuclearai":"Hyperscalers are signing 20-year deals for existing nuclear output and funding uprates, led by Constellation.",
 "pushback":"Utility commissions, courts and antitrust complainants are challenging how power and fuel are priced.",
 "lng":"New export capacity and long-term offtakes are being signed across North America, the Gulf and Asia.",
 "metals":"Battery makers and traders are locking in multi-year lithium and spodumene supply; sanctions are shutting other mines.",
 "ppa":"Google, Amazon, Microsoft, Meta and Oracle are signing long-dated solar and wind PPAs across four continents.",
}

def parse(s):
    try: return json.loads(s) if s else None
    except Exception: return None

events=[]; kg=collections.defaultdict(lambda: {"names":set(),"events":set(),"type":None})
for r in rows:
    ents = parse(r["entities"]) or []
    ent_text = " ".join(e["name"] for e in ents)
    text = (r["short_description"]+" "+r["description"]+" "+ent_text).lower()
    themes=[tid for tid,_,rx in THEMES if re.search(rx,text)]
    if re.search(AI,text): themes.insert(0,"ai")
    if not themes: themes=["grid"]
    places = {e["name"].lower() for e in ents if e["entity_type"] in ("location","government")}
    drivers=[]
    if r["event_type"] in REG_TYPES or re.search(r"regulator|commission|court|emergency order|base rates", text): drivers.append("regulatory")
    if r["event_type"] in GEO_TYPES or places & GEO_PLACES or re.search(r"sanction|geopolit", text): drivers.append("geopolitical")
    if not drivers or r["event_category"] not in ("Financial Crime",) and r["event_type"] not in REG_TYPES|GEO_TYPES: 
        if r["event_category"] in ("Strategic Moves","Business Operations & Commercial Activity","Financial Performance","M&A & Ownership Activity","Product Events","People & Leadership") or not drivers:
            drivers.append("market")
    # primary driver
    if r["event_type"] in REG_TYPES: primary="regulatory"
    elif r["event_type"] in GEO_TYPES or r["event_category"]=="Financial Crime": primary="geopolitical"
    else: primary = "market" if "market" in drivers else drivers[0]
    if primary not in drivers: drivers.insert(0,primary)
    why=[]
    if r["event_type"] in REG_TYPES: why.append("event type '%s' is a regulatory action"%r["event_type"])
    m=re.search(r"regulator|commission|court|emergency order|base rates", text)
    if m: why.append("names a regulator or court ('%s')"%m.group(0))
    if r["event_type"] in GEO_TYPES: why.append("event type '%s' is a geopolitical exposure"%r["event_type"])
    gp=sorted(places & GEO_PLACES)
    if gp: why.append("involves %s"%", ".join(p.title() for p in gp))
    if "market" in drivers: why.append("category '%s' signals a market or competitor move"%r["event_category"])
    thread=None
    for tid,_,rx in THREADS:
        if re.search(rx,text): thread=tid; break
    subj=[e for e in ents if e["role"]=="Subject"]
    company_subj=[e for e in subj if e["entity_type"]=="company" and e["entity_pguid"]]
    generic = bool(subj) and all(re.search(r"companies|refiners|firms|producers|entities|exporters|operators", e["name"], re.I) for e in subj)
    market_level = (not any(e["entity_type"]=="company" and e["role"]=="Subject" for e in ents)) or generic
    for e in ents:
        if e["entity_type"] not in ("company","organization","government"): continue
        key = e["entity_pguid"] or ("unresolved:"+e["name"])
        kg[key]["names"].add(e["name"]); kg[key]["events"].add(r["event_id"]); kg[key]["type"]=e["entity_type"]
    tmp=parse(r["temporal"]) or {}
    rel=parse(r["related_articles"]) or []
    events.append({
      "id":r["event_id"], "art":r["article_id"], "rel":rel, "pub":r["publication_date"],
      "cat":r["event_category"], "type":r["event_type"], "head":r["short_description"], "desc":r["description"],
      "dir":r["impact_direction"], "dirC":float(r["impact_direction_confidence"] or 0),
      "mag":r["impact_magnitude"], "magC":float(r["impact_magnitude_confidence"] or 0),
      "status":r["signal_status"], "tStart":r["temporal_start_date"], "tEnd":r["temporal_end_date"],
      "tPrec":tmp.get("precision"), "tRaw":tmp.get("raw_text"),
      "ents":[{"n":e["name"],"t":e["entity_type"],"r":e["role"],"c":e["confidence"],"x":e.get("context"),"kg":e["entity_pguid"]} for e in ents],
      "themes":list(dict.fromkeys(themes)), "drivers":drivers, "driver":primary, "decision":decision(r,text),
      "thread":thread, "market":market_level, "why":why,
    })

# dedupe: same subject pguid + same type + similar headline within 7 days -> mark as duplicate of earlier? keep simple: count corroboration by shared article id
art_counts=collections.Counter(e["art"] for e in events)
for e in events: e["siblings"]=art_counts[e["art"]]-1

kglist=[]
for k,v in kg.items():
    kglist.append({"key":k,"names":sorted(v["names"]),"n":len(v["events"]),"resolved":not k.startswith("unresolved:"),"type":v["type"],"events":sorted(v["events"])})
kglist.sort(key=lambda x:(-x["n"],x["names"][0]))
json.dump({"today":TODAY.isoformat(),"events":events,"kg":kglist,
  "themes":[{"id":"ai","label":"AI & data-centre power"}]+[{"id":t,"label":l} for t,l,_ in THEMES],
  "threads":[{"id":t,"label":l,"blurb":THREAD_BLURB[t]} for t,l,_ in THREADS],
  "decisions":[{"id":k,"label":v} for k,v in DECISIONS.items()]}, open(out,"w"), separators=(",",":"))
c=collections.Counter(e["thread"] for e in events); print(c)
print(collections.Counter(e["driver"] for e in events)); print(collections.Counter(e["decision"] for e in events))
print(collections.Counter(e["themes"][0] for e in events)); print(sum(e["market"] for e in events))
print(sum(1 for k in kglist if not k["resolved"]), sum(1 for k in kglist if k["resolved"] and len(k["names"])>1))
for t in ["pushback","crude","russia","alunorte","metals"]:
  print(t,[e["head"][:60] for e in events if e["thread"]==t])

# ---- near-duplicate clustering (same development reported several times)
ROLES={"Subject","Partner","Customer","Target","Acquirer","Seller","Supplier"}
def keyset(e):
    s={x["kg"] for x in e["ents"] if x["kg"] and x["t"]=="company" and x["r"] in ROLES}
    return s
par=list(range(len(events)))
def f(i):
    while par[i]!=i: par[i]=par[par[i]]; i=par[i]
    return i
D=lambda a,b: abs((dt.date.fromisoformat(a)-dt.date.fromisoformat(b)).days)
for i,a in enumerate(events):
    ka=keyset(a)
    for j in range(i+1,len(events)):
        b=events[j]; kb=keyset(b)
        if a["decision"]!=b["decision"] or D(a["pub"],b["pub"])>14: continue
        inter=ka&kb
        la={x["n"] for x in a["ents"] if x["t"]=="location"}; lb={x["n"] for x in b["ents"] if x["t"]=="location"}
        if (len(inter)>=2 and D(a["pub"],b["pub"])<=7) or (len(inter)==1 and len(ka)==1 and len(kb)==1 and a["type"]==b["type"] and (la&lb or a["art"]==b["art"])) or (a["art"]==b["art"] and inter):
            par[f(i)]=f(j)
groups=collections.defaultdict(list)
for i in range(len(events)): groups[f(i)].append(i)
for g in groups.values():
    g.sort(key=lambda i:(events[i]["pub"],-len(events[i]["desc"])))
    lead=events[g[0]]["id"]
    for i in g: events[i]["dup"]=lead; events[i]["dupN"]=len(g)
print("distinct developments",len(groups))
for g in groups.values():
    if len(g)>1: print([ (events[i]["pub"][5:],events[i]["head"][:50]) for i in g])
data=json.load(open(out)); data["events"]=events; json.dump(data,open(out,"w"),separators=(",",":"))
