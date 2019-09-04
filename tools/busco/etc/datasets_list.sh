#!/usr/bin/env bash

# Bacteria
wget http://busco.ezlab.org/v2/datasets/bacteria_odb9.tar.gz
wget http://busco.ezlab.org/v2/datasets/proteobacteria_odb9.tar.gz
wget http://busco.ezlab.org/v2/datasets/rhizobiales_odb9.tar.gz
wget http://busco.ezlab.org/v2/datasets/betaproteobacteria_odb9.tar.gz
wget http://busco.ezlab.org/v2/datasets/gammaproteobacteria_odb9.tar.gz
wget http://busco.ezlab.org/v2/datasets/enterobacteriales_odb9.tar.gz
wget http://busco.ezlab.org/v2/datasets/deltaepsilonsub_odb9.tar.gz
wget http://busco.ezlab.org/v2/datasets/actinobacteria_odb9.tar.gz
wget http://busco.ezlab.org/v2/datasets/cyanobacteria_odb9.tar.gz
wget http://busco.ezlab.org/v2/datasets/firmicutes_odb9.tar.gz
wget http://busco.ezlab.org/v2/datasets/clostridia_odb9.tar.gz
wget http://busco.ezlab.org/v2/datasets/lactobacillales_odb9.tar.gz
wget http://busco.ezlab.org/v2/datasets/bacillales_odb9.tar.gz
wget http://busco.ezlab.org/v2/datasets/bacteroidetes_odb9.tar.gz
wget http://busco.ezlab.org/v2/datasets/spirochaetes_odb9.tar.gz
wget http://busco.ezlab.org/v2/datasets/tenericutes_odb9.tar.gz
        
# # Eukaryota
# wget http://busco.ezlab.org/v2/datasets/eukaryota_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/fungi_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/microsporidia_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/dikarya_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/ascomycota_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/pezizomycotina_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/eurotiomycetes_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/sordariomyceta_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/saccharomyceta_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/saccharomycetales_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/basidiomycota_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/metazoa_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/nematoda_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/arthropoda_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/insecta_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/endopterygota_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/hymenoptera_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/diptera_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/vertebrata_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/actinopterygii_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/tetrapoda_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/aves_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/mammalia_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/euarchontoglires_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/laurasiatheria_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/embryophyta_odb9.tar.gz
# wget http://busco.ezlab.org/v2/datasets/protists_ensembl.tar.gz
# wget http://busco.ezlab.org/v2/datasets/alveolata_stramenophiles_ensembl.tar.gz
    

for f in *.tar.gz; do tar -xzvf "$f"; done