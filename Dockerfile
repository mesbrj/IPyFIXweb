# Confiigure/compiling/installing RRDtool, IPFIX, libpcap and dependencies
FROM python:3.12-slim AS BuildStage

RUN if [ ! -d "/usr/lib/x86_64-linux-gnu/pkgconfig" ]; then \
        echo "No pkgconfig in base image"; fi \
&& apt-get update && apt-get upgrade -y && apt-get install -y \
curl gcc perl make gperf gettext python3 python3-pip flex bison \
python3-setuptools python3-wheel ninja-build git groff-base \
&& pip install meson && pip install packaging && pip install setuptools \
&& if [ -d "/usr/lib/x86_64-linux-gnu/pkgconfig" ]; then \
        rm -frv /usr/lib/x86_64-linux-gnu/pkgconfig; \
        echo "Removed the default pkgconfig metadata of base image"; fi

ENV PATH=/opt/bin:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV PKG_CONFIG_PATH=/opt/lib/pkgconfig
ENV PKG_CONFIG=/opt/bin/pkg-config
ENV C_INCLUDE_PATH=/opt/include
ENV CPATH=/opt/include
ENV LD_LIBRARY_PATH=/opt/lib
ENV LDFLAGS=-L/opt/lib

## configure/compiling/install pkgconfig to /opt
## https://pkgconfig.freedesktop.org/releases/pkg-config-0.29.2.tar.gz
RUN mkdir -p /ipyfix_build/pkgconfig && cd /ipyfix_build/pkgconfig \
&& curl -LJO https://pkgconfig.freedesktop.org/releases/pkg-config-0.29.2.tar.gz \
&& tar -xzf pkg-config-0.29.2.tar.gz && cd pkg-config-0.29.2 \
&& ./configure --prefix=/opt --with-internal-glib \
&& make && make install

## configure/compiling/install zlib to /opt
## https://zlib.net/zlib-1.3.1.tar.gz
RUN mkdir -p /ipyfix_build/zlib && cd /ipyfix_build/zlib \
&& curl -LJO https://zlib.net/zlib-1.3.1.tar.gz \
&& tar -xzf zlib-1.3.1.tar.gz && cd zlib-1.3.1 \
&& ./configure --prefix=/opt \
&& make && make install

## configure/compiling/install libpng to /opt
## https://download.sourceforge.net/libpng/libpng-1.6.48.tar.gz
RUN mkdir -p /ipyfix_build/libpng && cd /ipyfix_build/libpng \
&& curl -LJO https://download.sourceforge.net/libpng/libpng-1.6.48.tar.gz \
&& tar -xzf libpng-1.6.48.tar.gz && cd libpng-1.6.48 \
&& ./configure --prefix=/opt --with-zlib-prefix=/opt/lib --with-pkgconfigdir=/opt/lib/pkgconfig \
&& make && make install

## configure/compiling/install freetype to /opt
## https://download.savannah.gnu.org/releases/freetype/freetype-2.13.3.tar.gz
RUN mkdir -p /ipyfix_build/freetype && cd /ipyfix_build/freetype \
&& curl -LJO https://download.savannah.gnu.org/releases/freetype/freetype-2.13.3.tar.gz \
&& tar -xzf freetype-2.13.3.tar.gz && cd freetype-2.13.3 \
&& ./configure --prefix=/opt --with-zlib=yes --with-png=yes \
&& make && make install

### configure/compiling/install LibXML2 to /opt
### https://download.gnome.org/sources/libxml2/2.14/libxml2-2.14.3.tar.xz
RUN mkdir -p /ipyfix_build/libxml2 && cd /ipyfix_build/libxml2 \
&& curl -LJO https://download.gnome.org/sources/libxml2/2.14/libxml2-2.14.3.tar.xz \
&& tar -xJf libxml2-2.14.3.tar.xz && cd libxml2-2.14.3 \
&& ./configure --prefix=/opt --with-zlib=/opt/lib --with-python=no \
&& make && make install

### configure/compiling/install fontconfig to /opt
### https://www.freedesktop.org/software/fontconfig/release/fontconfig-2.15.0.tar.gz
RUN mkdir -p /ipyfix_build/fontconfig && cd /ipyfix_build/fontconfig \
&& curl -LJO https://www.freedesktop.org/software/fontconfig/release/fontconfig-2.15.0.tar.gz \
&& tar -xzf fontconfig-2.15.0.tar.gz && cd fontconfig-2.15.0 \
&& ./configure --prefix=/opt --enable-libxml2 --with-pkgconfigdir=/opt/lib/pkgconfig \
&& make && make install

### configure/compiling/install Pixman to /opt | After installing: /opt (45MB), /opt/lib (34MB)
### https://cairographics.org/releases/pixman-0.42.2.tar.gz
RUN mkdir -p /ipyfix_build/pixman && cd /ipyfix_build/pixman \
&& curl -LJO https://cairographics.org/releases/pixman-0.42.2.tar.gz \
&& tar -xzf pixman-0.42.2.tar.gz && cd pixman-0.42.2 \
&& ./configure --prefix=/opt --enable-libpng \
&& make && make install

### configure/compiling/install PCRE2 to /opt | After installing: /opt (51MB), /opt/lib (37MB)
### https://github.com/PCRE2Project/pcre2
RUN mkdir -p /ipyfix_build/pcre2_build && cd /ipyfix_build/pcre2_build \
&& git clone https://github.com/PCRE2Project/pcre2.git ./pcre2 --branch pcre2-10.45 -c advice.detachedHead=false --depth 1 \
&& cd /ipyfix_build/pcre2_build/pcre2 \
&& ./configure --prefix=/opt --enable-pcre2grep-libz --enable-utf --enable-unicode-properties --enable-pcre2-16 --enable-pcre2-32 \
&& make && make install

## configure/compiling/install Glib to /opt | After installing: /opt (83MB), /opt/lib (53MB)
## https://download.gnome.org/sources/glib/2.80/glib-2.80.4.tar.xz
RUN mkdir -p /ipyfix_build/glib && cd /ipyfix_build/glib \
&& curl -LJO https://download.gnome.org/sources/glib/2.80/glib-2.80.4.tar.xz \
&& tar -xJf glib-2.80.4.tar.xz && cd glib-2.80.4 \
&& meson setup --prefix=/opt --libdir=lib --pkg-config-path=/opt/lib/pkgconfig --build.pkg-config-path=/opt/lib/pkgconfig _build \
&& meson compile -C _build && meson install -C _build

### configure/compiling/install Cairo to /opt | After installing: /opt (87MB), /opt/lib (57MB)
### https://www.cairographics.org/releases/cairo-1.18.4.tar.xz
RUN mkdir -p /ipyfix_build/cairo && cd /ipyfix_build/cairo \
&& curl -LJO https://www.cairographics.org/releases/cairo-1.18.4.tar.xz \
&& tar -xJf cairo-1.18.4.tar.xz && cd cairo-1.18.4 \
&& meson setup --prefix=/opt --libdir=lib --pkg-config-path=/opt/lib/pkgconfig --build.pkg-config-path=/opt/lib/pkgconfig _build \
&& meson compile -C _build && meson install -C _build

### configure/compiling/install Pango to /opt | After installing: /opt (156MB), /opt/lib (123MB)
### https://download.gnome.org/sources/pango/1.56/pango-1.56.3.tar.xz
RUN mkdir -p /ipyfix_build/pango && cd /ipyfix_build/pango \
&& curl -LJO https://download.gnome.org/sources/pango/1.56/pango-1.56.3.tar.xz \
&& tar -xJf pango-1.56.3.tar.xz && cd pango-1.56.3 \
&& meson setup --prefix=/opt --libdir=lib --pkg-config-path=/opt/lib/pkgconfig --build.pkg-config-path=/opt/lib/pkgconfig _build \
&& meson compile -C _build  && meson install -C _build

## Build/Install for RRDTool and its Python bindings | After installing: /opt (161MB), /opt/lib (126MB)
## https://github.com/oetiker/rrdtool-1.x/releases/download/v1.9.0/rrdtool-1.9.0.tar.gz
RUN mkdir -p /ipyfix_build/rrd && cd /ipyfix_build/rrd \
&& curl -LJO https://github.com/oetiker/rrdtool-1.x/releases/download/v1.9.0/rrdtool-1.9.0.tar.gz \
&& tar -xzf rrdtool-1.9.0.tar.gz && cd rrdtool-1.9.0 \
&& ./configure --prefix=/opt --disable-python --disable-perl \
&& make && make install \
&& pip install rrdtool-bindings && pip freeze

## Using the same openSSL install as the used in the base image.
RUN apt-get install -y libssl-dev
ENV OPENSSL_CFLAGS=-I/usr/include/openssl
ENV OPENSSL_LIBS=-L/lib/x86_64-linux-gnu

## Build/Install for libpcap | After installing: /opt (165MB), /opt/lib (130MB)
## https://www.tcpdump.org/release/libpcap-1.10.5.tar.xz
RUN mkdir -p /ipyfix_build/libpcap && cd /ipyfix_build/libpcap \
&& curl -LJO https://www.tcpdump.org/release/libpcap-1.10.5.tar.xz \
&& tar -xJf libpcap-1.10.5.tar.xz && cd libpcap-1.10.5 \
&& ./configure --prefix=/opt \
&& make && make install

## configure/compiling/install fixbuf-lib to /opt | After installing: /opt (167MB), /opt/lib (131MB)
## https://tools.netsa.cert.org/releases/libfixbuf-3.0.0.alpha2.tar.gz
RUN mkdir -p /ipyfix_build/fixbuf && cd /ipyfix_build/fixbuf \
&& curl -LJO https://tools.netsa.cert.org/releases/libfixbuf-3.0.0.alpha2.tar.gz \
&& tar -xzf libfixbuf-3.0.0.alpha2.tar.gz && cd libfixbuf-3.0.0.alpha2 \
&& ./configure --prefix=/opt --with-openssl=/usr/bin/openssl \
&& make && make install

## configure/compiling/install fixbuf-lib Python bindings
## https://tools.netsa.cert.org/releases/pyfixbuf-0.9.0.tar.gz
RUN mkdir -p /ipyfix_build/pyfixbuf && cd /ipyfix_build/pyfixbuf \
&& curl -LJO https://tools.netsa.cert.org/releases/pyfixbuf-0.9.0.tar.gz \
&& tar -xzf pyfixbuf-0.9.0.tar.gz ; cd pyfixbuf-0.9.0 \
&& python setup.py build && python setup.py install && pip freeze

## configure/compiling/install PCRE to /opt | After installing: /opt (182MB), /opt/lib (143MB)
## https://sourceforge.net/projects/pcre/files/pcre/8.45/pcre-8.45.tar.bz2
RUN mkdir -p /ipyfix_build/pcre && cd /ipyfix_build/pcre \
&& curl -LJO https://sourceforge.net/projects/pcre/files/pcre/8.45/pcre-8.45.tar.bz2 \
&& tar -xjf pcre-8.45.tar.bz2 && cd pcre-8.45 \
&& ./configure --prefix=/opt --enable-pcregrep-libz --enable-utf8 --enable-unicode-properties \ 
--enable-jit --enable-pcre16 --enable-pcre32 \
&& make && make install

## configure/compiling/install YAF application to /opt
## https://tools.netsa.cert.org/releases/yaf-3.0.0.alpha4.tar.gz
RUN mkdir -p /ipyfix_build/yaf && cd /ipyfix_build/yaf \
&& curl -LJO https://tools.netsa.cert.org/releases/yaf-3.0.0.alpha4.tar.gz \
&& tar -xzf yaf-3.0.0.alpha4.tar.gz && cd yaf-3.0.0.alpha4 \
&& ./configure --prefix=/opt  --enable-plugins --enable-applabel --enable-dpi --enable-mpls \
--with-libpcap=/opt --with-openssl=/usr/bin --with-zlib=/opt \
&& make && make install

## After configure/compiling/install (build) stage: 
## /opt (186 MB): /opt/lib (146 MB), /opt/include (7.0MB), /opt/bin (8.4 MB)

## Final Stage. Finish installation: Copies (layers, repo files),
## install python packages (requirements.txt) and run.

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PATH=/opt/bin:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV LD_LIBRARY_PATH=/opt/lib

COPY --from=BuildStage /opt /opt
COPY --from=BuildStage /usr/local/lib/python3.12/site-packages/rrdtool /usr/local/lib/python3.12/site-packages/rrdtool
COPY --from=BuildStage /usr/local/lib/python3.12/site-packages/rrdtool_bindings-0.3.1.dist-info /usr/local/lib/python3.12/site-packages/rrdtool_bindings-0.3.1.dist-info
COPY --from=BuildStage /usr/local/lib/python3.12/site-packages/rrdtool.cpython-312-x86_64-linux-gnu.so /usr/local/lib/python3.12/site-packages/rrdtool.cpython-312-x86_64-linux-gnu.so
COPY --from=BuildStage /usr/local/lib/python3.12/site-packages/pyfixbuf /usr/local/lib/python3.12/site-packages/pyfixbuf
COPY --from=BuildStage /usr/local/lib/python3.12/site-packages/pyfixbuf-0.9.0-py3.12.egg-info /usr/local/lib/python3.12/site-packages/pyfixbuf-0.9.0-py3.12.egg-info
COPY --from=BuildStage /usr/local/lib/python3.12/site-packages/src/pyfixbuf /usr/local/lib/python3.12/site-packages/src/pyfixbuf

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt \
&& useradd ipyfix \
&& mkdir -p /var/ipyfix/service \
&& mkdir /var/ipyfix/admin \
&& mkdir /var/ipyfix/tenants \
&& chown -R ipyfix: /app /var/ipyfix \
&& pip freeze

USER ipyfix

ENTRYPOINT ["python", "src/cmd/main.py"]