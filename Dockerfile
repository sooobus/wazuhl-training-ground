FROM python:3.6
ADD . /wazuhl-polygon
WORKDIR /wazuhl-polygon
RUN pip install -r requirements.txt
#RUN svn co http://llvm.org/svn/llvm-project/test-suite/trunk train.out/llvm-test-suite

ENTRYPOINT ["python", "./train.py", "/clang/bin/clang"]
