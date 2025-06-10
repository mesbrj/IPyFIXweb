# Build/Install stage for IPFIX libs and applications
FROM python:3.12-slim as BuildStage

RUN apt-get update && apt-get upgrade -y && apt-get install -y \
perl make gcc libssl-dev libglib2.0-dev libpcap-dev libpcre3-dev \
curl xsltproc \
&& pip install setuptools \
# configure/compiling/install fixbuf-lib to /opt
&& mkdir -p /ipfix_build/fixbuf && cd /ipfix_build/fixbuf \
&& curl -LJO https://tools.netsa.cert.org/releases/libfixbuf-3.0.0.alpha2.tar.gz \
&& tar -xzf libfixbuf-3.0.0.alpha2.tar.gz && cd libfixbuf-3.0.0.alpha2 \
&& ./configure --prefix=/opt --with-openssl=/usr/bin/openssl \
&& make && make install \
&& export LD_LIBRARY_PATH=/opt/lib && export PKG_CONFIG_PATH=/opt/lib/pkgconfig \
# configure/compiling/install fixbuf-lib Python bindings
&& mkdir -p /ipfix_build/pyfixbuf && cd /ipfix_build/pyfixbuf \
&& curl -LJO https://tools.netsa.cert.org/releases/pyfixbuf-0.9.0.tar.gz \
&& tar -xzf pyfixbuf-0.9.0.tar.gz ; cd pyfixbuf-0.9.0 \
&& python setup.py build && python setup.py install \
# configure/compiling/install YAF application
&& mkdir -p /ipfix_build/yaf && cd /ipfix_build/yaf \
&& curl -LJO https://tools.netsa.cert.org/releases/yaf-3.0.0.alpha4.tar.gz \
&& tar -xzf yaf-3.0.0.alpha4.tar.gz && cd yaf-3.0.0.alpha4 \
&& ./configure --prefix=/opt --enable-plugins --enable-applabel --enable-dpi --with-libpcap=/usr/include --with-openssl=/usr/bin \
&& make && make install

# Finish install and run stage
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV LD_LIBRARY_PATH=/opt/lib

COPY --from=BuildStage /opt /opt
COPY --from=BuildStage /usr/bin/xsltproc /usr/bin/xsltproc
COPY --from=BuildStage /usr/local/lib/python3.12/site-packages/src/pyfixbuf /usr/local/lib/python3.12/site-packages/src/pyfixbuf
COPY --from=BuildStage /usr/local/lib/python3.12/site-packages/pyfixbuf /usr/local/lib/python3.12/site-packages/pyfixbuf
COPY --from=BuildStage /usr/local/lib/python3.12/site-packages/pyfixbuf-0.9.0-py3.12.egg-info /usr/local/lib/python3.12/site-packages/pyfixbuf-0.9.0-py3.12.egg-info
COPY . /app

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && apt-get install -y gcc librrd-dev \
&& pip install --no-cache-dir -r requirements.txt \
&& useradd ipyfix \
&& mkdir -p /var/ipyfix/service \
&& mkdir -p /var/ipyfix/admin \
&& mkdir -p /var/ipyfix/tenants \
&& chown -R ipyfix: /app /var/ipyfix

USER ipyfix

ENTRYPOINT ["python", "src/cmd/main.py"]
