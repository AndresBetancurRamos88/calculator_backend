FROM python:3.9-alpine AS base

ARG ENVIRONMENT

ENV PYROOT /pyroot
ENV PYTHONUSERBASE ${PYROOT}
ENV PATH=${PATH}:${PYROOT}/bin

RUN PIP_USER=1 pip install pipenv
COPY Pipfile* ./

RUN if [ "${ENVIRONMENT}" = "test" ]; \
        then PIP_USER=1 pipenv install --system --deploy --ignore-pipfile --dev; \
    else \
        PIP_USER=1 pipenv install --system --deploy --ignore-pipfile; \
    fi

FROM python:3.9-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFERED 1

ENV PYROOT /pyroot
ENV PYTHONUSERBASE ${PYROOT}
ENV PATH=${PATH}:${PYROOT}/bin

RUN addgroup -S myapp && adduser -S -G myapp user -u 1234
COPY --chown=myapp:user --from=base ${PYROOT}/ ${PYROOT}/

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY --chown=myapp:user ./ ./
USER 1234
