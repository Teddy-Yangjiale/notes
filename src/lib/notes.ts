import { getCollection, type CollectionEntry } from 'astro:content';

export type Note = CollectionEntry<'notes'>;

const PALETTE = ['sand', 'moss', 'sky', 'clay', 'plum', 'lilac'] as const;
export type Swatch = (typeof PALETTE)[number];

/** 用标签名做稳定哈希，保证同一标签在全站永远是同一个颜色 */
export function swatchFor(seed: string): Swatch {
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) >>> 0;
  return PALETTE[h % PALETTE.length];
}

export function colorOf(note: Note): Swatch {
  return note.data.color ?? swatchFor(note.data.tags[0] ?? note.id);
}

/** 生产环境隐藏草稿；本地 dev 依然可见，方便边写边看 */
export async function allNotes(): Promise<Note[]> {
  const notes = await getCollection('notes', ({ data }) =>
    import.meta.env.PROD ? data.draft === false : true
  );
  return notes.sort((a, b) => {
    if (a.data.pinned !== b.data.pinned) return a.data.pinned ? -1 : 1;
    return b.data.date.getTime() - a.data.date.getTime();
  });
}

export async function allTags(): Promise<{ tag: string; count: number }[]> {
  const notes = await allNotes();
  const counts = new Map<string, number>();
  for (const n of notes) {
    for (const t of n.data.tags) counts.set(t, (counts.get(t) ?? 0) + 1);
  }
  return [...counts.entries()]
    .map(([tag, count]) => ({ tag, count }))
    .sort((a, b) => b.count - a.count || a.tag.localeCompare(b.tag, 'zh'));
}

/**
 * 给站内链接加上 base 前缀。
 * 设了 astro.config 的 base 之后，写死的 "/tags/" 不会自动变成 "/notes/tags/"，
 * 所有站内链接都要经过这里，否则部署上去会 404。
 */
export function withBase(path: string): string {
  const base = import.meta.env.BASE_URL.replace(/\/+$/, '');
  const rest = path.replace(/^\/+/, '');
  return rest ? `${base}/${rest}` : `${base}/`;
}

/** 判断导航项是否为当前页（比较时先补上 base） */
export function isCurrent(pathname: string, href: string): boolean {
  const target = withBase(href);
  const here = pathname.replace(/\/+$/, '') || '/';
  const there = target.replace(/\/+$/, '') || '/';
  return href === '/' ? here === there : here.startsWith(there);
}

export function fmtDate(d: Date): string {
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric', month: 'long', day: 'numeric',
  }).format(d);
}

/** 中英混排的粗略字数与阅读时长估算 */
export function readingTime(body: string): number {
  const cjk = (body.match(/[一-龥]/g) ?? []).length;
  const words = (body.replace(/[一-龥]/g, ' ').match(/\b\w+\b/g) ?? []).length;
  return Math.max(1, Math.round(cjk / 400 + words / 220));
}
