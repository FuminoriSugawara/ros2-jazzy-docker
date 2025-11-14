# ROS 2 Jazzy development environment on Ubuntu 24.04
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_BREAK_SYSTEM_PACKAGES=1 \
    ROS_DISTRO=jazzy

# Use bash for RUN commands so we can source setup files easily later.
SHELL ["/bin/bash", "-c"]

# Locale configuration and base tooling required for the ROS 2 apt repository.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      locales \
      curl \
      ca-certificates \
      gnupg \
      lsb-release && \
    locale-gen en_US en_US.UTF-8 && \
    update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 && \
    rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8

# Add the official ROS 2 GPG key and apt repository.
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | \
      gpg --dearmor -o /etc/apt/keyrings/ros-archive-keyring.gpg && \
    chmod a+r /etc/apt/keyrings/ros-archive-keyring.gpg && \
    tee /etc/apt/sources.list.d/ros2.list >/dev/null <<EOF
deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/ros-archive-keyring.gpg] \
http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") main
EOF

# Install ROS 2 Jazzy desktop and common developer tooling.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ros-${ROS_DISTRO}-desktop \
      ros-dev-tools \
      python3 \
      python3-venv \
      python3-pip \
      build-essential \
      git \
      python3-colcon-common-extensions && \
    rm -rf /var/lib/apt/lists/*

# Source ROS 2 on login shells.
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> /etc/bash.bashrc

# Default to an interactive shell so users can start working right away.
CMD ["bash"]
