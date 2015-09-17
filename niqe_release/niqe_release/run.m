function run(image_rootpath,core,csv_rootpath)
load modelparameters.mat
image_paths = multi(image_rootpath);
 c = parcluster('local');
 c.NumWorkers = core;
 parpool(c, c.NumWorkers);
for i = 1:numel(image_paths)
    if strfind(image_paths{i},'yy11')    
        image_paths{i}
    try  
    name = regexp(image_paths{i}, filesep(), 'split')
    logfile = strcat('log\',name{2},'.log')
    diary(logfile);
    diary on;
   
    image_paths{i},csv_rootpath
    OUTPUT(image_paths{i},csv_rootpath,mu_prisparam,cov_prisparam)    
    catch ME
        disp 'Exception Throw in run calling output'     
    end
    diary off;
    end
end
 poolobj = gcp('nocreate')
 delete(poolobj)
 