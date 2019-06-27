FROM maven:3.6-jdk-11-slim
WORKDIR apilayer
ADD src .
ADD pom.xml pom.xml
#RUN mvn compile && mvn package
#ENTRYPOINT ["mvn exec:java -Dexec.mainClass='com.foobar.social.ApiServer' -Dexec.classpathScope=runtime"]