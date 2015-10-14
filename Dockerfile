FROM ubuntu:14.04
MAINTAINER Jonathan Lee <chencjlee@gmail.com>

RUN useradd -m -d /home/judge0 -p judge0 judge0 && chsh -s /bin/bash judge0
RUN useradd -m -d /home/judge1 -p judge1 judge1 && chsh -s /bin/bash judge1
RUN useradd -m -d /home/judge2 -p judge2 judge2 && chsh -s /bin/bash judge2
RUN useradd -m -d /home/judge3 -p judge3 judge3 && chsh -s /bin/bash judge3
RUN useradd -m -d /home/judge4 -p judge4 judge4 && chsh -s /bin/bash judge4
RUN useradd -m -d /home/judge5 -p judge5 judge5 && chsh -s /bin/bash judge5
RUN useradd -m -d /home/judge6 -p judge6 judge6 && chsh -s /bin/bash judge6
RUN useradd -m -d /home/judge7 -p judge7 judge7 && chsh -s /bin/bash judge7
RUN useradd -m -d /home/judge8 -p judge8 judge8 && chsh -s /bin/bash judge8
RUN useradd -m -d /home/judge9 -p judge9 judge9 && chsh -s /bin/bash judge9

RUN apt-get update
RUN apt-get install -y time
RUN apt-get install -y build-essential python openjdk-7-jdk
RUN apt-get install -y python-dev python-pip
RUN wget www.scala-lang.org/files/archive/scala-2.11.7.deb
RUN dpkg -i scala-2.11.7.deb

RUN pip install numpy
