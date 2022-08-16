#!/bin/sh

mv -f xml/*.report reports

find ./xml -type f -name "*.xml" | while read F
do
  python2 CheckRemoteControls.py ${F} > ${F}.report
done

mv -f xml/*.report reports

mv -f html/*.html-* suggestions
mv -f html/*.xml-* suggestions

find ./html -type f -name "*.html" | while read F
do
  python2 CheckRemoteControls.py ${F}
done

mv -f html/*.html-* suggestions
mv -f html/*.xml-* suggestions
