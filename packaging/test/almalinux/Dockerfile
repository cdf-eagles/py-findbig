FROM almalinux:10.2
ARG VERSION
ARG PKGDIR=dist
ARG APK_PUBKEY
COPY ${PKGDIR}/ /pkgs/
COPY packaging/test/check-installed.sh /check-installed.sh
RUN dnf install -y --setopt=tsflags= /pkgs/findbig-*.noarch.rpm \
    && sh /check-installed.sh "${VERSION}" /usr/share/man/man1/findbig.1.gz \
    && dnf remove -y findbig \
    && ! command -v findbig
