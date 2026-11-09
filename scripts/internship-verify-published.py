"""Check every published internship article and all linked local assets."""
from pathlib import Path
from urllib.parse import urlsplit, urljoin, unquote
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from PIL import Image
import argparse, hashlib, io, json, time, urllib.request

p = argparse.ArgumentParser()
p.add_argument('--base', default='https://teddy-yangjiale.github.io/notes/')
p.add_argument('--report', required=True)
args = p.parse_args()
root = Path(__file__).resolve().parents[1]
base = args.base.rstrip('/') + '/'
errors, articles, urls = [], [], set()

def fetch(url):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'NotesPublicationVerifier/1.0', 'Cache-Control':'no-cache'})
            with urllib.request.urlopen(req,timeout=45) as r:
                return {'url':url,'status':r.status,'data':r.read(),'content_type':r.headers.get('Content-Type','')}
        except Exception as e:
            if attempt==2:return {'url':url,'error':str(e)}
            time.sleep(1)

slugs = sorted(x.parent.name for x in (root/'src/content/notes').glob('internship-*/index.md'))
with ThreadPoolExecutor(max_workers=6) as pool:
    pages=list(pool.map(fetch,[urljoin(base,s+'/') for s in slugs]))
for slug, response in zip(slugs,pages):
    if response.get('status')!=200:
        errors.append(response);continue
    html=BeautifulSoup(response['data'],'html.parser')
    expected=BeautifulSoup((root/'dist'/slug/'index.html').read_bytes(),'html.parser')
    formula_count=len(html.select('.katex'))
    if formula_count!=len(expected.select('.katex')) or html.select('.katex-error'):
        errors.append({'url':response['url'],'error':'formula count mismatch or KaTeX error'})
    if html.select_one('h1').get_text()!=expected.select_one('h1').get_text():
        errors.append({'url':response['url'],'error':'title mismatch'})
    actual_article=html.select_one('article');expected_article=expected.select_one('article')
    if actual_article.get_text().replace('\r\n','\n')!=expected_article.get_text().replace('\r\n','\n'):
        errors.append({'url':response['url'],'error':'article text mismatch'})
    images=html.select('article img')
    for el in html.select('[href], img[src]'):
        link=el.get('href') or el.get('src')
        if link.startswith('/notes/'):
            urls.add(urljoin(base,link))
    articles.append({'slug':slug,'url':response['url'],'status':200,'formulas':formula_count,'images':len(images)})

resources={}
with ThreadPoolExecutor(max_workers=8) as pool:
    results=pool.map(fetch,sorted({u.split('#')[0] for u in urls}))
    for r in results:
        resources[r['url']]=r
        if r.get('status')!=200:errors.append({k:v for k,v in r.items() if k!='data'})
image_count=code_count=0
for url,r in resources.items():
    if r.get('status')!=200:continue
    local_path=root/'dist'/unquote(urlsplit(url).path.removeprefix('/notes/'))
    if '/internship/' in url and local_path.is_file():
        actual_bytes,expected_bytes=r['data'],local_path.read_bytes()
        if local_path.suffix in {'.html','.json','.js','.css','.md','.py','.txt'}:
            actual_bytes=actual_bytes.replace(b'\r\n',b'\n')
            expected_bytes=expected_bytes.replace(b'\r\n',b'\n')
        if hashlib.sha256(actual_bytes).digest()!=hashlib.sha256(expected_bytes).digest():
            errors.append({'url':url,'error':'asset differs from release build'})
    if urlsplit(url).path.lower().endswith(('.png','.jpg','.jpeg','.webp')):
        try:Image.open(io.BytesIO(r['data'])).verify();image_count+=1
        except Exception as e:errors.append({'url':url,'error':'image decoding failed: '+str(e)})
    if '/internship/code/' in url or '/8827-lesson/code/' in url:
        code_count+=1
        if not BeautifulSoup(r['data'],'html.parser').select('pre span[id]'):
            errors.append({'url':url,'error':'missing source lines'})
for url in urls:
    parts=urlsplit(url)
    if not parts.fragment:continue
    r=resources.get(url.split('#')[0],{})
    if r.get('status')==200 and not BeautifulSoup(r['data'],'html.parser').find(id=unquote(parts.fragment)):
        errors.append({'url':url,'error':'missing anchor'})
column=resources.get(urljoin(base,'series/internship/'),{})
if column.get('status')!=200 or len(BeautifulSoup(column.get('data',b''),'html.parser').select('ol.toc>li'))!=18:
    errors.append({'error':'column does not list 18 articles'})
report={'base':base,'articles':articles,'article_count':len(articles),'formulas':sum(x['formulas'] for x in articles),
        'unique_images_verified':image_count,'source_pages_verified':code_count,'local_urls_with_fragments':len(urls),
        'http_resources_verified':len(resources),'errors':errors}
out=Path(args.report);out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='articles'},ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
