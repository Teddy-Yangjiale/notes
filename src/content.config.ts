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
  }),
});

export const collections = { notes };
