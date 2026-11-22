FROM almalinux:9.7
ARG VERSION
ARG PKGDIR=dist
ARG APK_PUBKEY
ARG RPM_PUBKEY
COPY ${PKGDIR}/ /pkgs/
COPY ${RPM_PUBKEY} /tmp/rpm-signing.pub.asc
COPY packaging/test/check-installed.sh /check-installed.sh
# rpm --checksig exits 0 for an unsigned package too, so the test matches
# its "digests signatures OK" line.
RUN rpm --import /tmp/rpm-signing.pub.asc \
    && rpm --checksig /pkgs/findbig-*.noarch.rpm | tee /tmp/checksig \
    && grep -q ': digests signatures OK$' /tmp/checksig \
    && dnf install -y --setopt=tsflags= /pkgs/findbig-*.noarch.rpm \
    && dnf remove -y findbig \
    && ! command -v findbig \
    && dnf install -y --setopt=tsflags= /pkgs/findbig-*.noarch.rpm \
    && dnf clean all
USER nobody
RUN sh /check-installed.sh "${VERSION}" /usr/share/man/man1/findbig.1.gz
