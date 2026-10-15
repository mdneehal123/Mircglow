"""Makes a click-through preview copy of dist/ with relative links (for the private preview page)."""
import os,re,shutil,json,sys
D="dist"; O=sys.argv[1]
shutil.rmtree(O,ignore_errors=True); os.makedirs(O)
pages=[os.path.relpath(os.path.join(d,f),D) for d,_,fs in os.walk(D) for f in fs if f.endswith(".html") and f!="404.html"]
def rel(t0, depth):
    t=t0.split("#")[0]; frag=t0[len(t):]
    if t=="/": return "../"*depth+"home/index.html"+frag
    if t.endswith("/"): t+="index.html"
    if not (t.startswith("/assets/") or t.startswith("/wp-content/")) and not os.path.exists(os.path.join(D,t.lstrip("/"))): return None
    return "../"*depth+t.lstrip("/")+frag
def fix_all(s,depth):
    return re.sub(r'(href|src)="(/[^"]*)"',lambda m: m.group(0) if m.group(2).startswith("//") else (f'{m.group(1)}="{rel(m.group(2),depth)}"' if rel(m.group(2),depth) else m.group(0)),s)
files={}
for p in pages:
    out="home/index.html" if p=="index.html" else p
    s=fix_all(open(os.path.join(D,p)).read(),out.count("/"))
    os.makedirs(os.path.dirname(os.path.join(O,out)),exist_ok=True); open(os.path.join(O,out),"w").write(s); files[out]=os.path.join(O,out)
shutil.copytree(os.path.join(D,"assets"),os.path.join(O,"assets"))
for f in os.listdir(os.path.join(O,"assets")): files["assets/"+f]=os.path.join(O,"assets",f)
h=fix_all(open(os.path.join(D,"index.html")).read(),0)
head=re.search(r"<head>(.*?)</head>",h,re.S).group(1); body=re.search(r"<body>(.*)</body>",h,re.S).group(1)
head=re.sub(r'<meta charset[^>]*>|<meta name="viewport"[^>]*>','',head)
head=re.sub(r"<title>.*?</title>","<title>Mirc Glow Website Preview</title>",head)
note='<div style="background:#fff7d6;color:#5a4500;font:600 13px/1.4 system-ui;padding:8px 16px;text-align:center">Preview of the new mircglow.com with your real product photos. Not live yet.</div>'
open(os.path.join(O,"main.html"),"w").write(head+note+body)
json.dump(files,open(os.path.join(O,"files.json"),"w"),indent=0)
print(len(files),"files")
