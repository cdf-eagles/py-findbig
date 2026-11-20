FROM almalinux:10.3
ARG VERSION
ARG PKGDIR=dist
ARG APK_PUBKEY
COPY ${PKGDIR}/ /pkgs/
COPY packaging/test/check-installed.sh /check-installed.sh
RUN dnf install -y --setopt=tsflags= /pkgs/findbig-*.noarch.rpm \
    && dnf remove -y findbig \
    && ! command -v findbig \
    && dnf install -y --setopt=tsflags= /pkgs/findbig-*.noarch.rpm \
    && dnf clean all
USER nobody
RUN sh /check-installed.sh "${VERSION}" /usr/share/man/man1/findbig.1.gz
