#!/bin/sh

echo ""
echo "Previews by OE-A"
echo ""
echo "Checking remote files, please wait ..."
begin=$(date +"%s")

python3 checkremotes.py | sort -u > previews.log

echo "Creating previews, please wait ..."

mkdir -p previews

python3 makepreviews.py

for f in previews/*.png; do
    mv -f "$f" "${f%.png}-preview.png"
done

mv -f previews/*.png rc/
rm -rf previews

git add -u
git add *
git commit -m "Create previews"

echo ""
finish=$(date +"%s")
timediff=$(($finish-$begin))
echo -e "Check time was $(($timediff / 60)) minutes and $(($timediff % 60)) seconds."
echo -e "Fast checking would be less than 1 minute."
echo ""
echo "Done!"
echo ""
