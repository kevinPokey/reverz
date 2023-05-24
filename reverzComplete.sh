#!/bin/bash

#document.save(f"{sessionUser}tmp.docx")
#os.system(f"mv {sessionUser}tmp.docx {sessionUser}tmp.docx.zip && unzip {sessionUser}tmp.docx.zip word/document.xml")
#file = open(f"word/document.xml")
#xmlBody = file.read()
# xmlBody = document._body._body.xml
#xmlBody = xmlBody.replace("Datum:", "Datum: Nekaj")
#file.close()
#file = open(f"word/document.xml", "w")
#file.write(xmlBody)
#file.close()
#os.system(f"zip {sessionUser}tmp.docx.zip word/document.xml")
#os.system(f"mv {sessionUser}tmp.docx.zip {sessionUser}tmp.docx && rm -r word")

cwd=$(pwd)
path="${cwd}/${1}"
echo $path

cd ${path}
currentDate=`date +"%d.%m.%Y"`

mv ${path}/tmp2.docx ${path}/${1}.zip
unzip -o ${path}/${1}.zip word/document.xml
sed -i "s/Datum:/Datum: ${currentDate}/" ${path}/word/document.xml
sed -i "s/templateUser/${2}/" ${path}/word/document.xml
sed -i "s/templateEmployee/${3}/" ${path}/word/document.xml
sed -i "s/templateGiven/${4}/" ${path}/word/document.xml
sed -i "s/templateTaken/${5}/" ${path}/word/document.xml
sed -i "s/reverzNum/${6}/" ${path}/word/document.xml
sed -i "s/star/${7}/" ${path}/word/document.xml
zip ${path}/${1}.zip word/document.xml
mv ${path}/${1}.zip ${path}/tmp2.docx
