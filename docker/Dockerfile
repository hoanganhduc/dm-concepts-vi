# Prebuilt build environment for the PDF release job (.github/workflows/build.yml
# -> release-pdf). Bakes the exact TeX Live subset, fonts, PreTeXt, and PreTeXt
# core resources that build-print.sh needs, so the release job pulls this image
# (~30s) instead of running ~165s of apt + pip + locale setup every release.
#
# Base is node:20 so GitHub's JavaScript actions (actions/checkout, etc.) run
# inside the `container:` job. Built & published by .github/workflows/build-image.yml
# to ghcr.io/hoanganhduc/dm-concepts-tex:latest. Rebuild only when this file or
# the PreTeXt version changes (deps here are otherwise stable).
FROM node:20-bookworm-slim

# Match the package set installed by the old release-pdf job verbatim, plus the
# CLI tools the build scripts call (poppler-utils -> pdftoppm/pdfinfo,
# ghostscript, git, gh). fonts-texgyre registers "TeX Gyre Termes"/"Cursor" with
# fontconfig so the XeLaTeX cover renders its text (fontspec loads fonts by name).
RUN apt-get update && apt-get install -y --no-install-recommends \
      texlive-xetex texlive-latex-recommended texlive-latex-extra \
      texlive-pictures texlive-fonts-recommended texlive-fonts-extra \
      texlive-lang-other latexmk fonts-texgyre \
      python3 python3-pip \
      poppler-utils ghostscript \
      git curl ca-certificates gnupg fontconfig \
    && fc-cache -f \
    && rm -rf /var/lib/apt/lists/*

# GitHub CLI (gh pr list / gh release create in the job).
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
      > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update && apt-get install -y --no-install-recommends gh \
    && rm -rf /var/lib/apt/lists/*

# PreTeXt pinned to the repo's version so the baked core resources below match
# what the job builds with. Debian's pip is externally managed -> break-system.
RUN pip3 install --no-cache-dir --break-system-packages pretext==2.42.0 pyyaml

# Pre-fetch PreTeXt core resources (the ~/.ptx download that install-vi-locale.sh
# otherwise triggers via a ~33s throwaway build). A minimal seed project forces
# the download; stash it at /opt/ptx-cache because GitHub overrides $HOME to
# /github/home for container jobs, so /root/.ptx is not visible at runtime — the
# job copies /opt/ptx-cache into $HOME/.ptx instead. Best-effort: if this fails,
# the runtime locale step falls back to its own fetch (slower, still correct).
RUN pretext new hello -d /tmp/ptx-seed >/dev/null 2>&1 || true; \
    ( cd /tmp/ptx-seed && pretext build web >/dev/null 2>&1 ) || true; \
    mkdir -p /opt/ptx-cache; \
    if [ -d /root/.ptx ]; then cp -a /root/.ptx/. /opt/ptx-cache/; fi; \
    rm -rf /tmp/ptx-seed

LABEL org.opencontainers.image.source="https://github.com/hoanganhduc/dm-concepts-vi" \
      org.opencontainers.image.description="TeX Live + PreTeXt build env for the DM-Concepts PDF release job"
