// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

// 部署目标: https://teddy-yangjiale.github.io/notes/
// site = 域名, base = 仓库名。改仓库名的话两处都要跟着改，
// 并且站内链接一律用 src/lib/notes.ts 里的 withBase() 生成。
export default defineConfig({
  site: 'https://teddy-yangjiale.github.io',
  base: '/notes',
  integrations: [mdx(), sitemap()],
  markdown: {
    remarkPlugins: [remarkMath],
    rehypePlugins: [rehypeKatex],
    shikiConfig: {
      themes: { light: 'github-light', dark: 'github-dark-dimmed' },
      wrap: true,
    },
  },
});
