// @ts-check
import { defineConfig } from 'astro/config';
import { site } from './src/config.ts';

export default defineConfig({
  site: site.url,
  base: site.basePath || '/',
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'zh'],
    routing: {
      prefixDefaultLocale: false, // English at /, Chinese at /zh/
    },
  },
});
