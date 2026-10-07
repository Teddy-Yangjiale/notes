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
    id: 'vision-foundations',
    title: '视觉大模型 · 基础与核心论文',
    badge: 'VISION',
    description:
      '面向基础不扎实的读者，从图像、数学与训练讲到视觉表征、视觉语言、生成、视频、三维和具身模型。' +
      '逐知识点解释符号、维度和直觉，配完整手算、原创图解与带详解的练习；总览列出完整知识覆盖和写作进度。',
    color: 'moss',
    weight: 7,
  },
  {
    id: 'vision-frontiers',
    title: '视觉大模型 · 前沿研究',
    badge: 'VFRONT',
    description:
      '围绕感知与推理、视觉潜空间、理解生成统一、流式记忆、空间与具身智能组织前沿论文。' +
      '每个专题讲原理、实验依据、分歧与开放问题，并给出可检验的研究假设。',
    color: 'clay',
    weight: 8,
  },
  {
    id: 'cs323',
    title: 'CS323 · 编译原理',
    badge: 'CS323',
    description:
      '南科大 CS323 Compilers（刘烨庞老师，Fall 2026）逐讲中文笔记。' +
      '从编译器的七个阶段讲起，沿着 正则表达式 → NFA → DFA → 上下文无关文法 这条主线，' +
      '把每个定义、算法和易错点都配上完整推导与例子，每讲末尾附复习自测。',
    color: 'plum',
    weight: 0,
  },
  {
    id: 'cs201',
    title: 'CS201 · 离散数学',
    badge: 'CS201',
    description:
      '南科大 CS201 Discrete Mathematics（Shan Chen 老师，Fall 2026）中文笔记。' +
      '面向零基础：每个符号都从「它到底在说什么」讲起，' +
      '命题逻辑 → 逻辑等价 → 谓词逻辑 → 形式证明 → 证明方法层层递进，' +
      '课件里的练习全部附完整解答，每章末尾有符号速查与易错清单。',
    color: 'sand',
    weight: 1,
  },
  {
    id: 'sta5007',
    title: 'STA-5007 · 高级自然语言处理',
    badge: 'STA-5007',
    description:
      '南科大统计与数据科学系，陈冠华老师《高级自然语言处理》课堂笔记。' +
      '按课件逐页拆解：每页配原始截图，图下先给原文要点，再补推导细节、维度核对、' +
      '直觉解释与易错点，配逐元素图解和带详解的练习。',
    color: 'moss',
    weight: 2,
  },
  {
    id: 'cs336',
    title: 'CS336 · 从零构建语言模型',
    badge: 'CS336',
    description:
      '斯坦福 CS336 Spring 2026 逐讲中文笔记。从 BPE 分词一路走到分布式训练、Scaling Laws、推理服务与后训练，' +
      '每讲都按"为什么需要它 → 算法怎么推 → 实现要注意什么 → 怎么判断做对了"重写过。',
    color: 'sky',
    weight: 3,
  },
  {
    id: 'cs329a',
    title: 'CS329A · 自我改进的语言模型智能体',
    badge: 'CS329A',
    description:
      '斯坦福 CS329A 逐讲中文笔记。主题是推理时扩展与自我改进：验证器、工具反馈、规划、' +
      '强化学习、深度研究智能体与长时程任务评估，外加三篇补充专题。',
    color: 'clay',
    weight: 4,
  },
  {
    id: 'ai-infra-survey',
    title: 'AI Infra 前沿调研 2026',
    badge: 'INFRA',
    description:
      '面向 LLM 系统的十二方向文献综述：推理服务与调度、KV Cache、投机解码、PD 分离、MoE、' +
      '量化低精度、显存卸载、长上下文、分布式训练、RL 后训练、GPU 算子编译器、Agent 基础设施。' +
      '每个方向按「问题定义 → 历史脉络 → 2025–2026 前沿 → 开放问题 → 论文速查」展开，' +
      '并附 PD 分离三部曲、KV 准入决策全链路讲解与顶会论文清单。每篇配可视化图解。',
    color: 'sky',
    weight: 6,
  },
  {
    id: 'mlsys-failures',
    title: 'MLSys 失败实验复盘',
    badge: 'KILL',
    description:
      '2026 年 9 月，在四张消费级 Blackwell 显卡上连续试了九个 MLSys 方向，全部没有活下来。' +
      '每篇按一条完整的研究链路复盘一个方向：背景原理、动机与假设、预注册判据、实验与数据、' +
      '怎么死的、哪些测量仍然有效、犯过的错和学到的教训。',
    color: 'lilac',
    weight: 5,
  },
];

export const seriesById = new Map(SERIES.map((s) => [s.id, s]));
