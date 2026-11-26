# Extend the application image and take the released binary from the machine base.
ARG MACHINE_IMAGE=cmdop-machine:local
ARG FIXTURE_IMAGE=cmdop-report-fixture:local
FROM ${MACHINE_IMAGE} AS machine
FROM ${FIXTURE_IMAGE}
USER root
RUN install -d -o 10001 -g 10001 /opt/cmdop/bin
COPY --from=machine --chmod=0755 /opt/cmdop/bin/cmdop /opt/cmdop/bin/cmdop
RUN ln -s /opt/cmdop/bin/cmdop /usr/local/bin/cmdop
RUN useradd --uid 10001 --create-home --home-dir /home/cmdop cmdop
RUN python -m pip install --no-cache-dir "cmdop==3.6.0"
COPY read_via_sdk.py connect.py wait_online.py /opt/report/
USER cmdop
ENV HOME=/home/cmdop
ENTRYPOINT ["/usr/local/bin/cmdop"]
CMD ["run", "--no-sessions"]
