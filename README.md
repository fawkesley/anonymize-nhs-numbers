NOTE: This is very old code, and not especially good or tested!

This utility will process the files passed on the command line (or look in the
current directory) and look for NHS numbers as defined below. It will use
pseudonyms stored in pseudonyms.csv or generate random, valid NHS numbers and
replace the numbers in the file with these numbers. Output files are placed in
the same directory but are prefixed with ANON_{filename}.

An NHS number is defined as any 10 digit number, surrounded by non-digits, ie
``xxx1234567890yyy``, with a valid modulo 11 checksum, as defined here:

[http://www.datadictionary.nhs.uk/version2/data_dictionary/data_field_notes/n/nhs_number_de.asp?shownav=0](http://www.datadictionary.nhs.uk/version2/data_dictionary/data_field_notes/n/nhs_number_de.asp?shownav=0)

Be careful as this will replace ANY 10 digit number which follows this format, even if randomly.

