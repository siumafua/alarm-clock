FROM alpine:3.10
#LABEL key="value"
ADD /env  /app/env
#ENTRYPOINT
#ENV key=value
#EXPOSE port
#HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD [ "executable" ]
#ONBUILD INSTRUCTION
RUN python3
COPY . /app
WORKDIR /app
CMD python3 alarm.py
