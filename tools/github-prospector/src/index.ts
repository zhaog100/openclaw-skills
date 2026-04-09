import { searchGitHub } from "./search";
import { scoreResults } from "./scoring";
import { CONFIG } from "./config";

async function main() {
  console.log("🔍 GitHub Bounty Prospector");
  console.log(`Searching ${CONFIG.queries.length} query patterns...`);

  const allResults = [];

  for (const query of CONFIG.queries) {
    console.log(`\nSearching: "${query}"`);
    const results = await searchGitHub(query, CONFIG.maxResults);
    allResults.push(...results);
  }

  const scored = scoreResults(allResults);
  
  console.log(`\n✅ Found ${scored.length} potential leads:`);
  
  for (const result of scored.slice(0, 20)) {
    console.log(
      `[${result.score.toFixed(1)}] ${result.url} — ${result.title}`
    );
  }

  // Export as JSON
  const fs = require("fs");
  fs.writeFileSync(
    "prospector-results.json",
    JSON.stringify(scored, null, 2)
  );
  console.log("\n📁 Results saved to prospector-results.json");
}

main().catch(console.error);
