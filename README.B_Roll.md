# B Roll

Add `[B]` right in the beginning of the subtitle section, i.e., right after the 'TAB' character. Then this line will be treated as a B-roll, `lane=1` set in fcpxml.

```
EDL 00:00:00,000    00:00:01,000    | some video |  [B] this line will be treated as B-roll
EDL 00:03:02,000    00:03:04,000    | A roll video |  normal lines
EDL 00:03:04,000    00:03:09,000    | A roll video |  more normal lines
```

It works in `tsv2fcpxml` now.

 - [ ] Support in tsv2roughcut
 - [ ] Only supported in Davinci Resolve. FCPX doesn't work.
