function delete_parpool()
    poolobj = gcp('nocreate')
    delete(poolobj)