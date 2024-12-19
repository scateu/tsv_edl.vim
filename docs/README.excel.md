Numbers.app will open `.tsv` file beautifully, recognizing tab as seperated characters.

However, if opened directly with MS Excel, `.tsv` file will be treated as `csv` (comma seperated values).

So,

# Excel import

 - In MS Excel, create a new `.xlsx` file.
 - Data > Get External Data > Import Text File
 - In `Text Import Wizard`, 
   - Select your `.tsv` file
   - Next
   - Next
   - Finish
   - Import

Voila!

If you want to remove a line, just delete the `EDL` from that first column. So your lines can still stay in your way for future reference.

Plus, copy a region from your spreadsheet in MS Excel and pipe to `tsv2roughcut` works fine.
