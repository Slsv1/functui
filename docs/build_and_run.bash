rm -r _build/html
rm -r _build/doctest
make doctest
make html
firefox _build/html/index.html

