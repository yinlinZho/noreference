function delete_parpool(core)
c = parcluster('local');
c.NumWorkers = core;
parpool(c, c.NumWorkers);