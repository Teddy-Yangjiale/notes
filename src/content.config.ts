import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const notes = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/notes' }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    updated: z.coerce.date().optional(),
    tags: z.array(z.string()).default([]),
    summary: z.string().optional(),
    draft: z.boolean().default(false),
    // 手账风格：给卡片指定一个便签配色（不填则按标签自动分配）
    color: z.enum(['sand', 'moss', 'sky', 'clay', 'plum', 'lilac']).optional(),
    pinned: z.boolean().default(false),

    // ── 专栏 ──────────────────────────────────────────
    // series 填 src/lib/series.ts 里定义的专栏 id，这篇笔记就归入那个合集，
    // 不再单独出现在首页的"散记"里。order 决定它在专栏内的顺序（从小到大）。
    series: z.string().optional(),
    order: z.number().optional(),
    // 专栏内的短标题，列表里用它代替长标题（可选）
    shortTitle: z.string().optional(),
  }),
});

export const collections = { notes };
