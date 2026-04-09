import { CONFIG } from "./config";

export interface SearchResult {
  url: string;
  title: string;
  body: string;
  type: "issue" | "repo";
  language: string;
  stars: number;
  createdAt: string;
  updatedAt: string;
  labels: string[];
}

export async function searchGitHub(
  query: string,
  maxResults: number = 30
): Promise<SearchResult[]> {
  const results: SearchResult[] = [];
  const headers = {
    Authorization: `token ${CONFIG.githubToken}`,
    Accept: "application/vnd.github+json",
  };

  // Search issues
  const issueUrl = `https://api.github.com/search/issues?q=${encodeURIComponent(query)}+is:open&sort=updated&per_page=${maxResults}`;
  const issueRes = await fetch(issueUrl, { headers });
  const issueData = await issueRes.json();

  for (const item of issueData.items || []) {
    results.push({
      url: item.html_url,
      title: item.title,
      body: item.body?.substring(0, 500) || "",
      type: "issue",
      language: "",
      stars: 0,
      createdAt: item.created_at,
      updatedAt: item.updated_at,
      labels: item.labels?.map((l: any) => l.name) || [],
    });
  }

  // Search repos
  const repoUrl = `https://api.github.com/search/repositories?q=${encodeURIComponent(query)}&sort=stars&per_page=10`;
  const repoRes = await fetch(repoUrl, { headers });
  const repoData = await repoRes.json();

  for (const repo of repoData.items || []) {
    results.push({
      url: repo.html_url,
      title: repo.description || repo.full_name,
      body: repo.description || "",
      type: "repo",
      language: repo.language || "",
      stars: repo.stargazers_count,
      createdAt: repo.created_at,
      updatedAt: repo.updated_at,
      labels: repo.topics || [],
    });
  }

  return results;
}
