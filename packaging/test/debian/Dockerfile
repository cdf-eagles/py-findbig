FROM debian:13
ARG VERSION
ARG PKGDIR=dist
ARG APK_PUBKEY
COPY ${PKGDIR}/ /pkgs/
COPY packaging/test/check-installed.sh /check-installed.sh
RUN rm -f /etc/dpkg/dpkg.cfg.d/docker* /etc/dpkg/dpkg.cfg.d/excludes \
    && apt-get update \
    && apt-get install -y --no-install-recommends /pkgs/findbig_*_all.deb \
    && sh /check-installed.sh "${VERSION}" /usr/share/man/man1/findbig.1.gz \
    && apt-get remove -y findbig \
    && ! command -v findbig
