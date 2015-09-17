function filename = OUTPUT(rootpath,outpath,mu_prisparam,cov_prisparam)
    
     blocksizerow    = 96;
     blocksizecol    = 96;
     blockrowoverlap = 0;
     blockcoloverlap = 0;
    if(isdir(rootpath))
        disp 'Reading the bmp list'
        name = regexp(rootpath, filesep(), 'split');
        name = name{2};
        
        listing = dir(rootpath);
        image_list = {listing.name}';
        len = numel(image_list);
        for i = 1:len
                image_list{i} = [rootpath,'\',image_list{i}];
        end
        qualityscore = zeros(len-2,1);
        index = zeros(len-2,1);
        parfor i =  3 : len
            
        %1. Load the image, for example
            
            if strfind(image_list{i},'bmp')
                image_list{i}                
                %a = regexp(image_list{i},'\d\d\d\d\d\d\d','match')
                
                %2. Call this function to calculate the quality score:
                try
                image  = imread(image_list{i});
                a = regexp(image_list{i},'_','split')
                l = numel(a{numel(a)})
                id = a{numel(a)}(l-6:l-4)
                id
                %id = a{1}(3:7)
                index(i-2) = str2num(id);
                qualityscore(i-2) =  computequality(image,blocksizerow,blocksizecol,blockrowoverlap,blockcoloverlap, ...
    mu_prisparam,cov_prisparam)              
                catch ME
                    disp 'error occur'
                end
             end
        end
        outpath = fullfile(outpath,strcat(name,'.csv'))
        A = [index qualityscore];
        csvwrite(outpath,A)
        filename = outpath;
    else
        disp('invalide image_path')
    end
end
