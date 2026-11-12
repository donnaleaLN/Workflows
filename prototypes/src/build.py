import json,sys
t=open(sys.argv[1]).read(); d=open(sys.argv[2]).read()
page=t.replace("/*__DATA__*/null", d.replace("</","<\\/"))
open(sys.argv[3],"w").write(page)
open(sys.argv[4],"w").write('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n</head>\n<body>\n'+page+'\n</body>\n</html>\n')
