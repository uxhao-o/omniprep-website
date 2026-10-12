/**
 * Central site configuration.
 * All site-wide identifiers (GitHub account/repo, domain, base path) are
 * defined here and imported where needed — nothing is hard-coded elsewhere.
 *
 * To relocate the site, edit this file (and `base` in astro.config.mjs).
 */
export const site = {
  /** GitHub account (used to build repo & releases URLs). */
  githubUser: 'uxhao-o',
  /** GitHub repository name. */
  githubRepo: 'omniprep-website',
  /** Canonical site domain (no trailing slash). */
  url: 'https://uxhao-o.github.io',
  /** Deployment base path ('' for apex, '/omniprep-website' for a project repo). */
  basePath: '/omniprep-website',
  /** Current pipeline version (also drives versioned-docs release names). */
  version: '26.2.1',
};

export const repoUrl = `https://github.com/${site.githubUser}/${site.githubRepo}`;
export const releasesUrl = `${repoUrl}/releases`;
