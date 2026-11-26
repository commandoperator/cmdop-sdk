# syntax=docker/dockerfile:1.7
FROM debian:bookworm-slim@sha256:e67eeead736ff7bbe258ef088bff683635c561b1fcfefad0806c1df4ab49ce0e AS base
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --uid 10001 --create-home --home-dir /home/cmdop cmdop

FROM base AS machine
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
# A changed stable installer invalidates the binary installation layer.
ADD https://install.cmdop.ai/ /tmp/install-cmdop.sh
RUN CMDOP_INSTALL_DIR=/usr/local/bin sh /tmp/install-cmdop.sh

FROM base
RUN install -d -o 10001 -g 10001 /opt/cmdop/bin
COPY --from=machine --chmod=0755 /usr/local/bin/cmdop /opt/cmdop/bin/cmdop
RUN ln -s /opt/cmdop/bin/cmdop /usr/local/bin/cmdop
USER cmdop
ENV HOME=/home/cmdop
WORKDIR /home/cmdop
ENTRYPOINT ["/usr/local/bin/cmdop"]
CMD ["run", "--no-sessions"]
