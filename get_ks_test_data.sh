rm -rf ~/.kilosort

mkdir -p ~/.kilosort/.test_data
wget https://osf.io/download/67effd64f74150d8738b7f34/ -O ~/.kilosort/.test_data/ZFM-02370_mini.imec0.ap.short.bin.zip
unzip ~/.kilosort/.test_data/ZFM-02370_mini.imec0.ap.short.bin.zip -d ~/.kilosort/.test_data

mkdir -p ~/.kilosort/probes
wget https://osf.io/download/67f012cc7e1fd38cad82980a/ -O ~/.kilosort/probes/NeuroPix1_default.mat

ls -alt ~/.kilosort/.test_data/
ls -alt ~/.kilosort/probes/
