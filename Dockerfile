FROM andgineer/allure:2.27.0

COPY src/allure_generate.py /

ENTRYPOINT ["python3", "allure_generate.py"]
