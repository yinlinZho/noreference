function run(image_rootpath,core,csv_rootpath)
image_paths = multi(image_rootpath)
    c = parcluster('local');
    c.NumWorkers = core;
    parpool(c, c.NumWorkers);
for i = 1:numel(image_paths)
    if ~isempty(strfind(image_paths{i},'p7')) || ~isempty(strfind(image_paths{i},'sony'))
        image_paths{i}
    try  
    name = regexp(image_paths{i}, filesep(), 'split')
    logfile = strcat('log\',name{2},'.log')
    diary(logfile);
    diary on;

    image_paths{i},csv_rootpath
    OUTPUT(image_paths{i},csv_rootpath)    
    catch ME
        disp 'Exception Throw in run calling output'
      
    end

    diary off;
    end
end
    poolobj = gcp('nocreate')
    delete(poolobj)