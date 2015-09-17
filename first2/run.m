function run(image_rootpath,core,csv_rootpath)
load modelparameters.mat
image_paths = multi(image_rootpath);
create_parpool(core);
for i = 1:numel(image_paths)
    if ~isempty(strfind(image_paths{i},'p7')) || ~isempty(strfind(image_paths{i},'sony'))
        image_paths{i}
    try  
    name = regexp(image_paths{i}, filesep(), 'split')
    logfile = strcat('log\',name{numel(name)},'.log')
    diary(logfile);
    diary on;
   
    OUTPUT(image_paths{i},csv_rootpath,mu_prisparam,cov_prisparam)    
   	catch ME
        disp 'Exception Throw in run calling output'
      
    end

    diary off;
    end
end
    delete_parpool()