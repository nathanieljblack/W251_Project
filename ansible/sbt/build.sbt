name := "LogisticRegression"

version := "1.0"

mergeStrategy in assembly <<= (mergeStrategy in assembly) { (old) =>
   {
    case PathList("META-INF", xs @ _*) => MergeStrategy.discard
    case x => MergeStrategy.first
   }
}

libraryDependencies += "org.apache.spark" % "spark-core_2.10" % "1.0.2"

libraryDependencies += "org.apache.spark" % "spark-mllib_2.10" % "1.4.0"

libraryDependencies += "com.github.fommil.netlib" % "all" % "1.1.2"

resolvers += "Akka Repository" at "http://repo.akka.io/releases/"