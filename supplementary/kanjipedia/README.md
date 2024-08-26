# Kanjipedia conversion indices
Since Japanese websites are often not very keen on using UTF-8 encoding, they often use
images to replace certain kanji, and whilst it's usually possible to turn the image into its Unicode
equivalent (most of the time, the image name is just the Unicode code point), there are some cases on
the Kanjipedia website where this doesn't hold true.

The first main examples of this are the "nw" kanji images, of which there are 8, which
substitute 8 particular (apparently unrelated) kanji. Since I could not understand by what pattern
they are all given their own "namespace" or special file path, I have drawn them up in the index
`headword_kanji_to_unicode.json` file, which is only to be invoked when the kanji in the headword
of an entry is not in Unicode already, and not an image with a Unicode-codepoint file name.

The second exponent is the kanji radical images, which are primarily based on the equivalent indices
of the Kangxi radicals (whose orders can be seen on Wikipedia, for instance), however do not match
them one-to-one. This means that some radical images have the same file name as their Kangxi radical's
number in the list, whereas others are mismatched, and others still have multiple different images,
denoted with an `a`, `b`, `c`, or even up to `d` suffix (for the one kanji (⻎) with four different images).
A further kanji still, 門, has both 169 and 169a, even though these are the same radical and the forms
are not different. Therefore, I have simply created an index, partly automated but all manually checked,
which associates the kanji radical images to their actual Unicode equivalents.