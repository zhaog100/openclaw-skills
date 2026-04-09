import { SearchResult } from "./search";

export interface ScoredResult extends SearchResult {
  score: number;
  reasons: string[];
}

export function scoreResults(results: SearchResult[]): ScoredResult[] {
  const seen = new Set<string>();
  const scored: ScoredResult[] = [];

  for (const r of results) {
    if (seen.has(r.url)) continue;
    seen.add(r.url);

    let score = 0;
    const reasons: string[] = [];

    // Bounty keyword signals
    const body = (r.title + " " + r.body).toLowerCase();
    if (body.includes("bounty")) { score += 30; reasons.push("bounty keyword"); }
    if (body.includes("usdc") || body.includes("usdt") || body.includes("$")) { score += 20; reasons.push("payment mentioned"); }
    if (body.includes("help wanted")) { score += 15; reasons.push("help wanted"); }

    // Labels
    for (const label of r.labels) {
      const l = label.toLowerCase();
      if (l.includes("bounty")) { score += 25; reasons.push("bounty label"); }
      if (l.includes("reward")) { score += 20; reasons.push("reward label"); }
      if (l.includes("price")) { score += 15; reasons.push("price label"); }
      if (l.includes("funding")) { score += 10; reasons.push("funding label"); }
    }

    // Repo signals
    if (r.type === "repo") {
      score += r.stars * 0.1;
      if (r.stars > 100) reasons.push(`${r.stars} stars`);
    }

    // Recency bonus
    const daysSinceUpdate =
      (Date.now() - new Date(r.updatedAt).getTime()) / (1000 * 60 * 60 * 24);
    if (daysSinceUpdate < 7) { score += 10; reasons.push("updated this week"); }
    else if (daysSinceUpdate < 30) { score += 5; reasons.push("updated this month"); }

    if (score > 0) {
      scored.push({ ...r, score, reasons });
    }
  }

  return scored.sort((a, b) => b.score - a.score);
}
