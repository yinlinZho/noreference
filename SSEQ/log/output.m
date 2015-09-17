
feature('DefaultCharacterSet', 'UTF8')
function filename = output(image_rootpath,outpath)
    image_rootpath
    outpath = 'F:\'
    score = multi(image_rootpath)
    
    len = numel(score)
    index = 1:len;
    index = index';
    name = regexp(image_rootpath, filesep(), 'split');
    name = name{2}
    outpath = fullfile(outpath,strcat(name,'.csv'))
    %file = fopen(outpath,'w');
    %format = '%d,%6.3f\n'
    A = [index score];
    csvwrite(outpath,A)
    %fclose(file)
    filename = outpath;
