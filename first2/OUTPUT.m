function filename = OUTPUT(rootpath,outpath,mu_prisparam,cov_prisparam)
    %parameter used in niqe algorithm
    blocksizerow    = 96;
    blocksizecol    = 96;
    blockrowoverlap = 0;
    blockcoloverlap = 0;
    if(isdir(rootpath))
        disp 'Reading the bmp list'
        name = regexp(rootpath, filesep(), 'split');
        name = name{numel(name)};

        listing = dir(rootpath);
        image_list = {listing.name}';
        len = numel(image_list);

        for i = 1:len
                image_list{i} = [rootpath,'\',image_list{i}];
        end
        niqe_qa = zeros(len-2,1);
        sseq_qa = zeros(len-2,1);
        %diivine_qa = zeros(len-2,1);
        index = zeros(len-2,1);
           
        parfor i =  3 : len
        %1. Load the image, for example      
            if ~isempty( strfind(image_list{i},'bmp'))
                image_list{i}               
                try
                %2.diivine algorithm
               
                a = regexp(image_list{i},'_','split')
                l = numel(a{numel(a)})
                id = a{numel(a)}(l-8:l-4)
                index(i-2) = str2num(id);
                
    
                %3.niqe
                image  = imread(image_list{i});
                niqe_qa(i-2) =  computequality(image,blocksizerow,blocksizecol,blockrowoverlap,blockcoloverlap, ...
                mu_prisparam,cov_prisparam);
                %4.sseq
                sseq_qa(i-2) = SSEQ(image);  
                %5.diivine
                %image = rgb2gray(imread(image_list{i}));
                %diivine_qa(i-2) = divine(image);
                catch ME
                    disp 'error occur'
                end
             end
        end
        outpath = fullfile(outpath,strcat(name,'.csv'))
        A = [index niqe_qa sseq_qa];
        csvwrite(outpath,A)
        filename = outpath;
    else
        disp('invalide image_path')
    end
end
