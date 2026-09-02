/**
 * 专栏（合集）定义。
 *
 * 想新开一个专栏：在下面数组里加一条，然后给笔记的 front matter 写上
 * `series: "那个 id"` 和 `order: 1`（决定专栏内顺序）即可。
 * 归入专栏的笔记不会再单独出现在首页的"散记"区，而是收进对应的合集卡片里。
 */
export interface Series {
  /** 唯一 id，也是网址：/series/<id>/ */
  id: string;
  /** 合集标题 */
  title: string;
  /** 印在封面上的短代号，一到六个字符最好看 */
  badge: string;
  /** 卡片与列表页上的一句话介绍 */
  description: string;
  /** 便签配色 */
  color: 'sand' | 'moss' | 'sky' | 'clay' | 'plum' | 'lilac';
  /** 首页排序，小的在前 */
  weight?: number;
}

export const SERIES: Series[] = [
  {
    id: 'cs336',
    title: 'CS336 · 从零构建语言模型',
    badge: 'CS336',
    description:
      '斯坦福 CS336 Spring 2026 逐讲中文笔记。从 BPE 分词一路走到分布式训练、Scaling Laws、推理服务与后训练，' +
      '每讲都按"为什么需要它 → 算法怎么推 → 实现要注意什么 → 怎么判断做对了"重写过。',
    color: 'sky',
    weight: 1,
  },
  {
    id: 'cs329a',
    title: 'CS329A · 自我改进的语言模型智能体',
    badge: 'CS329A',
    description:
      '斯坦福 CS329A 逐讲中文笔记。主题是推理时扩展与自我改进：验证器、工具反馈、规划、' +
      '强化学习、深度研究智能体与长时程任务评估，外加三篇补充专题。',
    color: 'clay',
    weight: 2,
  },
];

export const seriesById = new Map(SERIES.map((s) => [s.id, s]));
