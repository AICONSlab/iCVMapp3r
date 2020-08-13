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
    pip3 install --upgrade pip && \
    cd ~

# Install c3d
RUN wget https://downloads.sourceforge.net/project/c3d/c3d/Nightly/c3d-nightly-Linux-x86_64.tar.gz && \
    tar -xzvf c3d-nightly-Linux-x86_64.tar.gz && mv c3d-1.1.0-Linux-x86_64 /opt/c3d && \
    rm c3d-nightly-Linux-x86_64.tar.gz
ENV PATH /opt/c3d/bin:${PATH}

# FSL
# Installing Neurodebian packages FSL
# RUN wget -O- http://neuro.debian.net/lists/xenial.us-tn.full | tee /etc/apt/sources.list.d/neurodebian.sources.list
# RUN apt-key adv --recv-keys --keyserver hkp://pool.sks-keyservers.net:80 0xA5D32F012649A5A9

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
ENV ANTSPATH /opt/ANTs
RUN mkdir -p /opt/ANTs && \
    curl -sSL "https://dl.dropbox.com/s/2f4sui1z6lcgyek/ANTs-Linux-centos5_x86_64-v2.2.0-0740f91.tar.gz" \
    | tar -xzC $ANTSPATH --strip-components 1
ENV PATH=${ANTSPATH}:${PATH}

# Install all needed packages based on pip installation
COPY requirements.txt ./
RUN python3 -m pip install --no-cache-dir -r requirements.txt
COPY . .

# Download models, store in directory
# RUN mkdir -p /src/icvmapp3r/models && \
#     wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1Ulx07FlY7Zw5ragIMjQFIYYytGaJPvPq' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1Ulx07FlY7Zw5ragIMjQFIYYytGaJPvPq" -O /src/icvmapp3r/models/hfb_multi_mcdp_model_weights.h5 && \
#     rm -rf /tmp/cookies.txt && \
#     wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=19zEi7552X93_5JbEokfry2Y28gFeVGt2' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=19zEi7552X93_5JbEokfry2Y28gFeVGt2" -O /src/icvmapp3r/models/hfb_multi_mcdp_model.json && \
#     rm -rf /tmp/cookies.txt && \
#     wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1AZSAHty7caxVps7lJ8m0KWeUStwQrdvA' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1AZSAHty7caxVps7lJ8m0KWeUStwQrdvA" -O /src/icvmapp3r/models/hfb_multi_model_weights.h5 && \
#     rm -rf /tmp/cookies.txt && \
#     wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1_AhrxCC7kQKQPw6AlIIbp-NLwIrMTYgs' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1_AhrxCC7kQKQPw6AlIIbp-NLwIrMTYgs" -O /src/icvmapp3r/models/hfb_multi_model.json && \
#     rm -rf /tmp/cookies.txt && \
#     wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1ZQN2zn2o1DSVLhsMbUIzAtwoUu9IhqB8' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1ZQN2zn2o1DSVLhsMbUIzAtwoUu9IhqB8" -O /src/icvmapp3r/models/hfb_t1only_mcdp_model_weights.h5 && \
#     rm -rf /tmp/cookies.txt && \
#     wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1LppC8pEWSgByKF683hd7F5e8Gv8CuK6m' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1LppC8pEWSgByKF683hd7F5e8Gv8CuK6m" -O /src/icvmapp3r/models/hfb_t1only_mcdp_model.json && \
#     rm -rf /tmp/cookies.txt && \
#     wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1AEoo8kuDCLQYDkfpwE2qYzDsIZYlxaVV' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1AEoo8kuDCLQYDkfpwE2qYzDsIZYlxaVV" -O /src/icvmapp3r/models/hfb_t1only_model_weights.h5 && \
#     rm -rf /tmp/cookies.txt && \
#     wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1BXmYdr4U-SQYZIChPesDfFYzuTXg63kn' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1BXmYdr4U-SQYZIChPesDfFYzuTXg63kn" -O /src/icvmapp3r/models/hfb_t1only_model.json && \
#     rm -rf /tmp/cookies.txt && \
#     wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1W2WdayviLfFf9iTbw-LhoaduPeOseVj0' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1W2WdayviLfFf9iTbw-LhoaduPeOseVj0" -O /src/icvmapp3r/models/hfb_t1t2_mcdp_model_weights.h5 && \
#     rm -rf /tmp/cookies.txt && \
#     wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1esnItqZ2UdfamMy2ZXOMEIL-F25sz8sp' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1esnItqZ2UdfamMy2ZXOMEIL-F25sz8sp" -O /src/icvmapp3r/models/hfb_t1t2_mcdp_model.json && \
#     rm -rf /tmp/cookies.txt && \
#     wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1RDzWto5236l158K6nAaEpd8wtP93i9bU' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1RDzWto5236l158K6nAaEpd8wtP93i9bU" -O /src/icvmapp3r/models/hfb_t1t2_model_weights.h5 && \
#     rm -rf /tmp/cookies.txt && \
#     wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1BY9Iql0soAvv7MFRPQEW8G-CSn00VojA' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1BY9Iql0soAvv7MFRPQEW8G-CSn00VojA" -O /src/icvmapp3r/models/hfb_t1t2_model.json && \
#     rm -rf /tmp/cookies.txt && \
#     wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1JOYGCa97qnibSMnfQuRNvbHhy6xBTqPl' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1JOYGCa97qnibSMnfQuRNvbHhy6xBTqPl" -O /src/icvmapp3r/models/hfb_t1fl_mcdp_model_weights.h5 && \
#     rm -rf /tmp/cookies.txt && \
#     wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1TaJaLp_BysEX0LkgQ07MAcLQzSwHRgRW' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1TaJaLp_BysEX0LkgQ07MAcLQzSwHRgRW" -O /src/icvmapp3r/models/hfb_t1fl_mcdp_model.json && \
#     rm -rf /tmp/cookies.txt
RUN mkdir -p /src/icvmapp3r/models && \
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

# Run icvmapper when the container launches
ENTRYPOINT /bin/bash
