mkdir -p kilosort_test_data
wget https://osf.io/download/67effd64f74150d8738b7f34/ -O kilosort_test_data/ZFM-02370_mini.imec0.ap.short.bin.zip
unzip kilosort_test_data/ZFM-02370_mini.imec0.ap.short.bin.zip -d kilosort_test_data

mkdir -p kilosort_test_data/probes
wget https://osf.io/download/67f012cc7e1fd38cad82980a/ -O kilosort_test_data/probes/NeuroPix1_default.mat

ls -alt kilosort_test_data/
ls -alt kilosort_test_data/probes/
