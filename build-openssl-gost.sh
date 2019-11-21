#/bin/sh

echo "1 Install dependences"
apt-get update && apt-get install \
    build-essential \
    cmake \
    gcc \
    unzip \
    wget -y

echo "2 Build openssl"
PREFIX="/usr/local/ssl"
OPEN_SSL_VERSION="3f8907e459313f0b3df3b328f0a16db565fbcea0"
wget "https://github.com/openssl/openssl/archive/${OPEN_SSL_VERSION}.zip" -O openssl.zip \
  && unzip openssl.zip -d ./ \
  && cd "openssl-${OPEN_SSL_VERSION}" \
  && ./config shared -d --prefix=${PREFIX} --openssldir=${PREFIX} && make -j$(nproc) all && make install \
  && mv /usr/bin/openssl /root/ \
  && ln -s /usr/local/ssl/bin/openssl /usr/bin/openssl

echo "2.1 Update path of shared libraries"
echo "/usr/local/ssl/lib" >> /etc/ld.so.conf.d/ssl.conf && ldconfig

echo "3 Build GOST-engine for OpenSSL"
ENGINES=/usr/local/ssl/lib/engines-3
GOST_ENGINE_VERSION=58a46b289d6b8df06072fc9c0304f4b2d3f4b051
apt-get update && apt-get install cmake gcc -y \
  && cd /usr/local/src \
  && wget "https://github.com/gost-engine/engine/archive/${GOST_ENGINE_VERSION}.zip" -O gost-engine.zip \
  && unzip gost-engine.zip -d ./ \
  && cd "engine-${GOST_ENGINE_VERSION}" \
  && sed -i 's|printf("GOST engine already loaded\\n");|goto end;|' gost_eng.c \
  && mkdir build \
  && cd build \
  && cmake -DCMAKE_BUILD_TYPE=Release \
   -DOPENSSL_ROOT_DIR=/usr/local/ssl -DOPENSSL_LIBRARIES=/usr/local/ssl/lib -DOPENSSL_ENGINES_DIR=${ENGINES} .. \
  && cmake --build . --config Release \
  && cd bin \
  && cp gostsum gost12sum /usr/local/bin \
  && cd .. \
  && cp bin/gost.so "${ENGINES}" \
  && rm -rf "/usr/local/src/gost-engine.zip" "/usr/local/src/engine-${GOST_ENGINE_VERSION}"

echo "3.1 Enable GOST-engine"
sed -i '6i openssl_conf=openssl_def' /usr/local/ssl/openssl.cnf \
  && echo "" >> /usr/local/ssl/openssl.cnf \
  && echo "# OpenSSL default section" >> /usr/local/ssl/openssl.cnf \
  && echo "[openssl_def]" >> /usr/local/ssl/openssl.cnf \
  && echo "engines = engine_section" >> /usr/local/ssl/openssl.cnf \
  && echo "" >> /usr/local/ssl/openssl.cnf \
  && echo "# Engine scetion" >> /usr/local/ssl/openssl.cnf \
  && echo "[engine_section]" >> /usr/local/ssl/openssl.cnf \
  && echo "gost = gost_section" >> /usr/local/ssl/openssl.cnf \
  && echo "" >> /usr/local/ssl/openssl.cnf \
  && echo "# Engine gost section" >> /usr/local/ssl/openssl.cnf \
  && echo "[gost_section]" >> /usr/local/ssl/openssl.cnf \
  && echo "engine_id = gost" >> /usr/local/ssl/openssl.cnf \
  && echo "dynamic_path = ${ENGINES}/gost.so" >> /usr/local/ssl/openssl.cnf \
  && echo "default_algorithms = ALL" >> /usr/local/ssl/openssl.cnf \
  && echo "CRYPT_PARAMS = id-Gost28147-89-CryptoPro-A-ParamSet" >> /usr/local/ssl/openssl.cnf

echo "4 Rebuild curl"
CURL_VERSION=7.67.0
apt-get remove curl -y \
  && rm -rf /usr/local/include/curl \
  && cd /usr/local/src \
  && wget "https://curl.haxx.se/download/curl-${CURL_VERSION}.tar.gz" -O "curl-${CURL_VERSION}.tar.gz" \
  && tar -zxvf "curl-${CURL_VERSION}.tar.gz" \
  && cd "curl-${CURL_VERSION}" \
  && CPPFLAGS="-I/usr/local/ssl/include" \
     LDFLAGS="-L/usr/local/ssl/lib -Wl,-rpath,/usr/local/ssl/lib" \
     LD_LIBRARY_PATH=/usr/local/ssl/lib \
     ./configure --prefix=/usr/local/curl --with-ssl=/usr/local/ssl --with-libssl-prefix=/usr/local/ssl \
  && make \
  && make install \
  && ln -s /usr/local/curl/bin/curl /usr/bin/curl \
  && rm -rf "/usr/local/src/curl-${CURL_VERSION}.tar.gz" "/usr/local/src/curl-${CURL_VERSION}"

echo "5 Rebuild stunnel"
STUNNEL_VERSION=5.55
cd /usr/local/src \
  && wget "https://www.stunnel.org/downloads/stunnel-${STUNNEL_VERSION}.tar.gz" -O "stunnel-${STUNNEL_VERSION}.tar.gz" \
  && tar -zxvf "stunnel-${STUNNEL_VERSION}.tar.gz" \
  && cd "stunnel-${STUNNEL_VERSION}" \
  && CPPFLAGS="-I/usr/local/ssl/include" LDFLAGS="-L/usr/local/ssl/lib -Wl,-rpath,/usr/local/ssl/lib" LD_LIBRARY_PATH=/usr/local/ssl/lib \
   ./configure --prefix=/usr/local/stunnel --with-ssl=/usr/local/ssl \
  && make \
  && make install \
  && ln -s /usr/local/stunnel/bin/stunnel /usr/bin/stunnel \
  && rm -rf "/usr/local/src/stunnel-${STUNNEL_VERSION}.tar.gz" "/usr/local/src/stunnel-${STUNNEL_VERSION}"

echo "Done!"
echo "Use this command to check GOST algoritms: openssl ciphers -V \"ALL:COMPLEMENTOFALL\""