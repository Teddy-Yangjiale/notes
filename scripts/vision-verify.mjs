import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import katex from 'katex';

// Validates the authored curriculum and its small, dependency-free examples.
// This does not evaluate real model quality or run a vision training job.
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const notesRoot = path.join(root, 'src/content/notes');
const curriculum = JSON.parse(fs.readFileSync(path.join(root, 'scripts/vision-curriculum.json'), 'utf8'));
const errors = [];
const pages = [];
if (curriculum.chapters.length !== 80) errors.push('Expected 80 main chapters');
if (curriculum.frontiers.length !== 10) errors.push('Expected 10 frontier topics');
for (const [i, chapter] of curriculum.chapters.entries()) {
  if (chapter.order !== i + 1) errors.push('Chapter order ' + chapter.order + ' at ' + i);
  if (chapter.status === 'written' && (!chapter.slug || !fs.existsSync(path.join(notesRoot, chapter.slug, 'index.md')))) {
    errors.push('Written chapter lacks source: ' + chapter.order);
  }
}
for (const slug of fs.readdirSync(notesRoot).filter(n => /^vision-\d{2}-/.test(n)).sort()) {
  const source = fs.readFileSync(path.join(notesRoot, slug, 'index.md'), 'utf8').replace(/\r\n/g, '\n');
  const body = source.replace(/^---\n[\s\S]*?\n---\n/, '');
  const prose = body.replace(/^(~~~|[\x60]{3})[^\n]*\n[\s\S]*?^\1\s*$/gm, '');
  const formulas = [...prose.matchAll(/\$\$([\s\S]+?)\$\$|\$([^$\n]+?)\$/g)];
  for (const formula of formulas) {
    try {
      katex.renderToString(formula[1] ?? formula[2], { throwOnError: true, displayMode: Boolean(formula[1]), strict: 'error' });
    } catch (error) {
      errors.push(slug + ': ' + formula[0].slice(0, 90) + ': ' + error.message);
    }
  }
  if (/\\[()]/.test(prose)) errors.push(slug + ': unconverted inline math delimiters');
  for (const match of body.matchAll(/!\[[^\]]*\]\(([^)]+)\)/g)) {
    if (!match[1].startsWith('http') && !fs.existsSync(path.resolve(notesRoot, slug, match[1]))) {
      errors.push(slug + ': missing image ' + match[1]);
    }
  }
  for (const match of prose.matchAll(/(?<!!)\[[^\]]+\]\((\.\.\/[^)]+)\)/g)) {
    const target = match[1].split('#')[0].replace(/\/$/, '');
    if (target.startsWith('../series/')) {
      const series = target.slice('../series/'.length);
      const registry = fs.readFileSync(path.join(root, 'src/lib/series.ts'), 'utf8');
      if (!registry.includes("id: '" + series + "'") && !registry.includes('id: "' + series + '"')) {
        errors.push(slug + ': unknown series link ' + target);
      }
    } else if (!fs.existsSync(path.resolve(notesRoot, slug, target, 'index.md')) &&
               !fs.existsSync(path.resolve(notesRoot, slug, target + '.md'))) {
      errors.push(slug + ': unknown note link ' + target);
    }
  }
  const codeBlocks = [...body.matchAll(/^~~~python\n([\s\S]*?)^~~~\s*$/gm)];
  const examples = [];
  for (const [i, block] of codeBlocks.entries()) {
    const run = spawnSync('python', ['-c', block[1]], { encoding: 'utf8', timeout: 15000, windowsHide: true });
    if (run.error || run.status !== 0) errors.push(slug + ' example ' + (i+1) + ': ' + (run.error || run.stderr));
    examples.push({ number: i+1, output: run.stdout?.trim(), passed: run.status === 0 });
  }
  const htmlPath = path.join(root, 'dist', slug, 'index.html');
  const html = fs.existsSync(htmlPath) ? fs.readFileSync(htmlPath, 'utf8') : '';
  if (html.includes('class="katex-error"')) errors.push(slug + ': rendered KaTeX error');
  // A malformed display delimiter can swallow the rest of a Markdown page
  // even when each formula passes an isolated KaTeX call.
  if (html) {
    const sourceHeadings = (body.match(/^### /gm) || []).length;
    const builtHeadings = (html.match(/<h3\b/g) || []).length;
    if (sourceHeadings !== builtHeadings) {
      errors.push(slug + ': rendered h3 count ' + builtHeadings + ' differs from source ' + sourceHeadings);
    }
  }
  for (const match of html.matchAll(/<img\b[^>]*\bsrc="([^"]+)"/g)) {
    const assetPath = match[1].replace(/^\/notes\//, '');
    if (!match[1].startsWith('http') && !fs.existsSync(path.join(root, 'dist', assetPath))) {
      errors.push(slug + ': missing built asset ' + assetPath);
    }
  }
  pages.push({
    slug, sourceCharacters: body.length, numberedTopics: (body.match(/^### \d+\./gm) || []).length,
    detailedCases: (body.match(/^### (?:算例|案例)[A-Z]/gm) || []).length,
    exercises: (body.match(/^### 练习\d+/gm) || []).length,
    images: (body.match(/!\[/g) || []).length, formulas: formulas.length, examples,
  });
}
const summary = {
  pages, totals: {
    sourceCharacters: pages.reduce((n,p) => n+p.sourceCharacters, 0),
    numberedTopics: pages.reduce((n,p) => n+p.numberedTopics, 0),
    detailedCases: pages.reduce((n,p) => n+p.detailedCases, 0),
    exercises: pages.reduce((n,p) => n+p.exercises, 0),
    images: pages.reduce((n,p) => n+p.images, 0),
    formulas: pages.reduce((n,p) => n+p.formulas, 0),
    codeExamples: pages.reduce((n,p) => n+p.examples.length, 0),
  }, errors,
};
console.log(JSON.stringify(summary, null, 2));
if (errors.length) process.exitCode = 1;
