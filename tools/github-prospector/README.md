# GitHub Bounty Prospector

A tool for finding bounty projects and developers on GitHub for growth/marketing purposes.

## Usage

```bash
export GITHUB_TOKEN=your_token
cd tools/github-prospector
npx ts-node src/index.ts
```

## Features

- Searches GitHub for bounty-related repos and issues
- Scores and ranks potential leads
- Exports results as JSON

## Query Patterns

- `bounty label:help-wanted`
- `bug bounty reward`
- `open source bounty USDC`
- `crypto bounty program`
- `security bounty responsible disclosure`

## Output

Results are saved to `prospector-results.json` with scores and reasons.
