import { getCollection, type CollectionEntry } from 'astro:content';
import { SERIES, seriesById, type Series } from './series';

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

/** 不属于任何专栏的笔记 —— 首页"散记"区显示的就是这些 */
export async function standaloneNotes(): Promise<Note[]> {
  const notes = await allNotes();
  return notes.filter((n) => !n.data.series || !seriesById.has(n.data.series));
}

/** 某个专栏下的笔记，按 order 升序（没写 order 的排最后，再按日期） */
export async function notesInSeries(id: string): Promise<Note[]> {
  const notes = await allNotes();
  return notes
    .filter((n) => n.data.series === id)
    .sort((a, b) => {
      const ao = a.data.order ?? Number.MAX_SAFE_INTEGER;
      const bo = b.data.order ?? Number.MAX_SAFE_INTEGER;
      if (ao !== bo) return ao - bo;
      return a.data.date.getTime() - b.data.date.getTime();
    });
}

/** 专栏内的序号标签：正常讲次显示 01/02，补充篇（order>=90）显示 A/B/C */
export function orderLabel(order: number | undefined, fallback: number): string {
  const o = order ?? fallback;
  if (o === 0) return '00';
  if (o >= 90) return String.fromCharCode(65 + o - 91);
  return String(o).padStart(2, '0');
}

export interface SeriesWithNotes {
  series: Series;
  notes: Note[];
}

/** 所有非空专栏，按 weight 排序 —— 首页的合集卡片用它 */
export async function allSeries(): Promise<SeriesWithNotes[]> {
  const out: SeriesWithNotes[] = [];
  for (const series of SERIES) {
    const notes = await notesInSeries(series.id);
    if (notes.length > 0) out.push({ series, notes });
  }
  return out.sort(
    (a, b) => (a.series.weight ?? 99) - (b.series.weight ?? 99)
  );
}

/** 专栏内的上一篇 / 下一篇，用于文章底部的连续阅读 */
export async function seriesNeighbours(note: Note) {
  if (!note.data.series) return { series: null, prev: null, next: null, index: -1 };
  const series = seriesById.get(note.data.series);
  if (!series) return { series: null, prev: null, next: null, index: -1 };
  const list = await notesInSeries(note.data.series);
  const i = list.findIndex((n) => n.id === note.id);
  return {
    series,
    prev: i > 0 ? list[i - 1] : null,
    next: i >= 0 && i < list.length - 1 ? list[i + 1] : null,
    index: i,
    total: list.length,
  };
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
