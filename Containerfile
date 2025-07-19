FROM docker.io/debian:trixie

# Install systemd, ansible and other dependencies
RUN apt-get update && apt-get install -y \
    systemd \
    systemd-sysv \
    ansible \
    python3 \
    python3-pip \
    sudo \
    procps \
    iproute2 \
    curl \
    vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configure autologin for root on console and shutdown on exit
RUN mkdir -p /etc/systemd/system/console-getty.service.d && \
    echo '[Service]' > /etc/systemd/system/console-getty.service.d/autologin.conf && \
    echo 'ExecStart=' >> /etc/systemd/system/console-getty.service.d/autologin.conf && \
    echo 'ExecStart=-/sbin/agetty --autologin root --noclear --keep-baud console 115200,38400,9600 $TERM' >> /etc/systemd/system/console-getty.service.d/autologin.conf && \
    echo 'ExecStopPost=/bin/systemctl poweroff' >> /etc/systemd/system/console-getty.service.d/autologin.conf && \
    systemctl set-default multi-user.target
