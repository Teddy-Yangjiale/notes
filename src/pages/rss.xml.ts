import rss from '@astrojs/rss';
import type { APIContext } from 'astro';
import { allNotes, withBase } from '../lib/notes';

export async function GET(context: APIContext) {
  const notes = await allNotes();
  return rss({
    title: '笔记本',
    description: 'markdown 笔记、读书摘录与随手记录',
    site: new URL(withBase('/'), context.site!),   // 频道首页也要带 base
    items: notes.map((note) => ({
      title: note.data.title,
      pubDate: note.data.date,
      description: note.data.summary ?? '',
      link: withBase(`/${note.id}/`),   // withBase 补 base, rss 再接上 site
      categories: note.data.tags,
    })),
    customData: '<language>zh-CN</language>',
  });
}
