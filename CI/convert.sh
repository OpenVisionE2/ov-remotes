#!/bin/sh

echo ""
echo "ConvertRemoteControls.py by IanSav"
echo ""
echo "Converting remote files, please wait ..." 
begin=$(date +"%s")

rm -rf convert-report
rm -rf convert-result
mkdir -p convert-report
mkdir -p convert-result

find ./rc -type f -name "*.xml" | while read F
do
  python2 ConvertRemoteControls.py ${F} > ${F}.report
done

mv -f rc/*.report convert-report

mv -f rc/*-new* convert-result

find ./rc -type f -name "*.html" | while read F
do
  python2 ConvertRemoteControls.py ${F}
done

mv -f rc/*-new* convert-result

git add -u
git add *
git commit -m "Convert remote files"

echo ""
finish=$(date +"%s")
timediff=$(($finish-$begin))
echo -e "Convert time was $(($timediff / 60)) minutes and $(($timediff % 60)) seconds."
echo -e "Fast converting would be less than 1 minute."
echo ""
echo "Convert Done!"
echo ""
