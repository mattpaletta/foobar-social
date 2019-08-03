FROM maven:3.6-jdk-11-slim
WORKDIR apilayer
ADD src src/
ADD pom.xml pom.xml
RUN mvn -q clean package
ENTRYPOINT ["java", "-cp", "target/apilayer-1.0-SNAPSHOT.jar", "com.foobar.social.ApiServer"]
