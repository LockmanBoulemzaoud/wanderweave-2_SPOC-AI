import os
from pipeline import build_itinerary

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    csv_path = os.path.join(BASE, "data","pois_sample_france.csv")
    outputs = os.path.join(BASE, "outputs")
    os.makedirs(outputs, exist_ok=True)

    city = "Paris"
    topics = ["art","photo","street-art","relax","gourmet"]
    mode = "rencontres"   # 'solo' | 'amis' | 'rencontres'
    hidden_ratio = 0.4

    itin = build_itinerary(csv_path, city, topics, mode=mode, hidden_ratio=hidden_ratio)
    if itin.empty:
        print("Aucun créneau trouvé. Essayez d'élargir les horaires ou les topics.")
        return

    csv_out = os.path.join(outputs, "itinerary.csv")
    itin.to_csv(csv_out, index=False)

    md_out = os.path.join(outputs, "itinerary.md")
    with open(md_out, "w", encoding="utf-8") as f:
        f.write("# Itinéraire — WanderWeave (démo)\n\n")
        f.write(f"Ville: {city} | Mode: {mode} | Topics: {', '.join(topics)}\n\n")
        for _, r in itin.iterrows():
            hidden = " (Hidden)" if int(r['hidden'])==1 else ""
            line = f"- **{r['time_start']}–{r['time_end']}** — **{r['name']}** [{r['category']}{hidden}] — tags: {r['tags']}\n"
            f.write(line)
        f.write("\n> Export généré offline à partir de `data/pois_sample.csv`.\n")
    print(f"Exports:\n - {csv_out}\n - {md_out}")

if __name__ == "__main__":
    main()