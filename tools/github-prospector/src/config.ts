export const CONFIG = {
  githubToken: process.env.GITHUB_TOKEN || "",
  queries: [
    "bounty label:help-wanted",
    "bug bounty reward",
    "open source bounty USDC",
    "crypto bounty program",
    "smart contract audit bounty",
    "DeFi bounty developer",
    "security bounty responsible disclosure",
    "open bounty contributor",
  ],
  maxResults: 30,
};
