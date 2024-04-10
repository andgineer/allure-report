FROM amazoncorretto:11-alpine-jdk

ARG ALLURE_VERSION=2.27.0
ARG ALLURE_REPO=https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline
ARG ALLURE_HOME=/opt/allure-$ALLURE_VERSION/

ARG APP_HOME=/app

RUN apk update && \
    apk add --no-cache bash curl python3 && \
    rm -rf /var/cache/apk/* && \
    curl --insecure -L -o /tmp/allure.tgz \
         $ALLURE_REPO/$ALLURE_VERSION/allure-commandline-$ALLURE_VERSION.tgz && \
    mkdir -p $ALLURE_HOME && \
    tar -xzf /tmp/allure.tgz -C $(dirname $ALLURE_HOME) && \
    rm -rf /tmp/* && \
    chmod -R +x $ALLURE_HOME/bin &&\
    pip install Jinja2 && \
    mkdir -p $APP_HOME

ENV PATH=$PATH:$ALLURE_HOME/bin

VOLUME ["/allure-results"]
VOLUME ["/allure-report"]

COPY ./src/ /$APP_HOME/

WORKDIR $APP_HOME
ENTRYPOINT ["python allure_generate.py"]
