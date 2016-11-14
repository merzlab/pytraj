#!/usr/bin/env bash

# PLEASE NOTE: This script was adapted from output generated by conda-smithy.

FEEDSTOCK_ROOT=$(cd "$(dirname "$0")/.."; pwd;)
CPPTRAJ_RECIPE=$FEEDSTOCK_ROOT/devtools/conda-recipe/libcpptraj
PYTRAJ_RECIPE=$FEEDSTOCK_ROOT/devtools/conda-recipe/pytraj

docker info

config=$(cat <<CONDARC

channels:
 - defaults # As we need conda-build

 - conda-forge

conda-build:
 root-dir: /feedstock_root/build_artefacts

show_channel_urls: true

CONDARC
)

cat << EOF | docker run -i \
                        -v ${CPPTRAJ_RECIPE}:/cpptraj_recipe \
                        -v ${FEEDSTOCK_ROOT}:/feedstock_root \
                        -a stdin -a stdout -a stderr \
                        condaforge/linux-anvil \
                        bash || exit $?

export PYTHONUNBUFFERED=1

echo "$config" > ~/.condarc
# A lock sometimes occurs with incomplete builds. The lock file is stored in build_artefacts.
conda clean --lock

conda update --yes --all
conda install --yes conda-build
conda info

# Embarking on 1 case(s).
    conda build /cpptraj_recipe --quiet || exit 1
    conda build /feedstock_root/devtools/conda-recipe/pytraj --quiet || exit 1
    cp /opt/conda/conda-bld/linux-64/pytraj*  /feedstock_root/
    cp /opt/conda/conda-bld/linux-64/libcpptraj* /feedstock_root/
EOF