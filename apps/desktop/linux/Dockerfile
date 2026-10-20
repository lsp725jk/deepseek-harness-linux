# syntax=docker/dockerfile:1
FROM ubuntu:22.04

ARG NODE_VERSION=24.21.0
ARG PNPM_VERSION=11.28.5
ARG NODE_DIST_BASE=https://nodejs.org/dist

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates curl git python3 make g++ pkg-config \
      xz-utils tar unzip file xvfb xauth bubblewrap fakeroot dpkg-dev \
      libgtk-3-0 libnss3 libasound2 libgbm1 libxss1 libxtst6 \
      libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libcups2 libdrm2 \
      libatk1.0-0 libatk-bridge2.0-0 fonts-noto-cjk \
 && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL "${NODE_DIST_BASE}/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-x64.tar.xz" -o /tmp/node.tar.xz \
 && tar -xJf /tmp/node.tar.xz -C /usr/local --strip-components=1 \
 && rm /tmp/node.tar.xz \
 && (corepack enable || true) \
 && (corepack prepare pnpm@${PNPM_VERSION} --activate || npm install -g pnpm@${PNPM_VERSION})

# Electron's release archives are large; the mirror keeps container builds usable from China.
ENV ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/
ENV npm_config_registry=https://registry.npmmirror.com

WORKDIR /src
