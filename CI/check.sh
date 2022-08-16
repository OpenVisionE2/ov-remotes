#!/bin/sh

echo ""
echo "CheckRemoteControls.py by IanSav"
echo ""
echo "Checking remote files, please wait ..." 
begin=$(date +"%s")

rm -rf check-report
rm -rf check-result
mkdir -p check-report
mkdir -p check-result

find ./rc -type f -name "*.xml" | while read F
do
  python2 CheckRemoteControls.py ${F} > ${F}.report
done

mv -f rc/*.report check-report

mv -f rc/*.html-* check-result
mv -f rc/*.xml-* check-result

find ./rc -type f -name "*.html" | while read F
do
  python2 CheckRemoteControls.py ${F}
done

mv -f rc/*.html-* check-result
mv -f rc/*.xml-* check-result

git add -u
git add *
git commit -m "Check remote files"

echo ""
finish=$(date +"%s")
timediff=$(($finish-$begin))
echo -e "Check time was $(($timediff / 60)) minutes and $(($timediff % 60)) seconds."
echo -e "Fast checking would be less than 1 minute."
echo ""
echo "Check Done!"
echo ""
