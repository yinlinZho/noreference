function image_paths = multi(rootpath)
    disp 'Reading image_rootpath'
    rootpath
    if(isdir(rootpath))
            image_rootpaths = dir(rootpath);
            image_rootpaths = {image_rootpaths.name}';
            len = numel(image_rootpaths);
             for i = 1:len
                 image_rootpaths{i} = [rootpath,'\',image_rootpaths{i}];
             end
             numel(image_rootpaths)
             image_paths = image_rootpaths;
    end
end

