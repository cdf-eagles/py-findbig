FROM alpine:3.24.2
ARG VERSION
ARG PKGDIR=dist
ARG APK_PUBKEY
COPY ${APK_PUBKEY} /etc/apk/keys/py-findbig.rsa.pub
COPY ${PKGDIR}/ /pkgs/
COPY packaging/test/check-installed.sh /check-installed.sh
RUN apk add --no-cache /pkgs/findbig_*_noarch.apk \
    && apk del findbig \
    && ! command -v findbig \
    && apk add --no-cache /pkgs/findbig_*_noarch.apk
USER nobody
RUN sh /check-installed.sh "${VERSION}" /usr/share/man/man1/findbig.1.gz
