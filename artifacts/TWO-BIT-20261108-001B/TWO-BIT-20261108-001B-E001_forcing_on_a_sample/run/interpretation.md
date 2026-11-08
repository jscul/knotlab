# TWO-BIT-20261108-001B-E001: interpretation

**No result.** Three launches, none of which wrote a row:
- 14:47 UTC: failed at setup within five seconds, a pickling error from loading the forcing library twice under different names
  (`log_first_launch.txt`); fixed by loading the torus search's modules first.
- 14:49 UTC: killed by the out-of-memory killer at 14:56 (peak 59.6 GB with 6 GB of swap). Six products ran at once, each holding about
  300,000 labelled collars with the full support index of `forcing4.arc_consistency`. The session restart at that time probably came from
  this. (`log_second_launch_killed_at_restart.txt` is empty: the run prints nothing before its first rows.)
- 16:22 UTC: killed the same way at 16:33 (peak 58.9 GB). The empty `log.txt` is this launch's.

The test was rerun as E002 and then E003 with the same sample and steps.
