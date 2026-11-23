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
  /** GitHub repository name. */
  codeRepo: 'omniprep',
  /** Canonical site domain (no trailing slash). */
  url: 'https://omniprep.run',
  /** Deployment base path ('' for apex, '/omniprep-website' for a project repo). */
  basePath: '',
  /** Current pipeline version (also drives versioned-docs release names). */
  version: '26.3.1',
};

export const repoUrl = `https://github.com/${site.githubUser}/${site.githubRepo}`;
export const codeRepoUrl = `https://github.com/${site.githubUser}/${site.codeRepo}`;
export const issuesUrl = `https://github.com/${site.githubUser}/${site.codeRepo}/issues`;
export const releasesUrl = `${codeRepoUrl}/releases`;
/** Latest release page (auto-resolves to the newest tag, includes assets). */
export const latestReleaseUrl = `${releasesUrl}/latest`;

/**
 * Release asset naming convention (version = `site.version`, tag = `v${site.version}`):
 *   omniprep-<version>-docker.tar.gz           → container image archive
 *   omniprep-<version>-win-x64.exe             → Windows GUI
 *   omniprep-<version>-macos-universal.dmg     → macOS GUI
 *   omniprep-<version>-linux-amd64.deb         → Linux GUI (Debian/Ubuntu)
 */
const tag = `v${site.version}`;
/** Build a direct GitHub download URL for a release asset. */
const assetUrl = (filename: string) =>
  `${releasesUrl}/download/${tag}/${filename}`;

export const downloads = {
  /** Current release tag (e.g. `v26.2.1`). */
  tag,
  /** Docker image archive (tar.gz). */
  docker: {
    filename: `omniprep-${site.version}-docker.tar.gz`,
    url: assetUrl(`omniprep-${site.version}-docker.tar.gz`),
  },
  /** Desktop GUI installers. */
  gui: {
    win: {
      filename: `omniprep-${site.version}-win-x64.exe`,
      url: assetUrl(`omniprep-${site.version}-win-x64.exe`),
    },
    macos: {
      filename: `omniprep-${site.version}-macos-universal.dmg`,
      url: assetUrl(`omniprep-${site.version}-macos-universal.dmg`),
    },
    linux: {
      filename: `omniprep-${site.version}-linux-amd64.deb`,
      url: assetUrl(`omniprep-${site.version}-linux-amd64.deb`),
    },
  },
};
