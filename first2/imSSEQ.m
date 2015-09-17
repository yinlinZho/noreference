function score = imSSEQ( filename )
    
    image = imread(filename);
    score = SSEQ(image);
    
end