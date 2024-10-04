# Use a Linux Distro as a parent image
FROM ubuntu:16.04

# Set up
RUN apt-get update && apt-get install -y git wget build-essential g++ gcc cmake curl clang && \
    apt-get install -y libfreetype6-dev apt-utils pkg-config vim gfortran && \
    apt-get install -y binutils make linux-source unzip && \
    apt install -y libsm6 libxext6 libfontconfig1 libxrender1 libgl1-mesa-glx && \
    apt-get install -y python3-pip python3-dev && \
    cd /usr/local/bin/ && \
    ln -s /usr/bin/python3 python && \
    pip3 install --upgrade pip==20.3.4 && \
    cd ~
    
# Install c3d
RUN wget https://downloads.sourceforge.net/project/c3d/c3d/Nightly/c3d-nightly-Linux-x86_64.tar.gz && \
    tar -xzvf c3d-nightly-Linux-x86_64.tar.gz && mv c3d-1.1.0-Linux-x86_64 /opt/c3d && \
    rm c3d-nightly-Linux-x86_64.tar.gz
ENV PATH=/opt/c3d/bin:${PATH}

# Install FSL
RUN apt-get update && apt-get install -y fsl

ENV FSLDIR="/usr/share/fsl/5.0" \
    FSLOUTPUTTYPE="NIFTI_GZ" \
    FSLMULTIFILEQUIT="TRUE" \
    POSSUMDIR="/usr/share/fsl/5.0" \
    LD_LIBRARY_PATH="/usr/lib/fsl/5.0:$LD_LIBRARY_PATH" \
    FSLTCLSH="/usr/bin/tclsh" \
    FSLWISH="/usr/bin/wish" \
    POSSUMDIR="/usr/share/fsl/5.0"

ENV PATH="/usr/lib/fsl/5.0:${PATH}"

# Install ANTs
ENV ANTSPATH="/opt/ANTs"
ENV ANTSTAR="/opt/ants.tar.gz"
RUN mkdir -p "${ANTSPATH}" && \
    wget --no-check-certificate -q --show-progress -O "${ANTSTAR}" https://huggingface.co/datasets/AICONSlab/icvmapper/resolve/dev/software/ANTs/ANTs-Linux-centos5_x86_64-v2.2.0-0740f91.tar.gz && \
    tar -xzvf "${ANTSTAR}" -C "${ANTSPATH}" --strip-components 1
ENV PATH=${ANTSPATH}:${PATH}

# Install all needed packages based on pip installation
COPY requirements.txt ./
RUN python3 -m pip install --no-cache-dir -r requirements.txt
#COPY . .

# Download models, store in directory

RUN mkdir -p /src/icvmapp3r/models && \
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1XJqs_kagiXQPxm_kbUiCMayputKKDP99' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1XJqs_kagiXQPxm_kbUiCMayputKKDP99" -O /src/icvmapp3r/models/hfb_t1only_mcdp_224iso_multi_model_weights.h5 && \
    rm -rf /tmp/cookies.txt && \
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1vygaxGmdN-FY3IDCKv_IugDSTSc-bupk' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1vygaxGmdN-FY3IDCKv_IugDSTSc-bupk" -O /src/icvmapp3r/models/hfb_t1only_mcdp_224iso_multi_model.json && \
    rm -rf /tmp/cookies.txt && \
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1kgWMeTqpSlhTLIqBqpkhES1593Mb689x' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1kgWMeTqpSlhTLIqBqpkhES1593Mb689x" -O /src/icvmapp3r/models/hfb_t1only_mcdp_224iso_contrast_model_weights.h5 && \
    rm -rf /tmp/cookies.txt && \
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1dT6CKEgR0a18VQO9HIKixJcVu8jnFA1I' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1dT6CKEgR0a18VQO9HIKixJcVu8jnFA1I" -O /src/icvmapp3r/models/hfb_t1only_mcdp_224iso_contrast_model.json && \
    rm -rf /tmp/cookies.txt && \
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1trZghBXf2Hsbd_AW_9eJ2mpeYGP3gx0k' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1trZghBXf2Hsbd_AW_9eJ2mpeYGP3gx0k" -O /src/icvmapp3r/models/hfb_t1fl_mcdp_multi_model_weights.h5 && \
    rm -rf /tmp/cookies.txt && \
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1VODDQlLRL-uDiYrvRLmKKaLaChNGrhYv' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1VODDQlLRL-uDiYrvRLmKKaLaChNGrhYv" -O /src/icvmapp3r/models/hfb_t1fl_mcdp_multi_model.json && \
    rm -rf /tmp/cookies.txt && \
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1haiul6JK6m4Z7qmTb1FZf4x6mF7GPBrp' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1haiul6JK6m4Z7qmTb1FZf4x6mF7GPBrp" -O /src/icvmapp3r/models/hfb_t1flt2_mcdp_contrast_model_weights.h5 && \
    rm -rf /tmp/cookies.txt && \
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1rSWXdBCBab79ZspDURe6HBVnDRVkx_Iw' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1rSWXdBCBab79ZspDURe6HBVnDRVkx_Iw" -O /src/icvmapp3r/models/hfb_t1flt2_mcdp_contrast_model.json && \
    rm -rf /tmp/cookies.txt && \
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1h-5py1kYYpj2dtALVWvqTQgMt6v-3YRZ' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1h-5py1kYYpj2dtALVWvqTQgMt6v-3YRZ" -O /src/icvmapp3r/models/hfb_t1only_mcdp_multi_model_weights.h5 && \
    rm -rf /tmp/cookies.txt && \
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1ohpclEIAw2_aOgwbKelE5Il_E1KCYfl2' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1ohpclEIAw2_aOgwbKelE5Il_E1KCYfl2" -O /src/icvmapp3r/models/hfb_t1only_mcdp_multi_model.json && \
    rm -rf /tmp/cookies.txt && \
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1IoR8PpTjf4UtZXJo5iNrSRznQk8xcHlh' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1IoR8PpTjf4UtZXJo5iNrSRznQk8xcHlh" -O /src/icvmapp3r/models/hfb_t1t2_mcdp_multi_model_weights.h5 && \
    rm -rf /tmp/cookies.txt && \
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1wDFsMGxXZeqdrU3Ic2ITQztU772Vy8Hu' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1wDFsMGxXZeqdrU3Ic2ITQztU772Vy8Hu" -O /src/icvmapp3r/models/hfb_t1t2_mcdp_multi_model.json && \
    rm -rf /tmp/cookies.txt
    
RUN set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        fsl-core \
        '^libxcb.*-dev' \
        libx11-xcb-dev \
        libglu1-mesa-dev \
        libxrender-dev \
        libxi-dev \
        libxkbcommon-dev \
        libxkbcommon-x11-dev \
        libxinerama-dev 

# Run icvmapper when the container launches
ENTRYPOINT ["/bin/bash"]
