FROM python:3.11.1-alpine3.17

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

ARG DEV=${DEV}
ARG APP_PORT=${APP_PORT}

RUN addgroup -S appgroup && \
    adduser -S app-user -G appgroup

WORKDIR /home/app-user/int-project

COPY ./dockerfiles/fastapi/requirements/ ./requirements/

RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    if [ $DEV = True ]; \
    then \
    /venv/bin/pip install -r ./requirements/requirements.dev.txt ; \
    else \
    /venv/bin/pip install -r ./requirements/requirements.txt ; \
    fi && \
    rm -rf ./requirements/ && \
    mkdir /.ssh && \
    apk add --update --no-cache --virtual .tmp-keygen-deps openssh-keygen openssl && \
    ssh-keygen -f "/.ssh/id_rsa" -t rsa -b 4096 -m pem -P '' && \
    openssl rsa -in "/.ssh/id_rsa" -out \
    "/.ssh/id_rsa.pub.jwk" -pubout -outform PEM && \
    apk del .tmp-keygen-deps && \
    rm /.ssh/id_rsa.pub && \
    chown -R app-user:appgroup /home/app-user/int-project/

COPY . .
RUN rm -rf ./dockerfiles/ && \
    if [ $DEV != True ]; then rm -rf tests; fi

EXPOSE $APP_PORT
